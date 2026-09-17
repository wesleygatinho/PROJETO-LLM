"""
06_treinar_qlora.py — Etapa 3: especializa um modelo de código por QLoRA com cabeça de classificação.

O que este script faz, em ordem:
  1. Monta o treino a partir do PrimeVul-train: TODAS as funções vulneráveis + as benignas na proporção
     escolhida em --benignas_por_vul ("real" = todas, ~35 por vulnerável; ou um número k).
  2. Carrega o modelo BASE (não o Instruct, protocolo §2) em 4 bits NF4, com uma cabeça de 2 saídas.
  3. Congela o modelo e treina só os adaptadores LoRA e a cabeça.
  4. No fim de cada época: salva o adaptador e mede a AUC numa amostra FIXA da VALIDAÇÃO
     (o teste não é tocado aqui). A época com maior AUC vira a "melhor época".
  5. Grava uma linha em ../resultados/treinos_etapa3.csv, a receita completa e a perda passo a passo
     em ../logs/ e, com --repo_hf, envia o adaptador para um repositório PRIVADO do Hugging Face
     (o pod é apagado no fim da sessão; sem isso o adaptador se perde).

Uso (primeira rodada = depuração, poucos minutos):
  python 06_treinar_qlora.py --benignas_por_vul 1 --limite_treino 400 --preco_hora 0.50

Rodada de verdade (exemplo):
  python 06_treinar_qlora.py --modelo Qwen/Qwen2.5-Coder-7B --benignas_por_vul real --epocas 1 --seed 1 \
      --preco_hora 0.50 --repo_hf SEU_USUARIO/etapa3-adaptadores

Depois: python 07_avaliar_classificador.py --rodada ../adapters/NOME_DA_RODADA
"""

import argparse
import json
import math
import random
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from tqdm import tqdm

from ambiente import conferir, descrever_ambiente, versao
from classificador import (CAMADAS_LORA, auc_segura, carregar_base, carregar_jsonl, carregar_tokenizer,
                           dividir_por_tokens, fixar_seed, gravar_linha_csv, impressao_digital,
                           montar_lote, pontuar, tokenizar)


def montar_treino(itens, benignas_por_vul, seed, limite):
    """Todas as vulneráveis + benignas na proporção pedida.
    limite > 0 (depuração): N funções no total, metade de cada classe."""
    rng = random.Random(seed)
    vul = [d for d in itens if int(d["target"]) == 1]
    ben = [d for d in itens if int(d["target"]) == 0]
    if limite:
        rng.shuffle(vul)
        rng.shuffle(ben)
        return vul[: limite // 2] + ben[: limite - limite // 2]
    if benignas_por_vul != "real":
        ben = rng.sample(ben, min(len(ben), int(benignas_por_vul) * len(vul)))
    return vul + ben


def amostra_checagem(itens, limite):
    """Amostra da validação conferida no fim de cada época: todas as vulneráveis + 4 benignas para cada.
    Semente fixa (0): é a mesma amostra em todas as rodadas, então as AUCs são comparáveis.
    A AUC não depende da proporção entre as classes, por isso não precisa da validação inteira."""
    rng = random.Random(0)
    vul = [d for d in itens if int(d["target"]) == 1]
    ben = [d for d in itens if int(d["target"]) == 0]
    if limite:
        vul = rng.sample(vul, min(len(vul), max(1, limite // 2)))
    return vul + rng.sample(ben, min(len(ben), 4 * len(vul)))


def lotes_de_treino(seqs, tamanho_lote, seed):
    """Embaralha, junta funções de comprimento parecido no mesmo lote (menos preenchimento = mais rápido)
    e embaralha a ordem dos lotes. Mesma seed + mesma época = mesmos lotes."""
    rng = random.Random(seed)
    indices = list(range(len(seqs)))
    rng.shuffle(indices)
    bloco = tamanho_lote * 50
    lotes = []
    for a in range(0, len(indices), bloco):
        grupo = sorted(indices[a:a + bloco], key=lambda i: len(seqs[i]), reverse=True)
        lotes += [grupo[b:b + tamanho_lote] for b in range(0, len(grupo), tamanho_lote)]
    rng.shuffle(lotes)
    return lotes


def enviar_hf(repo, pasta, nome):
    """Envia a pasta da rodada para um repositório PRIVADO do Hugging Face. Se falhar, o treino segue.
    (Se o repositório já existir como público, continua público: confira no site.)"""
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        api.create_repo(repo, private=True, exist_ok=True)
        api.upload_folder(repo_id=repo, folder_path=str(pasta), path_in_repo=nome,
                          commit_message=f"{nome}: adaptadores")
        print(f"Adaptador enviado. Para avaliar em outro pod: --rodada hf:{repo}/{nome}")
    except Exception as erro:  # rede, token, cota: não vale perder horas de treino por isso
        print("\n" + "!" * 72 + f"\n[ATENÇÃO] Falha ao enviar para o Hugging Face: {erro}\n"
              f"O adaptador está só em {pasta}. Envie à mão antes de apagar o pod.\n" + "!" * 72 + "\n")


def main():
    ap = argparse.ArgumentParser(description="Etapa 3 — QLoRA + cabeça de classificação (treino).")
    ap.add_argument("--modelo", default="Qwen/Qwen2.5-Coder-3B", help="versão BASE, não Instruct")
    ap.add_argument("--treino", default="../dados/primevul_train.jsonl")
    ap.add_argument("--validacao", default="../dados/primevul_valid.jsonl")
    ap.add_argument("--benignas_por_vul", required=True,
                    help='"real" (todas as benignas, ~35 por vulnerável) ou um número k (k benignas por vulnerável)')
    ap.add_argument("--peso_vul", type=float, default=1.0, help="peso da classe vulnerável na perda (1 = sem peso)")
    ap.add_argument("--epocas", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1, help="rodadas oficiais: 1, 2 e 3 (protocolo §6)")
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--lote", type=int, default=16, help="funções por passo de otimização")
    ap.add_argument("--aquecimento", type=float, default=0.03, help="fração inicial dos passos com lr subindo")
    ap.add_argument("--lora_r", type=int, default=16)
    ap.add_argument("--lora_alpha", type=int, default=32)
    ap.add_argument("--lora_dropout", type=float, default=0.05)
    ap.add_argument("--max_tokens", type=int, default=2048, help="corta funções mais longas (treino e avaliação)")
    ap.add_argument("--tokens_por_passo", type=int, default=16384,
                    help="só memória: o lote é dividido em pedaços com até isso de tokens (a conta não muda)")
    ap.add_argument("--limite_treino", type=int, default=0, help="depuração: só N funções (metade/metade)")
    ap.add_argument("--preco_hora", type=float, default=0.0, help="preço por hora do pod em US$")
    ap.add_argument("--repo_hf", default="", help="usuario/repositorio PRIVADO no Hugging Face para guardar o adaptador")
    ap.add_argument("--observacoes", default="", help="texto livre para a planilha")
    args = ap.parse_args()

    if args.benignas_por_vul != "real" and not (args.benignas_por_vul.isdigit() and int(args.benignas_por_vul) > 0):
        raise SystemExit('[ERRO] --benignas_por_vul deve ser "real" ou um número inteiro positivo.')
    fixar_seed(args.seed)  # antes de carregar o modelo: a cabeça nasce aleatória e depende da seed
    depuracao = args.limite_treino > 0
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome = (f"etapa3_{args.modelo.split('/')[-1]}_ben{args.benignas_por_vul}_s{args.seed}_{carimbo}"
            + ("_depuracao" if depuracao else ""))
    pasta = Path("../adapters") / nome
    pasta.mkdir(parents=True, exist_ok=True)
    pasta_logs = Path("../logs")
    pasta_logs.mkdir(parents=True, exist_ok=True)

    # ---- 1) Dados -----------------------------------------------------------
    for caminho in (args.treino, args.validacao):
        if not Path(caminho).exists():
            raise SystemExit(f"[ERRO] Não achei {caminho}. Rode python 00_baixar_primevul.py")
    treino = montar_treino(carregar_jsonl(Path(args.treino)), args.benignas_por_vul, args.seed, args.limite_treino)
    checagem = amostra_checagem(carregar_jsonl(Path(args.validacao)), args.limite_treino)
    dados_sha256 = impressao_digital(Path(args.treino))
    n_vul = sum(int(d["target"]) for d in treino)
    print(f"Treino: {len(treino)} funções ({n_vul} vulneráveis, {len(treino) - n_vul} benignas)"
          f"{'  [DEPURAÇÃO]' if depuracao else ''}  |  checagem na validação: {len(checagem)} funções")

    # ---- 2) Ambiente, tokens e modelo em 4 bits -----------------------------
    gpu = torch.cuda.get_device_name(0)
    ambiente_confere = conferir(gpu)  # antes de baixar o modelo: dá tempo de parar (Ctrl+C)
    tokenizer = carregar_tokenizer(args.modelo)
    pad_id = tokenizer.pad_token_id
    seqs, cortadas = tokenizar(tokenizer, treino, args.max_tokens)
    alvos = np.array([int(d["target"]) for d in treino], dtype=np.int64)
    seqs_val, _ = tokenizar(tokenizer, checagem, args.max_tokens)
    alvos_val = np.array([int(d["target"]) for d in checagem], dtype=np.int64)
    del treino, checagem
    tokens_por_epoca = int(sum(len(s) for s in seqs))
    print(f"Tokens por época: {tokens_por_epoca / 1e6:.1f} milhões  |  funções cortadas em {args.max_tokens}: {sum(cortadas)}")

    print(f"Carregando modelo em 4 bits (NF4): {args.modelo}")
    model = carregar_base(args.modelo, "nf4", pad_id)
    modelo_revisao = (getattr(model.config, "_commit_hash", None) or "")[:12]
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                            gradient_checkpointing_kwargs={"use_reentrant": False})
    model = get_peft_model(model, LoraConfig(
        task_type=TaskType.SEQ_CLS, r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=args.lora_dropout,
        target_modules=CAMADAS_LORA, modules_to_save=["score"],
    ))
    treinaveis = [p for p in model.parameters() if p.requires_grad]
    n_treinaveis = sum(p.numel() for p in treinaveis)
    memoria_modelo_gb = torch.cuda.memory_allocated() / 1e9
    print(f"Parâmetros treináveis: {n_treinaveis / 1e6:.1f} M  |  memória do modelo: {memoria_modelo_gb:.1f} GB  |  GPU: {gpu}")

    # ---- 3) Otimizador: lr sobe no aquecimento e desce em linha reta até 0 ----
    passos_por_epoca = math.ceil(len(seqs) / args.lote)
    passos_total = passos_por_epoca * args.epocas
    aquecimento = max(1, round(args.aquecimento * passos_total))
    otimizador = torch.optim.AdamW(treinaveis, lr=args.lr, weight_decay=0.0)
    agenda = torch.optim.lr_scheduler.LambdaLR(otimizador, lambda p: min(
        (p + 1) / aquecimento, max(0.0, (passos_total - p) / max(1, passos_total - aquecimento))))
    pesos = torch.tensor([1.0, args.peso_vul], device="cuda")

    registro = {
        "nome": nome, "modelo": args.modelo, "modelo_revisao": modelo_revisao, "args": vars(args),
        "camadas_lora": CAMADAS_LORA, "dados_sha256": dados_sha256, "depuracao": depuracao,
        "treino": {"n_vul": n_vul, "n_ben": len(seqs) - n_vul, "cortadas": int(sum(cortadas)),
                   "tokens_por_epoca": tokens_por_epoca, "passos_por_epoca": passos_por_epoca},
        "checagem_validacao": {"n_vul": int(alvos_val.sum()), "n_ben": int(len(alvos_val) - alvos_val.sum())},
        "parametros_treinaveis": n_treinaveis, "ambiente_confere": ambiente_confere,
        "ambiente": {**descrever_ambiente(), "peft": versao("peft"), "bitsandbytes": versao("bitsandbytes"), "gpu": gpu},
        "epocas": [], "melhor_epoca": None,
    }

    # ---- 4) Treino ----------------------------------------------------------
    arquivo_passos = pasta_logs / f"{nome}_passos.jsonl"
    inicio_total = time.time()
    tempo_treino = 0.0
    tokens_total = 0
    passo = 0
    with arquivo_passos.open("w", encoding="utf-8") as flog:
        for epoca in range(1, args.epocas + 1):
            model.train()
            t_epoca = time.time()
            tokens_epoca, soma_perda_epoca, soma_janela, n_janela = 0, 0.0, 0.0, 0
            barra = tqdm(lotes_de_treino(seqs, args.lote, seed=args.seed * 1000 + epoca),
                         desc=f"Época {epoca}/{args.epocas}")
            for k, lote in enumerate(barra, 1):
                ordenado = sorted(lote, key=lambda i: len(seqs[i]), reverse=True)
                perda_lote = 0.0
                for pedaco in dividir_por_tokens(ordenado, seqs, args.tokens_por_passo):
                    ids, mascara = montar_lote(seqs, pedaco, pad_id)
                    y = torch.from_numpy(alvos[pedaco]).cuda()
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        logits = model(input_ids=ids, attention_mask=mascara).logits
                    # soma no pedaço / tamanho do lote inteiro = média do lote, qualquer que seja a divisão
                    perda = F.cross_entropy(logits.float(), y, weight=pesos, reduction="sum") / len(lote)
                    perda.backward()
                    perda_lote += perda.item()
                    tokens_epoca += int(mascara.sum())
                torch.nn.utils.clip_grad_norm_(treinaveis, 1.0)
                otimizador.step()
                agenda.step()
                otimizador.zero_grad(set_to_none=True)
                passo += 1
                soma_perda_epoca += perda_lote
                soma_janela += perda_lote
                n_janela += 1
                if passo % 20 == 0 or k == passos_por_epoca:  # a cada 20 passos e no último da época
                    tok_s = tokens_epoca / (time.time() - t_epoca)
                    flog.write(json.dumps({"passo": passo, "epoca": epoca, "perda": round(soma_janela / n_janela, 5),
                                           "lr": agenda.get_last_lr()[0], "tokens_por_s": round(tok_s)}) + "\n")
                    flog.flush()
                    barra.set_postfix(perda=f"{soma_janela / n_janela:.4f}", tok_s=f"{tok_s:.0f}")
                    soma_janela, n_janela = 0.0, 0
            duracao = time.time() - t_epoca
            tempo_treino += duracao
            tokens_total += tokens_epoca

            # ---- fim da época: checagem na validação, salvar, enviar ----
            notas_val = pontuar(model, seqs_val, pad_id, args.tokens_por_passo * 2, desc="Checando validação")
            sinal = np.where(alvos_val == 1, 1.0, -1.0)
            perda_val = float(np.mean(np.logaddexp(0.0, -sinal * notas_val)))  # entropia cruzada
            auc_val = auc_segura(alvos_val, notas_val)
            model.save_pretrained(str(pasta / f"epoca_{epoca}"))
            registro["epocas"].append({
                "epoca": epoca, "auc_validacao": round(auc_val, 4), "perda_validacao": round(perda_val, 5),
                "perda_treino": round(soma_perda_epoca / passos_por_epoca, 5), "tempo_s": round(duracao, 1),
                "tokens_por_s": round(tokens_epoca / duracao),
            })
            validas = [e for e in registro["epocas"] if not math.isnan(e["auc_validacao"])]
            registro["melhor_epoca"] = max(validas, key=lambda e: e["auc_validacao"])["epoca"] if validas else epoca
            (pasta / "rodada.json").write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Época {epoca}: perda treino={soma_perda_epoca / passos_por_epoca:.4f}  |  validação: "
                  f"AUC={auc_val:.4f} perda={perda_val:.4f}  |  {duracao / 60:.1f} min, {tokens_epoca / duracao:.0f} tokens/s")
            if args.repo_hf:
                enviar_hf(args.repo_hf, pasta, nome)

    tempo_total = time.time() - inicio_total
    memoria_pico_gb = torch.cuda.max_memory_allocated() / 1e9
    custo_usd = args.preco_hora * tempo_total / 3600.0
    (pasta_logs / f"{nome}.json").write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- 5) Planilha --------------------------------------------------------
    melhor = next(e for e in registro["epocas"] if e["epoca"] == registro["melhor_epoca"])
    linha = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rodada": nome,
        "modelo": args.modelo,
        "seed": args.seed,
        "benignas_por_vul": args.benignas_por_vul,
        "n_vul": n_vul, "n_ben": len(seqs) - n_vul,
        "peso_vul": args.peso_vul,
        "epocas": args.epocas, "lr": args.lr, "lote": args.lote, "aquecimento": args.aquecimento,
        "lora_r": args.lora_r, "lora_alpha": args.lora_alpha, "lora_dropout": args.lora_dropout,
        "max_tokens": args.max_tokens, "cortadas": int(sum(cortadas)), "tokens_por_epoca": tokens_por_epoca,
        "parametros_treinaveis": n_treinaveis,
        "auc_validacao_por_epoca": ";".join(str(e["auc_validacao"]) for e in registro["epocas"]),
        "melhor_epoca": registro["melhor_epoca"], "auc_validacao_melhor": melhor["auc_validacao"],
        "tokens_por_s": round(tokens_total / max(1.0, tempo_treino)),
        "memoria_modelo_gb": round(memoria_modelo_gb, 2), "memoria_pico_gb": round(memoria_pico_gb, 2),
        "tempo_treino_s": round(tempo_treino, 1), "tempo_total_s": round(tempo_total, 1),
        "gpu": gpu, "preco_hora_usd": args.preco_hora, "custo_total_usd": round(custo_usd, 4),
        "repo_hf": args.repo_hf,
        "depuracao": "sim" if depuracao else "nao",
        "observacoes": args.observacoes,
        "ambiente_confere": ambiente_confere,
        **{k: registro["ambiente"][k] or "" for k in ("torch", "cuda", "transformers", "tokenizers", "peft", "bitsandbytes")},
        "modelo_revisao": modelo_revisao,
        "dados_sha256": dados_sha256,
    }
    arquivo_csv = Path("../resultados/treinos_etapa3.csv")
    arquivo_csv.parent.mkdir(parents=True, exist_ok=True)
    gravar_linha_csv(arquivo_csv, linha)

    print("\n================ TREINO CONCLUÍDO ================")
    print(f"Rodada: {nome}")
    print(f"Melhor época (AUC na validação): {registro['melhor_epoca']}  AUC={melhor['auc_validacao']}")
    print(f"Tempo total={tempo_total / 60:.1f} min  |  memória pico={memoria_pico_gb:.1f} GB  |  custo US$ {custo_usd:.2f}")
    print(f"Adaptadores em: {pasta}")
    print(f"Receita e perda por passo em: {pasta_logs / (nome + '.json')} e {arquivo_passos}")
    print(f"Linha gravada em: {arquivo_csv}")
    print(f"Próximo: python 07_avaliar_classificador.py --rodada {pasta} --preco_hora {args.preco_hora}")
    if args.preco_hora == 0:
        print("[ATENÇÃO] --preco_hora não informado: o custo saiu zerado.")
    if ambiente_confere != "sim":
        print(f"[ATENÇÃO] Ambiente fora da trava (ambiente_confere={ambiente_confere}): esta rodada serve só como teste.")


if __name__ == "__main__":
    main()
