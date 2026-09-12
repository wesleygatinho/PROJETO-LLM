"""
02_ver_dados.py — Abre o PrimeVul e mostra como ele é.

Objetivo: você ENTENDER os dados antes de rodar qualquer modelo.

Como obter o PrimeVul:
  Opção A (oficial): repositório https://github.com/DLVulDet/PrimeVul — o README
    aponta o link de download. Baixe os arquivos .jsonl e coloque em ../dados/.
    Os nomes costumam ser: primevul_train.jsonl, primevul_valid.jsonl,
    primevul_test.jsonl e as versões *_paired.jsonl (pares vulnerável/corrigida).
  Opção B (espelho no Hugging Face, comunidade): datasets "colin/PrimeVul".
    Use só se a opção A der trabalho; confira se as colunas batem.

Uso:
  python 02_ver_dados.py                      # procura ../dados/primevul_test.jsonl
  python 02_ver_dados.py --arquivo ../dados/primevul_test_paired.jsonl
"""

import argparse
import json
from collections import Counter
from pathlib import Path


def carregar_jsonl(caminho: Path):
    """Lê um arquivo .jsonl (um JSON por linha) e devolve uma lista de dicionários."""
    linhas = []
    with caminho.open("r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                linhas.append(json.loads(linha))
    return linhas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquivo", default="../dados/primevul_test.jsonl",
                    help="caminho do .jsonl a inspecionar")
    args = ap.parse_args()

    caminho = Path(args.arquivo)
    if not caminho.exists():
        print(f"[ERRO] Não achei {caminho}. Baixe o PrimeVul para ../dados/ (veja o cabeçalho deste arquivo).")
        return

    dados = carregar_jsonl(caminho)
    print(f"Arquivo: {caminho}")
    print(f"Total de itens: {len(dados)}")

    # 1) Quais colunas existem? (No PrimeVul, o código fica em 'func' e o rótulo em 'target'.)
    print("\nColunas do primeiro item:")
    for chave, valor in dados[0].items():
        resumo = str(valor).replace("\n", " ")[:80]
        print(f"  - {chave}: {resumo}")

    # 2) Quantos são vulneráveis (1) e quantos não (0)?
    if "target" in dados[0]:
        contagem = Counter(int(d["target"]) for d in dados)
        print(f"\nRótulos: {dict(contagem)}  (1 = vulnerável, 0 = sem vulnerabilidade)")
        total = sum(contagem.values())
        print(f"Proporção de vulneráveis: {contagem.get(1, 0) / total:.2%}")
    else:
        print("\n[AVISO] Não achei a coluna 'target'. Confira o nome da coluna de rótulo acima.")

    # 3) Um exemplo de cada, para você ver a cara do código.
    campo_codigo = "func" if "func" in dados[0] else None
    if campo_codigo and "target" in dados[0]:
        for alvo in (1, 0):
            ex = next((d for d in dados if int(d["target"]) == alvo), None)
            if ex:
                print(f"\n===== Exemplo com target={alvo} (primeiras 15 linhas) =====")
                print("\n".join(ex[campo_codigo].splitlines()[:15]))
    else:
        print("\n[AVISO] Não achei a coluna 'func' com o código. Veja as colunas listadas acima.")

    # 4) Tamanho das funções (importa para não estourar a memória da GPU).
    if campo_codigo:
        tamanhos = sorted(len(d[campo_codigo]) for d in dados)
        mediana = tamanhos[len(tamanhos) // 2]
        print(f"\nTamanho das funções (caracteres): mediana={mediana}, máx={tamanhos[-1]}")


if __name__ == "__main__":
    main()
