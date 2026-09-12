"""
03_inferencia_etapa1.py — Etapa 1 (baseline): o modelo responde YES/NO para cada função,
o script conta os acertos, mede memória/tempo/custo e grava uma linha no CSV de resultados.

O que este script faz, em ordem:
  1. Carrega o modelo na GPU em 16 bits (sem encolher, sem treinar = o "ponto de referência").
  2. Pega N funções do PrimeVul (por padrão, metade com falha e metade sem, só para depurar).
  3. Para cada função: monta a pergunta, pede a resposta, transforma "YES/NO" em 1/0.
  4. Compara com o rótulo verdadeiro e calcula F1, precisão, revocação, FPR, acurácia.
  5. Mede memória de GPU, tempo por função e custo (preço/hora × tempo).
  6. Grava tudo: uma linha em ../resultados/resultados_etapa1.csv
     e a resposta crua de cada função em ../logs/ (para você conferir o parsing).

Uso (primeira rodada recomendada):
  python 03_inferencia_etapa1.py --n 50

Outros exemplos:
  python 03_inferencia_etapa1.py --n 50 --preco_hora 0.44          # informe o preço/hora do seu pod
  python 03_inferencia_etapa1.py --n 200 --sem_balancear            # amostra com a proporção real (~1:32)
  python 03_inferencia_etapa1.py --n 50 --modelo Qwen/Qwen2.5-Coder-7B-Instruct
"""

import argparse
import csv
import json
import random
import re
import time
from datetime import datetime
from pathlib import Path

import torch
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# ----------------------------------------------------------------------------
# Configuração fixa desta versão de prompt. Se mudar o texto, mude a versão
# (assim a planilha registra qual prompt gerou cada número).
# ----------------------------------------------------------------------------
PROMPT_VERSAO = "v1"
SISTEMA = "You are an expert in software security and static code analysis."
INSTRUCAO = (
    "Analyze the following C/C++ function and decide whether it contains a security vulnerability.\n"
    "Answer with exactly one word: YES or NO.\n\n"
    "```c\n{codigo}\n```"
)


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def carregar_jsonl(caminho: Path):
    """Lê um .jsonl (um JSON por linha)."""
    itens = []
    with caminho.open("r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                itens.append(json.loads(linha))
    return itens


def escolher_amostra(itens, n, balanceado, seed):
    """Escolhe N funções. Balanceado = metade target=1, metade target=0 (bom para depurar,
    porque no teste real só ~3% são vulneráveis e uma amostra pequena poderia vir sem nenhuma)."""
    for pos, d in enumerate(itens):
        d["_pos"] = pos  # posição original no arquivo (necessária para a avaliação pareada)
    rng = random.Random(seed)
    if not balanceado:
        rng.shuffle(itens)
        return itens[:n]
    vul = [d for d in itens if int(d["target"]) == 1]
    ben = [d for d in itens if int(d["target"]) == 0]
    rng.shuffle(vul)
    rng.shuffle(ben)
    metade = n // 2
    amostra = vul[:metade] + ben[: n - metade]
    rng.shuffle(amostra)
    return amostra


def truncar_codigo(tokenizer, codigo, max_tokens):
    """Corta funções muito longas pelo número de tokens, para não estourar a memória."""
    ids = tokenizer(codigo, add_special_tokens=False)["input_ids"]
    if len(ids) <= max_tokens:
        return codigo, False
    return tokenizer.decode(ids[:max_tokens]), True


def interpretar_resposta(texto):
    """Transforma a resposta em 1 (vulnerável) ou 0 (não). Devolve também um status:
    'ok' se achou YES/NO com clareza, 'indefinido' se o modelo enrolou."""
    s = texto.strip().lower()
    primeira = re.match(r"[a-záéíóúãõç]+", s)
    primeira = primeira.group(0) if primeira else ""
    if primeira in ("yes", "sim"):
        return 1, "ok"
    if primeira in ("no", "não", "nao"):
        return 0, "ok"
    # Se não veio na primeira palavra, procura nos primeiros caracteres.
    # Negativos ANTES dos positivos, porque "not vulnerable" contém "vulnerable".
    trecho = s[:60]
    if re.search(r"\b(no|não|nao|not vulnerable|safe|no vulnerability)\b", trecho):
        return 0, "ok"
    if re.search(r"\b(yes|sim|vulnerable)\b", trecho):
        return 1, "ok"
    return 0, "indefinido"  # não entendeu: conta como "não vulnerável" e registra


# ----------------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Etapa 1 — baseline por prompt (YES/NO).")
    ap.add_argument("--modelo", default="Qwen/Qwen2.5-Coder-3B-Instruct")
    ap.add_argument("--dados", default="../dados/primevul_test.jsonl")
    ap.add_argument("--n", type=int, default=50, help="quantas funções avaliar")
    ap.add_argument("--sem_balancear", action="store_true",
                    help="usa a proporção real do teste em vez de metade/metade")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max_tokens_entrada", type=int, default=2048,
                    help="corta funções mais longas que isso (em tokens)")
    ap.add_argument("--preco_hora", type=float, default=0.0,
                    help="preço por hora do pod em US$ (para calcular o custo)")
    ap.add_argument("--observacoes", default="", help="texto livre para a planilha")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    random.seed(args.seed)

    # ---- 1) Dados -----------------------------------------------------------
    caminho_dados = Path(args.dados)
    if not caminho_dados.exists():
        raise SystemExit(f"[ERRO] Não achei {caminho_dados}. Baixe o PrimeVul para ../dados/ "
                         f"(veja o cabeçalho de 02_ver_dados.py).")
    itens = carregar_jsonl(caminho_dados)
    amostra = escolher_amostra(itens, args.n, balanceado=not args.sem_balancear, seed=args.seed)
    print(f"Dados: {caminho_dados}  |  usando {len(amostra)} funções "
          f"({'proporção real' if args.sem_balancear else 'metade/metade'})")

    # ---- 2) Modelo em 16 bits -----------------------------------------------
    print(f"Carregando modelo: {args.modelo}")
    tokenizer = AutoTokenizer.from_pretrained(args.modelo)
    try:  # versões novas do transformers usam `dtype`; as antigas, `torch_dtype`
        model = AutoModelForCausalLM.from_pretrained(args.modelo, dtype=torch.float16, device_map="cuda")
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(args.modelo, torch_dtype=torch.float16, device_map="cuda")
    model.eval()
    n_params_bilhoes = sum(p.numel() for p in model.parameters()) / 1e9
    gpu_nome = torch.cuda.get_device_name(0)
    print(f"Modelo carregado: {n_params_bilhoes:.2f} B parâmetros  |  GPU: {gpu_nome}")

    # ---- 3) Laço de inferência ----------------------------------------------
    pasta_logs = Path("../logs")
    pasta_logs.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_log = pasta_logs / f"etapa1_{carimbo}.jsonl"

    verdadeiros, previstos = [], []
    indefinidos, truncadas = 0, 0
    tempos = []

    inicio_total = time.time()
    with arquivo_log.open("w", encoding="utf-8") as flog:
        for i, item in enumerate(tqdm(amostra, desc="Avaliando")):
            codigo, foi_truncada = truncar_codigo(tokenizer, item["func"], args.max_tokens_entrada)
            truncadas += int(foi_truncada)

            mensagens = [
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": INSTRUCAO.format(codigo=codigo)},
            ]
            # return_dict=True devolve input_ids + attention_mask (funciona em versões novas e antigas)
            entrada = tokenizer.apply_chat_template(
                mensagens, add_generation_prompt=True, return_tensors="pt", return_dict=True
            )
            entrada = {k: v.to(model.device) for k, v in entrada.items()}
            n_entrada = entrada["input_ids"].shape[1]

            t0 = time.time()
            with torch.no_grad():
                saida = model.generate(
                    **entrada,
                    max_new_tokens=5,          # só precisamos de YES/NO
                    do_sample=False,           # determinístico (equivale a temperatura 0)
                    temperature=None, top_p=None, top_k=None,  # evita avisos do generation_config
                    pad_token_id=tokenizer.eos_token_id,
                )
            tempos.append(time.time() - t0)

            resposta = tokenizer.decode(saida[0][n_entrada:], skip_special_tokens=True)
            pred, status = interpretar_resposta(resposta)
            indefinidos += int(status == "indefinido")

            alvo = int(item["target"])
            verdadeiros.append(alvo)
            previstos.append(pred)

            flog.write(json.dumps({
                "i": i, "pos": item.get("_pos"), "idx": item.get("idx"),
                "project": item.get("project"), "commit_id": item.get("commit_id"),
                "func_hash": item.get("func_hash"),
                "target": alvo, "pred": pred, "status": status,
                "resposta_crua": resposta, "truncada": foi_truncada,
                "tempo_s": round(tempos[-1], 3),
            }, ensure_ascii=False) + "\n")

            if i < 5:  # mostra as primeiras respostas para você ver o parsing funcionando
                print(f"  [{i}] target={alvo} pred={pred} ({status})  resposta='{resposta.strip()}'")

    tempo_total = time.time() - inicio_total

    # ---- 4) Métricas de qualidade -------------------------------------------
    tn, fp, fn, tp = confusion_matrix(verdadeiros, previstos, labels=[0, 1]).ravel()
    f1 = f1_score(verdadeiros, previstos, pos_label=1, zero_division=0)
    precisao = precision_score(verdadeiros, previstos, pos_label=1, zero_division=0)
    revocacao = recall_score(verdadeiros, previstos, pos_label=1, zero_division=0)
    acuracia = accuracy_score(verdadeiros, previstos)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # ---- 5) Custo -----------------------------------------------------------
    memoria_gb = torch.cuda.max_memory_allocated() / 1e9
    tempo_por_funcao = sum(tempos) / len(tempos)
    custo_usd = args.preco_hora * (tempo_total / 3600.0)

    # ---- 6) Gravar na planilha ----------------------------------------------
    pasta_res = Path("../resultados")
    pasta_res.mkdir(parents=True, exist_ok=True)
    arquivo_csv = pasta_res / "resultados_etapa1.csv"
    linha = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "modelo": args.modelo,
        "tamanho_B": round(n_params_bilhoes, 2),
        "precisao_bits": 16,
        "metodo_quantizacao": "nenhum",
        "prompt_versao": PROMPT_VERSAO,
        "seed": args.seed,
        "n_funcoes": len(amostra),
        "amostra": "proporcao_real" if args.sem_balancear else "balanceada",
        "f1": round(f1, 4),
        "precisao": round(precisao, 4),
        "revocacao": round(revocacao, 4),
        "fpr": round(fpr, 4),
        "acuracia": round(acuracia, 4),
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "indefinidos": indefinidos,
        "truncadas": truncadas,
        "memoria_gpu_gb": round(memoria_gb, 2),
        "tempo_por_funcao_s": round(tempo_por_funcao, 3),
        "tempo_total_s": round(tempo_total, 1),
        "gpu": gpu_nome,
        "preco_hora_usd": args.preco_hora,
        "custo_total_usd": round(custo_usd, 4),
        "log": arquivo_log.name,
        "observacoes": args.observacoes,
    }
    novo = not arquivo_csv.exists()
    with arquivo_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linha.keys()))
        if novo:
            w.writeheader()
        w.writerow(linha)

    # ---- 7) Resumo na tela --------------------------------------------------
    print("\n================ RESULTADO ================")
    print(f"F1={f1:.3f}  precisão={precisao:.3f}  revocação={revocacao:.3f}  FPR={fpr:.3f}  acurácia={acuracia:.3f}")
    print(f"TP={tp} FP={fp} FN={fn} TN={tn}  |  respostas indefinidas={indefinidos}  |  truncadas={truncadas}")
    print(f"Memória GPU (pico)={memoria_gb:.2f} GB  |  tempo/função={tempo_por_funcao:.2f}s  |  total={tempo_total:.0f}s")
    print(f"Custo estimado: US$ {custo_usd:.4f}  (preço/hora informado: {args.preco_hora})")
    print(f"Linha gravada em: {arquivo_csv}")
    print(f"Respostas cruas em: {arquivo_log}")
    if indefinidos > 0:
        print(f"[ATENÇÃO] {indefinidos} respostas não foram YES/NO claros — abra o log e ajuste o prompt/parsing.")


if __name__ == "__main__":
    main()
