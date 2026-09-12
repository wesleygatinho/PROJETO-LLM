"""
04_metricas_pareadas.py — Avaliação PAREADA (o teste mais importante do trabalho).

Ideia: cada função vulnerável tem uma "irmã" — a mesma função já corrigida. As duas são quase
iguais no texto. Um modelo que entende de verdade responde YES para a vulnerável e NO para a
corrigida. Um modelo que só "chuta pelo formato" responde a mesma coisa para as duas.

Para cada par, classificamos o resultado em um de quatro desfechos (como no artigo do PrimeVul):
  P-C  (pair-correct)  : vulnerável=YES e corrigida=NO   -> o modelo distinguiu (o que queremos)
  P-V  (pair-vulnerable): as duas = YES                  -> achou tudo vulnerável
  P-B  (pair-benign)   : as duas = NO                   -> achou tudo seguro
  P-R  (pair-reversed) : vulnerável=NO e corrigida=YES  -> trocou (o pior caso)
Chute aleatório daria ~25% em cada um. O que interessa é o P-C.

Requisitos:
  - o arquivo de dados pareado (ex.: ../dados/primevul_test_paired.jsonl);
  - um log gerado pelo 03_inferencia_etapa1.py que contenha o campo "pos"
    (versão atual do script; logs antigos, sem "pos", não servem — rode de novo).

Uso:
  python 04_metricas_pareadas.py --dados ../dados/primevul_test_paired.jsonl --log ../logs/etapa1_XXXX.jsonl
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def carregar_jsonl(caminho):
    with Path(caminho).open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def formar_pares(dados):
    """Devolve lista de pares (pos_vulneravel, pos_corrigida).
    1º tenta a regra do PrimeVul: vulnerável e corrigida vêm em linhas consecutivas.
    Se isso falhar para muitos pares, agrupa por (project, commit_id) e junta um 1 com um 0."""
    pares, falhas = [], 0
    for a in range(0, len(dados) - 1, 2):
        x, y = dados[a], dados[a + 1]
        mesmo_commit = (x.get("commit_id") == y.get("commit_id")) if "commit_id" in x else True
        alvos = {int(x["target"]), int(y["target"])}
        if alvos == {0, 1} and mesmo_commit:
            vul, ben = (a, a + 1) if int(x["target"]) == 1 else (a + 1, a)
            pares.append((vul, ben))
        else:
            falhas += 1
    if falhas <= max(1, len(dados) // 20):  # até 5% de falhas: aceita a regra consecutiva
        return pares, "consecutivos"

    # Fallback: agrupar por projeto+commit
    grupos = defaultdict(lambda: {"1": [], "0": []})
    for pos, d in enumerate(dados):
        chave = (d.get("project"), d.get("commit_id"))
        grupos[chave][str(int(d["target"]))].append(pos)
    pares = []
    for g in grupos.values():
        for vul, ben in zip(g["1"], g["0"]):
            pares.append((vul, ben))
    return pares, "por project+commit_id"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="../dados/primevul_test_paired.jsonl")
    ap.add_argument("--log", required=True, help="log .jsonl gerado pelo 03_inferencia_etapa1.py")
    ap.add_argument("--rotulo", default="", help="texto livre para identificar a rodada no CSV")
    args = ap.parse_args()

    dados = carregar_jsonl(args.dados)
    log = carregar_jsonl(args.log)
    if not log or "pos" not in log[0]:
        raise SystemExit("[ERRO] Este log não tem o campo 'pos'. Rode o 03_inferencia_etapa1.py de novo "
                         "(versão atual) sobre o arquivo pareado e use o novo log.")

    pred_por_pos = {r["pos"]: int(r["pred"]) for r in log}
    pares, metodo = formar_pares(dados)

    pc = pv = pb = pr = 0
    avaliados = 0
    for vul, ben in pares:
        if vul not in pred_por_pos or ben not in pred_por_pos:
            continue  # o log pode ter só uma amostra do arquivo
        avaliados += 1
        a, b = pred_por_pos[vul], pred_por_pos[ben]
        if a == 1 and b == 0:
            pc += 1
        elif a == 1 and b == 1:
            pv += 1
        elif a == 0 and b == 0:
            pb += 1
        else:
            pr += 1

    if avaliados == 0:
        raise SystemExit("[ERRO] Nenhum par completo encontrado no log. O log cobre o arquivo pareado inteiro?")

    pct = lambda k: 100.0 * k / avaliados
    print("================ AVALIAÇÃO PAREADA ================")
    print(f"pares no arquivo: {len(pares)} (formados por: {metodo})  |  pares avaliados: {avaliados}")
    print(f"P-C  (distinguiu)      : {pc:5d}  = {pct(pc):5.1f}%   <- o que importa (acaso ≈ 25%)")
    print(f"P-V  (tudo vulnerável) : {pv:5d}  = {pct(pv):5.1f}%")
    print(f"P-B  (tudo seguro)     : {pb:5d}  = {pct(pb):5.1f}%")
    print(f"P-R  (trocou)          : {pr:5d}  = {pct(pr):5.1f}%")

    saida = Path("../resultados/resultados_pareado.csv")
    saida.parent.mkdir(parents=True, exist_ok=True)
    linha = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "log": Path(args.log).name, "dados": Path(args.dados).name,
        "pares_avaliados": avaliados, "metodo_pareamento": metodo,
        "P_C": pc, "P_V": pv, "P_B": pb, "P_R": pr,
        "P_C_pct": round(pct(pc), 2), "P_V_pct": round(pct(pv), 2),
        "P_B_pct": round(pct(pb), 2), "P_R_pct": round(pct(pr), 2),
        "rotulo": args.rotulo,
    }
    novo = not saida.exists()
    with saida.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linha.keys()))
        if novo:
            w.writeheader()
        w.writerow(linha)
    print(f"\nLinha gravada em: {saida}")


if __name__ == "__main__":
    main()
