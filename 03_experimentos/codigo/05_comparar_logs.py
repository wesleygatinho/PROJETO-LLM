"""
05_comparar_logs.py — confere se duas rodadas deram as MESMAS respostas, função por função.

Para que serve: testar reprodutibilidade. Exemplo: a mesma configuração rodada num pod novo,
em outra GPU ou com outras versões das bibliotecas. Se o resultado for IDÊNTICAS, nada mudou.
Serve para os logs da Etapa 1 (texto cru) e da Etapa 3 (nota da cabeça de classificação).

Uso:
  python 05_comparar_logs.py ../logs/etapa1_A.jsonl ../logs/etapa1_B.jsonl
"""

import argparse
import json
from pathlib import Path


def carregar(caminho):
    with Path(caminho).open("r", encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def main():
    ap = argparse.ArgumentParser(description="Compara as respostas de duas rodadas.")
    ap.add_argument("log_a")
    ap.add_argument("log_b")
    args = ap.parse_args()

    a, b = carregar(args.log_a), carregar(args.log_b)
    if not a or not b:
        raise SystemExit("[ERRO] Um dos logs está vazio.")
    # "pos" = posição da função no arquivo de dados. Logs antigos não têm; aí tenta "idx" e,
    # por último, "i" (ordem de avaliação, que só bate se as duas rodadas usaram os mesmos dados e seed).
    chave = next((c for c in ("pos", "idx", "i") if a[0].get(c) is not None and b[0].get(c) is not None), None)
    if chave is None:
        raise SystemExit("[ERRO] Os logs não têm um campo em comum para identificar as funções.")
    if chave == "i":
        print("[AVISO] Logs antigos: comparando pela ordem de avaliação (vale só com mesmos dados e mesma seed).")
    ma = {r[chave]: r for r in a}
    mb = {r[chave]: r for r in b}
    comuns = sorted(set(ma) & set(mb))
    if not comuns:
        raise SystemExit("[ERRO] Os dois logs não têm nenhuma função em comum.")

    so_a, so_b = len(set(ma) - set(mb)), len(set(mb) - set(ma))
    # Etapa 1 guarda o texto cru; Etapa 3 guarda a nota (número). Compara o que existir.
    cru = lambda r: r["resposta_crua"] if "resposta_crua" in r else r.get("nota")
    difs = [k for k in comuns if int(ma[k]["pred"]) != int(mb[k]["pred"])]
    crus = [k for k in comuns if cru(ma[k]) != cru(mb[k])]

    print(f"funções em comum: {len(comuns)}  (só no A: {so_a}, só no B: {so_b})")
    print(f"respostas YES/NO diferentes: {len(difs)}")
    print(f"texto cru / nota diferente:  {len(crus)}")
    for k in difs[:10]:
        print(f"  {chave}={k}  target={ma[k]['target']}  "
              f"A={str(cru(ma[k])).strip()!r}  B={str(cru(mb[k])).strip()!r}")
    if len(difs) > 10:
        print(f"  ... e mais {len(difs) - 10}")

    identicas = not difs and not crus and so_a == 0 and so_b == 0
    print("\nRESULTADO:", "IDÊNTICAS" if identicas else "DIFERENTES")


if __name__ == "__main__":
    main()
