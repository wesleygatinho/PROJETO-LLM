"""
07_avaliar_classificador.py — Etapa 3: avalia um adaptador treinado pelo 06_treinar_qlora.py.

O que este script faz, em ordem:
  1. Lê a receita da rodada (rodada.json): modelo base, max_tokens e melhor época.
  2. Carrega a variante pedida:
       nf4  = base em 4 bits NF4 + adaptador (o modelo exatamente como foi treinado);
       bf16 = base em 16 bits com o adaptador MESCLADO (o "modelo especializado" de referência,
              ponto de partida das variantes quantizadas da RQ2).
  3. Dá uma nota a cada função da VALIDAÇÃO, do TESTE e do TESTE PAREADO.
  4. No teste: F1, precisão, revocação, FPR e acurácia no limiar padrão (nota > 0), AUC e VD-S.
     VD-S = taxa de vulneráveis perdidas no teste, com o limiar escolhido na VALIDAÇÃO para dar
     no máximo 0,5% de alarmes falsos (protocolo §6: o limiar nunca é escolhido no teste).
     Também grava o "VD-S oráculo" (limiar escolhido no próprio teste), só para comparar com o artigo do PrimeVul.
     No pareado: P-C, P-V, P-B, P-R (nota > 0) e a % de pares em que a vulnerável recebeu nota maior.
  5. Grava uma linha em ../resultados/resultados_etapa3.csv e as notas de cada função em ../logs/.

Tempo e memória aqui são indicativos (transformers, em lotes). O custo oficial da curva custo × qualidade
será medido na etapa de quantização, com o vLLM (protocolo §1, item 4).

Uso:
  python 07_avaliar_classificador.py --rodada ../adapters/NOME --limite 200               # depuração
  python 07_avaliar_classificador.py --rodada ../adapters/NOME --variante nf4 --preco_hora 0.50
  python 07_avaliar_classificador.py --rodada hf:SEU_USUARIO/etapa3-adaptadores/NOME --variante bf16 --preco_hora 0.50
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from peft import PeftModel

from ambiente import conferir, descrever_ambiente, versao
from classificador import (auc_segura, carregar_base, carregar_jsonl, carregar_tokenizer, escolher_amostra,
                           fixar_seed, formar_pares, gravar_linha_csv, impressao_digital, limiar_para_fpr,
                           metricas_classificacao, metricas_pareadas, pontuar, taxas_no_limiar, tokenizar)


def localizar_rodada(rodada):
    """Pasta local da rodada. 'hf:usuario/repositorio/NOME' baixa só essa rodada do Hugging Face."""
    if not rodada.startswith("hf:"):
        return Path(rodada)
    usuario, repositorio, nome = rodada[3:].split("/", 2)
    from huggingface_hub import snapshot_download
    raiz = snapshot_download(repo_id=f"{usuario}/{repositorio}", allow_patterns=[f"{nome}/*"])
    return Path(raiz) / nome


def gravar_log(arquivo, amostra, notas, cortadas, seqs):
    """Uma linha por função, na ordem do arquivo de dados. Tem 'pos' e 'pred' (nota > 0), então
    serve também para o 04_metricas_pareadas.py e o 05_comparar_logs.py."""
    with arquivo.open("w", encoding="utf-8") as f:
        for j in sorted(range(len(amostra)), key=lambda j: amostra[j]["_pos"]):
            d = amostra[j]
            f.write(json.dumps({
                "pos": d["_pos"], "idx": d.get("idx"), "project": d.get("project"),
                "commit_id": d.get("commit_id"), "func_hash": d.get("func_hash"),
                "target": int(d["target"]), "nota": round(float(notas[j]), 5), "pred": int(notas[j] > 0),
                "truncada": bool(cortadas[j]), "n_tokens": int(len(seqs[j])),
            }, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Etapa 3 — avaliação do classificador (QLoRA + cabeça).")
    ap.add_argument("--rodada", required=True, help="pasta da rodada (../adapters/NOME) ou hf:usuario/repositorio/NOME")
    ap.add_argument("--epoca", type=int, default=0, help="0 = melhor época pela AUC na validação (escolhida no treino)")
    ap.add_argument("--variante", choices=["nf4", "bf16"], default="nf4")
    ap.add_argument("--validacao", default="../dados/primevul_valid.jsonl")
    ap.add_argument("--teste", default="../dados/primevul_test.jsonl")
    ap.add_argument("--pareado", default="../dados/primevul_test_paired.jsonl")
    ap.add_argument("--tokens_por_lote", type=int, default=32768, help="só memória/velocidade: tokens por lote")
    ap.add_argument("--limite", type=int, default=0, help="depuração: só N funções de cada arquivo")
    ap.add_argument("--preco_hora", type=float, default=0.0, help="preço por hora do pod em US$")
    ap.add_argument("--observacoes", default="", help="texto livre para a planilha")
    args = ap.parse_args()

    fixar_seed(0)
    pasta = localizar_rodada(args.rodada)
    if not (pasta / "rodada.json").exists():
        raise SystemExit(f"[ERRO] Não achei {pasta / 'rodada.json'}.")
    registro = json.loads((pasta / "rodada.json").read_text(encoding="utf-8"))
    epoca = args.epoca or registro["melhor_epoca"]
    pasta_epoca = pasta / f"epoca_{epoca}"
    if not pasta_epoca.exists():
        raise SystemExit(f"[ERRO] Não achei {pasta_epoca}.")
    modelo, max_tokens = registro["modelo"], registro["args"]["max_tokens"]
    depuracao = args.limite > 0 or registro.get("depuracao", False)
    print(f"Rodada: {registro['nome']}  |  época {epoca}  |  variante {args.variante}  |  max_tokens {max_tokens}")

    # ---- 1) Dados -----------------------------------------------------------
    conjuntos = {}
    for nome_c, caminho in (("validacao", args.validacao), ("teste", args.teste), ("pareado", args.pareado)):
        caminho = Path(caminho)
        if not caminho.exists():
            raise SystemExit(f"[ERRO] Não achei {caminho}. Rode python 00_baixar_primevul.py")
        itens = carregar_jsonl(caminho)
        if nome_c == "pareado":  # os pares vêm em linhas consecutivas: o limite pega as primeiras linhas
            for pos, d in enumerate(itens):
                d["_pos"] = pos
            amostra = itens[: args.limite] if args.limite else itens
        else:
            amostra = escolher_amostra(itens, args.limite or len(itens), balanceado=args.limite > 0, seed=0)
        conjuntos[nome_c] = {"caminho": caminho, "itens": itens, "amostra": amostra}
        print(f"  {nome_c}: {len(amostra)} funções")

    # ---- 2) Ambiente e modelo -----------------------------------------------
    gpu = torch.cuda.get_device_name(0)
    ambiente_confere = conferir(gpu)
    tokenizer = carregar_tokenizer(modelo)
    pad_id = tokenizer.pad_token_id
    print(f"Carregando {modelo} ({'4 bits NF4' if args.variante == 'nf4' else '16 bits'}) + adaptador {pasta_epoca.name}")
    base = carregar_base(modelo, args.variante, pad_id)
    modelo_revisao = (getattr(base.config, "_commit_hash", None) or "")[:12]
    if registro.get("modelo_revisao") and modelo_revisao != registro["modelo_revisao"]:
        print(f"[ATENÇÃO] Revisão do modelo base mudou: treino {registro['modelo_revisao']}, agora {modelo_revisao}.")
    model = PeftModel.from_pretrained(base, str(pasta_epoca))
    if args.variante == "bf16":
        model = model.merge_and_unload()  # adaptador somado aos pesos: um modelo só, sem camadas extras
    model.eval()
    torch.cuda.reset_peak_memory_stats()
    memoria_modelo_gb = torch.cuda.memory_allocated() / 1e9

    # ---- 3) Notas -----------------------------------------------------------
    pasta_logs = Path("../logs")
    pasta_logs.mkdir(parents=True, exist_ok=True)
    nome_aval = f"etapa3_aval_{args.variante}_{datetime.now():%Y%m%d_%H%M%S}"
    inicio_total = time.time()
    for nome_c, c in conjuntos.items():
        seqs, cortadas = tokenizar(tokenizer, c["amostra"], max_tokens)
        t0 = time.time()
        c["notas"] = pontuar(model, seqs, pad_id, args.tokens_por_lote, desc=f"Pontuando {nome_c}")
        c["tempo_s"] = time.time() - t0
        c["alvos"] = np.array([int(d["target"]) for d in c["amostra"]], dtype=np.int64)
        c["cortadas"] = int(sum(cortadas))
        c["log"] = pasta_logs / f"{nome_aval}_{nome_c}.jsonl"
        gravar_log(c["log"], c["amostra"], c["notas"], cortadas, seqs)
    tempo_total = time.time() - inicio_total
    memoria_pico_gb = torch.cuda.max_memory_allocated() / 1e9

    # ---- 4) Métricas --------------------------------------------------------
    val, teste, par = conjuntos["validacao"], conjuntos["teste"], conjuntos["pareado"]
    m = metricas_classificacao(teste["notas"], teste["alvos"])
    auc_val = auc_segura(val["alvos"], val["notas"])
    limiar_vds = limiar_para_fpr(val["notas"], val["alvos"])
    vds, fpr_no_limiar = taxas_no_limiar(teste["notas"], teste["alvos"], limiar_vds)
    vds_oraculo, _ = taxas_no_limiar(teste["notas"], teste["alvos"], limiar_para_fpr(teste["notas"], teste["alvos"]))
    pares, metodo_pares = formar_pares(par["itens"])
    p = metricas_pareadas({d["_pos"]: float(n) for d, n in zip(par["amostra"], par["notas"])}, pares)
    pct = lambda k: 100.0 * k / p["avaliados"] if p["avaliados"] else 0.0
    tempo_por_funcao = teste["tempo_s"] / len(teste["amostra"])
    custo_teste = args.preco_hora * teste["tempo_s"] / 3600.0
    custo_total = args.preco_hora * tempo_total / 3600.0

    # ---- 5) Planilha --------------------------------------------------------
    ambiente = descrever_ambiente()
    linha = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rodada": registro["nome"], "modelo": modelo, "epoca": epoca, "variante": args.variante,
        "seed": registro["args"]["seed"], "benignas_por_vul": registro["args"]["benignas_por_vul"],
        "max_tokens": max_tokens, "n_teste": len(teste["amostra"]),
        "f1": round(m["f1"], 4), "precisao": round(m["precisao"], 4), "revocacao": round(m["revocacao"], 4),
        "fpr": round(m["fpr"], 4), "acuracia": round(m["acuracia"], 4), "auc": round(m["auc"], 4),
        "tp": m["tp"], "fp": m["fp"], "fn": m["fn"], "tn": m["tn"],
        "vds": round(vds, 4), "fpr_teste_no_limiar_vds": round(fpr_no_limiar, 4), "limiar_vds": round(limiar_vds, 5),
        "vds_oraculo_teste": round(vds_oraculo, 4), "auc_validacao": round(auc_val, 4),
        "cortadas_teste": teste["cortadas"],
        "pares_avaliados": p["avaliados"], "metodo_pareamento": metodo_pares,
        "P_C": p["P_C"], "P_V": p["P_V"], "P_B": p["P_B"], "P_R": p["P_R"],
        "P_C_pct": round(pct(p["P_C"]), 2), "pares_ordenados_pct": round(pct(p["ordenados"]), 2),
        "memoria_modelo_gb": round(memoria_modelo_gb, 2), "memoria_pico_gb": round(memoria_pico_gb, 2),
        "tempo_por_funcao_s": round(tempo_por_funcao, 4), "tokens_por_lote": args.tokens_por_lote,
        "tempo_total_s": round(tempo_total, 1), "gpu": gpu, "preco_hora_usd": args.preco_hora,
        "custo_teste_usd": round(custo_teste, 4), "custo_total_usd": round(custo_total, 4),
        "motor": "transformers",
        "log_prefixo": nome_aval,
        "depuracao": "sim" if depuracao else "nao",
        "observacoes": args.observacoes,
        "ambiente_confere": ambiente_confere,
        "torch": ambiente["torch"], "cuda": ambiente["cuda"], "transformers": ambiente["transformers"],
        "tokenizers": ambiente["tokenizers"], "peft": versao("peft") or "", "bitsandbytes": versao("bitsandbytes") or "",
        "modelo_revisao": modelo_revisao, "dados_sha256_teste": impressao_digital(teste["caminho"]),
    }
    arquivo_csv = Path("../resultados/resultados_etapa3.csv")
    arquivo_csv.parent.mkdir(parents=True, exist_ok=True)
    gravar_linha_csv(arquivo_csv, linha)

    # ---- 6) Resumo na tela --------------------------------------------------
    auc_treino = next((e["auc_validacao"] for e in registro["epocas"] if e["epoca"] == epoca), None)
    print("\n================ RESULTADO (TESTE) ================")
    print(f"F1={m['f1']:.3f}  precisão={m['precisao']:.3f}  revocação={m['revocacao']:.3f}  "
          f"FPR={m['fpr']:.3f}  acurácia={m['acuracia']:.3f}  AUC={m['auc']:.3f}")
    print(f"TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']}  |  cortadas={teste['cortadas']}")
    print(f"VD-S={vds:.3f} (limiar da validação; FPR no teste={fpr_no_limiar:.4f})  |  VD-S oráculo={vds_oraculo:.3f}")
    print(f"Pareado ({p['avaliados']} pares): P-C={pct(p['P_C']):.1f}%  P-V={pct(p['P_V']):.1f}%  "
          f"P-B={pct(p['P_B']):.1f}%  P-R={pct(p['P_R']):.1f}%  |  vulnerável com nota maior: {pct(p['ordenados']):.1f}% (acaso 50%)")
    print(f"AUC na validação inteira={auc_val:.3f}  (no treino, na amostra de checagem: {auc_treino}; "
          f"se esta ficar perto de 0,5 e a do treino não, o adaptador não carregou direito)")
    print(f"Memória: modelo={memoria_modelo_gb:.2f} GB, pico={memoria_pico_gb:.2f} GB  |  "
          f"tempo/função no teste={tempo_por_funcao:.4f}s  |  total={tempo_total / 60:.1f} min  |  custo US$ {custo_total:.2f}")
    print(f"Linha gravada em: {arquivo_csv}")
    print(f"Notas por função em: {pasta_logs}/{nome_aval}_{{validacao,teste,pareado}}.jsonl")
    if depuracao:
        print("[DEPURAÇÃO] Amostra pequena ou rodada de depuração: os números servem só para conferir o fluxo.")
    if args.preco_hora == 0:
        print("[ATENÇÃO] --preco_hora não informado: o custo saiu zerado.")
    if ambiente_confere != "sim":
        print(f"[ATENÇÃO] Ambiente fora da trava (ambiente_confere={ambiente_confere}): esta linha serve só como teste.")


if __name__ == "__main__":
    main()
