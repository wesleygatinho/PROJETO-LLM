"""
08_baseline_tamanho.py — o baseline burro: "quanto maior a função, mais suspeita".

Por que existe: no PrimeVul-test as funções vulneráveis são muito mais longas que as benignas
(922 contra 297 tokens, em média). Um "detector" que só mede o tamanho da função chega a AUC 0,82
sem entender nada de segurança. Toda tabela da dissertação precisa desta linha embaixo: um modelo
de 7B só vale o custo se ganhar DISTO. No pareado ele desmorona (a versão corrigida costuma ser a
maior, porque o conserto acrescenta código), e é justamente essa a graça da avaliação pareada.

Não usa GPU nem modelo treinado. A medida padrão é o nº de tokens, o mesmo que o modelo enxerga
(cortado em --max_tokens); `--medida linhas` ou `--medida caracteres` nem precisa do tokenizer.

Mesmo protocolo dos outros scripts: tudo o que é escolha sai da VALIDAÇÃO, nunca do teste.
  - limiar de decisão: o que dá a maior F1 na validação (o modelo usa nota > 0; aqui não existe "0",
    por isso o limiar precisa ser escolhido — e é escolhido fora do teste);
  - VD-S: limiar da validação para FPR <= 0,5%, aplicado ao teste;
  - pareado: P-C/P-V/P-B/P-R no limiar de decisão e a % de pares ordenados (não depende de limiar).

Uso:
  python 08_baseline_tamanho.py
  python 08_baseline_tamanho.py --medida linhas
  python 08_baseline_tamanho.py --medida tokens --max_tokens 0     # 0 = sem corte
"""

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np

from ambiente import descrever_ambiente
from classificador import (auc_segura, carregar_jsonl, carregar_tokenizer, escolher_amostra, formar_pares,
                           gravar_linha_csv, gravar_log_notas, impressao_digital, limiar_para_fpr,
                           metricas_pareadas, taxas_no_limiar, tokenizar)


def medir(itens, medida, tokenizer, max_tokens):
    """Tamanho de cada função, na medida escolhida. É essa a 'nota' do baseline."""
    if medida == "linhas":
        return np.array([d["func"].count("\n") + 1 for d in itens], dtype=np.float64)
    if medida == "caracteres":
        return np.array([len(d["func"]) for d in itens], dtype=np.float64)
    seqs, _ = tokenizar(tokenizer, itens, max_tokens or 10**9)
    return np.array([len(s) for s in seqs], dtype=np.float64)


def limiar_melhor_f1(notas, alvos):
    """Limiar que dá a maior F1 NESTAS funções (usado só na validação).
    Testa cada valor distinto como corte, com a regra 'nota > limiar'."""
    ordem = np.argsort(-notas)
    y = alvos[ordem]
    tp = np.cumsum(y == 1)
    fp = np.cumsum(y == 0)
    total_vul = max(1, int((alvos == 1).sum()))
    f1 = 2 * tp / np.maximum(1, tp + fp + total_vul)
    # o corte fica ENTRE a função k e a seguinte: só vale onde o valor muda
    valido = np.ones(len(y), dtype=bool)
    valido[:-1] = notas[ordem][:-1] != notas[ordem][1:]
    f1 = np.where(valido, f1, -1)
    k = int(np.argmax(f1))
    return float(np.nextafter(notas[ordem][k], -np.inf)), float(f1[k])


def main():
    ap = argparse.ArgumentParser(description="Baseline trivial: o tamanho da função como detector.")
    ap.add_argument("--medida", choices=["tokens", "linhas", "caracteres"], default="tokens")
    ap.add_argument("--modelo", default="Qwen/Qwen2.5-Coder-3B", help="só para contar tokens do mesmo jeito que o modelo")
    ap.add_argument("--max_tokens", type=int, default=2048, help="corta como no treino/avaliação; 0 = sem corte")
    ap.add_argument("--validacao", default="../dados/primevul_valid.jsonl")
    ap.add_argument("--teste", default="../dados/primevul_test.jsonl")
    ap.add_argument("--pareado", default="../dados/primevul_test_paired.jsonl")
    ap.add_argument("--limite", type=int, default=0, help="depuração: só N funções de cada arquivo")
    ap.add_argument("--observacoes", default="", help="texto livre para a planilha")
    args = ap.parse_args()

    # ---- 1) Dados -----------------------------------------------------------
    conjuntos = {}
    for nome_c, caminho in (("validacao", args.validacao), ("teste", args.teste), ("pareado", args.pareado)):
        caminho = Path(caminho)
        if not caminho.exists():
            raise SystemExit(f"[ERRO] Não achei {caminho}. Rode python 00_baixar_primevul.py")
        itens = carregar_jsonl(caminho)
        if nome_c == "pareado":  # os pares vêm em linhas consecutivas
            for pos, d in enumerate(itens):
                d["_pos"] = pos
            amostra = itens[: args.limite] if args.limite else itens
        else:
            amostra = escolher_amostra(itens, args.limite or len(itens), balanceado=args.limite > 0, seed=0)
        conjuntos[nome_c] = {"caminho": caminho, "itens": itens, "amostra": amostra}

    # ---- 2) Medir o tamanho -------------------------------------------------
    tokenizer = carregar_tokenizer(args.modelo) if args.medida == "tokens" else None
    for nome_c, c in conjuntos.items():
        c["notas"] = medir(c["amostra"], args.medida, tokenizer, args.max_tokens)
        c["alvos"] = np.array([int(d["target"]) for d in c["amostra"]], dtype=np.int64)
        print(f"  {nome_c}: {len(c['amostra'])} funções  |  {args.medida} (mediana): "
              f"benignas {np.median(c['notas'][c['alvos'] == 0]):.0f}, vulneráveis {np.median(c['notas'][c['alvos'] == 1]):.0f}")
    val, teste, par = conjuntos["validacao"], conjuntos["teste"], conjuntos["pareado"]

    # ---- 3) Métricas (tudo calibrado na validação) --------------------------
    limiar, f1_val = limiar_melhor_f1(val["notas"], val["alvos"])
    previsto = teste["notas"] > limiar
    vul = teste["alvos"] == 1
    tp, fp = int((previsto & vul).sum()), int((previsto & ~vul).sum())
    fn, tn = int((~previsto & vul).sum()), int((~previsto & ~vul).sum())
    precisao = tp / max(1, tp + fp)
    revocacao = tp / max(1, tp + fn)
    f1 = 2 * precisao * revocacao / max(1e-12, precisao + revocacao)
    limiar_vds = limiar_para_fpr(val["notas"], val["alvos"])
    vds, fpr_no_limiar = taxas_no_limiar(teste["notas"], teste["alvos"], limiar_vds)
    vds_oraculo, _ = taxas_no_limiar(teste["notas"], teste["alvos"], limiar_para_fpr(teste["notas"], teste["alvos"]))
    pares, metodo_pares = formar_pares(par["itens"])
    p = metricas_pareadas({d["_pos"]: float(n) for d, n in zip(par["amostra"], par["notas"])}, pares)
    pct = lambda k: 100.0 * k / p["avaliados"] if p["avaliados"] else 0.0

    # ---- 4) Logs e planilha -------------------------------------------------
    pasta_logs = Path("../logs")
    pasta_logs.mkdir(parents=True, exist_ok=True)
    nome = f"baseline_tamanho_{args.medida}_{datetime.now():%Y%m%d_%H%M%S}"
    for nome_c in ("teste", "pareado"):
        gravar_log_notas(pasta_logs / f"{nome}_{nome_c}.jsonl", conjuntos[nome_c]["amostra"],
                         conjuntos[nome_c]["notas"], limiar=limiar)

    ambiente = descrever_ambiente()
    linha = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rodada": nome, "modelo": f"(nenhum: {args.medida} da função)", "epoca": "", "variante": "baseline_tamanho",
        "seed": "", "benignas_por_vul": "", "max_tokens": args.max_tokens, "n_teste": len(teste["amostra"]),
        "f1": round(f1, 4), "precisao": round(precisao, 4), "revocacao": round(revocacao, 4),
        "fpr": round(fp / max(1, fp + tn), 4), "acuracia": round((tp + tn) / max(1, len(teste["alvos"])), 4),
        "auc": round(auc_segura(teste["alvos"], teste["notas"]), 4),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "vds": round(vds, 4), "fpr_teste_no_limiar_vds": round(fpr_no_limiar, 4), "limiar_vds": round(limiar_vds, 5),
        "vds_oraculo_teste": round(vds_oraculo, 4),
        "auc_validacao": round(auc_segura(val["alvos"], val["notas"]), 4),
        "pares_avaliados": p["avaliados"], "metodo_pareamento": metodo_pares,
        "P_C": p["P_C"], "P_V": p["P_V"], "P_B": p["P_B"], "P_R": p["P_R"],
        "P_C_pct": round(pct(p["P_C"]), 2), "pares_ordenados_pct": round(pct(p["ordenados"]), 2),
        "limiar_decisao": round(limiar, 2), "f1_validacao_no_limiar": round(f1_val, 4),
        "gpu": "", "motor": "nenhum", "log_prefixo": nome,
        "depuracao": "sim" if args.limite else "nao",
        "observacoes": args.observacoes,
        "ambiente_confere": "nao se aplica",
        "tokenizers": ambiente["tokenizers"], "transformers": ambiente["transformers"],
        "dados_sha256_teste": impressao_digital(teste["caminho"]),
    }
    arquivo_csv = Path("../resultados/resultados_etapa3.csv")
    arquivo_csv.parent.mkdir(parents=True, exist_ok=True)
    gravar_linha_csv(arquivo_csv, linha)

    # ---- 5) Resumo na tela --------------------------------------------------
    margem = 100 * 1.96 * 0.5 / np.sqrt(max(1, p["avaliados"]))
    print(f"\n============ BASELINE: {args.medida} da função ============")
    print(f"Limiar escolhido na validação: {limiar:.1f} {args.medida} (F1 lá: {f1_val:.3f})")
    print(f"TESTE: F1={f1:.3f}  precisão={precisao:.3f}  revocação={revocacao:.3f}  "
          f"FPR={fp / max(1, fp + tn):.3f}  AUC={linha['auc']:.3f}")
    print(f"VD-S={vds:.3f} (limiar da validação; FPR no teste={fpr_no_limiar:.4f})  |  VD-S oráculo={vds_oraculo:.3f}")
    print(f"Pareado ({p['avaliados']} pares): P-C={pct(p['P_C']):.1f}%  |  vulnerável com nota maior: "
          f"{pct(p['ordenados']):.1f}% (acaso 50% ± {margem:.1f})")
    print(f"\nLeitura: compare a AUC com a do modelo treinado. Se o modelo não passar DISTO, ele está "
          f"aprendendo tamanho, não vulnerabilidade — e o pareado mostra que tamanho não serve.")
    print(f"Linha gravada em: {arquivo_csv}  |  logs: {pasta_logs}/{nome}_*.jsonl")


if __name__ == "__main__":
    main()
