"""
classificador.py — peças comuns da Etapa 3 (QLoRA + cabeça de classificação).

Quem usa: 06_treinar_qlora.py e 07_avaliar_classificador.py. Não é para rodar sozinho.

A ideia da cabeça de classificação: em vez de pedir ao modelo que ESCREVA "YES/NO" (Etapa 1),
o modelo lê só o código da função e devolve dois números (logits): um para "benigna" e um para
"vulnerável". A NOTA de cada função é a diferença entre os dois. Nota > 0 = o modelo acha mais
provável ser vulnerável. Como a nota é contínua, dá para mudar o limiar de decisão — é o que o
VD-S precisa (o limiar que deixa passar no máximo 0,5% de alarmes falsos).
"""

import importlib
import json
import random

import numpy as np
import torch
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig

# Reaproveita as funções da Etapa 1: mesma leitura dos dados, mesma amostragem, mesma planilha
# e, principalmente, a MESMA regra de formar os pares (resultados comparáveis entre etapas).
_etapa1 = importlib.import_module("03_inferencia_etapa1")
_pareado = importlib.import_module("04_metricas_pareadas")
_baixar = importlib.import_module("00_baixar_primevul")
carregar_jsonl = _etapa1.carregar_jsonl
escolher_amostra = _etapa1.escolher_amostra
impressao_digital = _etapa1.impressao_digital
gravar_linha_csv = _etapa1.gravar_linha_csv
formar_pares = _pareado.formar_pares
qual_release = _baixar.qual_release  # para a planilha registrar de qual release são os dados

# LoRA em todas as camadas lineares dos blocos (recomendação do artigo do QLoRA, Dettmers et al. 2023).
CAMADAS_LORA = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
FPR_VDS = 0.005  # VD-S: no máximo 0,5% de alarmes falsos (valor do artigo do PrimeVul)


def fixar_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ----------------------------------------------------------------------------
# Modelo e tokens
# ----------------------------------------------------------------------------
def carregar_tokenizer(modelo):
    tokenizer = AutoTokenizer.from_pretrained(modelo)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def carregar_base(modelo, precisao, pad_token_id):
    """Modelo base com cabeça de 2 saídas. precisao: 'nf4' (4 bits, como no QLoRA) ou 'bf16'.
    O aviso "Some weights ... were not initialized: ['score.weight']" é esperado: a cabeça nasce
    aleatória no treino e é trocada pela treinada na avaliação."""
    kwargs = dict(num_labels=2, dtype=torch.bfloat16, device_map="cuda")
    if precisao == "nf4":
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            llm_int8_skip_modules=["score"],  # a cabeça fica em precisão cheia
        )
    elif precisao != "bf16":
        raise ValueError(f"precisão desconhecida: {precisao}")
    model = AutoModelForSequenceClassification.from_pretrained(modelo, **kwargs)
    # Num lote, as funções curtas são completadas com pad; o modelo usa o pad_token_id para achar
    # o último token de verdade de cada função (é nele que a cabeça lê a nota).
    model.config.pad_token_id = pad_token_id
    return model


def tokenizar(tokenizer, itens, max_tokens, tamanho_bloco=1000):
    """Código de cada função -> tokens. Funções mais longas que max_tokens perdem o fim
    (fica o começo, como na Etapa 1). Devolve (lista de arrays, lista de 'foi cortada')."""
    seqs, cortadas = [], []
    for a in range(0, len(itens), tamanho_bloco):
        textos = [d["func"] for d in itens[a:a + tamanho_bloco]]
        for ids in tokenizer(textos, add_special_tokens=False)["input_ids"]:
            cortadas.append(len(ids) > max_tokens)
            seqs.append(np.asarray(ids[:max_tokens], dtype=np.int64))
    return seqs, cortadas


def dividir_por_tokens(indices, seqs, tokens_max):
    """Agrupa índices (em ordem DECRESCENTE de comprimento) em lotes de até tokens_max tokens,
    contando o preenchimento. Todo lote tem pelo menos uma função."""
    lotes, atual = [], []
    for i in indices:
        maior = len(seqs[atual[0]]) if atual else len(seqs[i])
        if atual and (len(atual) + 1) * maior > tokens_max:
            lotes.append(atual)
            atual = []
        atual.append(i)
    if atual:
        lotes.append(atual)
    return lotes


def montar_lote(seqs, lote, pad_id):
    """Empilha as funções do lote numa matriz, completando à direita com pad."""
    maior = max(len(seqs[i]) for i in lote)
    ids = torch.full((len(lote), maior), pad_id, dtype=torch.long)
    mascara = torch.zeros((len(lote), maior), dtype=torch.long)
    for j, i in enumerate(lote):
        n = len(seqs[i])
        ids[j, :n] = torch.from_numpy(seqs[i])
        mascara[j, :n] = 1
    return ids.cuda(), mascara.cuda()


@torch.no_grad()
def pontuar(model, seqs, pad_id, tokens_por_lote, desc="Pontuando"):
    """Nota de cada função = logit(vulnerável) - logit(benigna).
    As funções são processadas da mais longa para a mais curta (a falta de memória aparece logo
    no primeiro lote) e a divisão em lotes é fixa: a mesma rodada dá as mesmas notas."""
    estava_treinando = model.training
    model.eval()
    ordem = sorted(range(len(seqs)), key=lambda i: len(seqs[i]), reverse=True)
    notas = np.zeros(len(seqs), dtype=np.float64)
    for lote in tqdm(dividir_por_tokens(ordem, seqs, tokens_por_lote), desc=desc):
        ids, mascara = montar_lote(seqs, lote, pad_id)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = model(input_ids=ids, attention_mask=mascara).logits.float()
        notas[lote] = (logits[:, 1] - logits[:, 0]).cpu().numpy()
    if estava_treinando:
        model.train()
    return notas


def gravar_log_notas(arquivo, amostra, notas, limiar=0.0, extras=None):
    """Uma linha por função, na ordem do arquivo de dados. Tem 'pos' e 'pred' (nota > limiar), então
    o log serve também para o 04_metricas_pareadas.py e o 05_comparar_logs.py.
    extras: colunas a mais, como {"n_tokens": [...]}, alinhadas com a amostra."""
    with arquivo.open("w", encoding="utf-8") as f:
        for j in sorted(range(len(amostra)), key=lambda j: amostra[j]["_pos"]):
            d = amostra[j]
            linha = {"pos": d["_pos"], "idx": d.get("idx"), "project": d.get("project"),
                     "commit_id": d.get("commit_id"), "func_hash": d.get("func_hash"),
                     "target": int(d["target"]), "nota": round(float(notas[j]), 5),
                     "pred": int(notas[j] > limiar)}
            for nome, valores in (extras or {}).items():
                v = valores[j]
                linha[nome] = bool(v) if isinstance(v, (bool, np.bool_)) else int(v)
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")


# ----------------------------------------------------------------------------
# Métricas
# ----------------------------------------------------------------------------
def limiar_para_fpr(notas, alvos, fpr_max=FPR_VDS):
    """Menor limiar t tal que a regra 'nota > t' gere no máximo fpr_max de alarmes falsos
    NESTAS funções. Usado na validação para escolher o limiar do VD-S."""
    benignas = np.sort(notas[alvos == 0])[::-1]
    k = int(np.floor(fpr_max * len(benignas)))  # quantos alarmes falsos são tolerados
    return float(benignas[min(k, len(benignas) - 1)])


def taxas_no_limiar(notas, alvos, limiar):
    """(FNR, FPR) com a regra 'nota > limiar'. FNR no limiar da validação = VD-S (menor é melhor)."""
    previsto = notas > limiar
    vul = alvos == 1
    fnr = float((~previsto & vul).sum() / max(1, vul.sum()))
    fpr = float((previsto & ~vul).sum() / max(1, (~vul).sum()))
    return fnr, fpr


def auc_segura(alvos, notas):
    return float(roc_auc_score(alvos, notas)) if len(set(alvos.tolist())) == 2 else float("nan")


def metricas_classificacao(notas, alvos):
    """Métricas no limiar padrão (nota > 0), as mesmas da Etapa 1, mais a AUC."""
    previsto = (notas > 0).astype(int)
    tn, fp, fn, tp = confusion_matrix(alvos, previsto, labels=[0, 1]).ravel()
    return {
        "f1": f1_score(alvos, previsto, pos_label=1, zero_division=0),
        "precisao": precision_score(alvos, previsto, pos_label=1, zero_division=0),
        "revocacao": recall_score(alvos, previsto, pos_label=1, zero_division=0),
        "fpr": fp / (fp + tn) if (fp + tn) > 0 else 0.0,
        "acuracia": accuracy_score(alvos, previsto),
        "auc": auc_segura(alvos, notas),
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
    }


def metricas_pareadas(nota_por_pos, pares):
    """P-C/P-V/P-B/P-R no limiar padrão (nota > 0), como o 04_metricas_pareadas.py.
    'ordenados' não depende de limiar: pares em que a vulnerável recebeu nota MAIOR que a corrigida
    (acaso = 50%). Serve para comparar variantes mesmo quando o limiar padrão fica mal calibrado."""
    r = {"avaliados": 0, "P_C": 0, "P_V": 0, "P_B": 0, "P_R": 0, "ordenados": 0}
    for vul, ben in pares:
        if vul not in nota_por_pos or ben not in nota_por_pos:
            continue
        r["avaliados"] += 1
        a, b = nota_por_pos[vul], nota_por_pos[ben]
        chave = {(True, False): "P_C", (True, True): "P_V", (False, False): "P_B", (False, True): "P_R"}
        r[chave[(a > 0, b > 0)]] += 1
        r["ordenados"] += int(a > b)
    return r
