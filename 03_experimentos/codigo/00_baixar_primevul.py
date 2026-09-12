"""
00_baixar_primevul.py — Baixa o PrimeVul para ../dados/ com os nomes de arquivo oficiais.

Duas fontes possíveis:
  (padrão) Hugging Face, espelho "colin/PrimeVul" — licença MIT, sem gating, colunas iguais
           às oficiais (func, target, func_hash, cwe, cve...). É o caminho mais simples no pod.
  --fonte drive  Pasta oficial no Google Drive (release v0.1 do repositório DLVulDet/PrimeVul).
           Use se quiser os arquivos exatamente como os autores publicaram. Precisa de `gdown`.

Ao final, o script conta quantas funções vulneráveis (1) e benignas (0) há em cada arquivo
e compara com os números do artigo do PrimeVul (Ding et al., ICSE 2025), para você conferir
que baixou a coisa certa.

Uso:
  python 00_baixar_primevul.py                 # via Hugging Face (recomendado)
  python 00_baixar_primevul.py --fonte drive   # via Google Drive oficial
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

PASTA_DADOS = Path("../dados")

# Números do artigo (Tabela III do PrimeVul) — servem só como referência para conferir.
ESPERADO = {
    "primevul_train.jsonl":        {"1": 5574, "0": 178853},
    "primevul_valid.jsonl":        {"1": 699,  "0": 24731},
    "primevul_test.jsonl":         {"1": 695,  "0": 25216},
    "primevul_train_paired.jsonl": {"1": 4354, "0": 4354},
    "primevul_valid_paired.jsonl": {"1": 562,  "0": 562},
    "primevul_test_paired.jsonl":  {"1": 564,  "0": 564},
}

# Pasta oficial (v0.1) no Google Drive, conforme o README do DLVulDet/PrimeVul.
DRIVE_V01 = "https://drive.google.com/drive/folders/1cznxGme5o6A_9tT8T47JUh3MPEpRYiKK"


def baixar_via_huggingface():
    """Baixa os subsets 'default' e 'paired' do espelho colin/PrimeVul e grava em JSONL."""
    try:
        from datasets import load_dataset
    except ImportError:
        sys.exit("[ERRO] Falta a biblioteca 'datasets'. Rode: pip install datasets")

    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    nome_split = {"train": "train", "validation": "valid", "test": "test"}

    for subset, sufixo in (("default", ""), ("paired", "_paired")):
        print(f"\n== Baixando subset '{subset}' de colin/PrimeVul ==")
        ds = load_dataset("colin/PrimeVul", subset)
        for split in ds.keys():
            curto = nome_split.get(split, split)
            destino = PASTA_DADOS / f"primevul_{curto}{sufixo}.jsonl"
            with destino.open("w", encoding="utf-8") as f:
                for linha in ds[split]:
                    f.write(json.dumps(linha, ensure_ascii=False) + "\n")
            print(f"  gravado {destino.name}: {len(ds[split])} linhas")


def baixar_via_drive():
    """Baixa a pasta oficial do Google Drive com gdown (pode falhar por cota do Drive)."""
    try:
        import gdown  # noqa: F401
    except ImportError:
        print("Instalando gdown...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "gdown"])
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    print(f"\n== Baixando a pasta oficial v0.1 do Google Drive ==\n{DRIVE_V01}")
    subprocess.check_call([sys.executable, "-m", "gdown", "--folder", DRIVE_V01,
                           "-O", str(PASTA_DADOS)])
    print("\nSe o download falhar por 'quota exceeded', baixe pelo navegador e coloque os "
          f".jsonl em {PASTA_DADOS.resolve()} — ou use a fonte Hugging Face (padrão).")


def conferir():
    """Conta os rótulos de cada arquivo e compara com o artigo."""
    print("\n================ CONFERÊNCIA ================")
    for nome, esperado in ESPERADO.items():
        caminho = PASTA_DADOS / nome
        if not caminho.exists():
            print(f"  {nome}: (não encontrado)")
            continue
        cont = Counter()
        with caminho.open("r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    cont[str(int(json.loads(linha)["target"]))] += 1
        ok = (cont.get("1", 0) == esperado["1"] and cont.get("0", 0) == esperado["0"])
        marca = "OK" if ok else "diferente do artigo"
        print(f"  {nome}: vuln={cont.get('1', 0)}  benignas={cont.get('0', 0)}  "
              f"(artigo: {esperado['1']}/{esperado['0']}) -> {marca}")
    print("\nSe algum total ficar 'diferente do artigo', não é necessariamente erro: o espelho pode "
          "ser da release v0.1 (atualizada). Anote a diferença na planilha, na coluna 'observacoes'.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonte", choices=["hf", "drive"], default="hf",
                    help="hf = Hugging Face (padrão); drive = pasta oficial no Google Drive")
    ap.add_argument("--so_conferir", action="store_true",
                    help="não baixa nada; só conta os rótulos dos arquivos já em ../dados/")
    args = ap.parse_args()

    if not args.so_conferir:
        if args.fonte == "hf":
            baixar_via_huggingface()
        else:
            baixar_via_drive()
    conferir()
    print(f"\nPronto. Próximo passo: python 02_ver_dados.py")


if __name__ == "__main__":
    main()
