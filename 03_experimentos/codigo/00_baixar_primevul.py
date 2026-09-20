"""
00_baixar_primevul.py — Baixa o PrimeVul para ../dados/ com os nomes de arquivo oficiais.

ATENÇÃO — existem DUAS releases do PrimeVul, e elas têm tamanhos diferentes:

  --release original  (padrão)  O conjunto usado no artigo (Ding et al., ICSE 2025, Tabela III):
                      teste com 25.911 funções (695 vulneráveis) e 564 pares. É esta que permite
                      comparar os nossos números com os do artigo e com o resto da literatura.
  --release v01       A "PrimeVul-v0.1" (set/2024), que acrescenta metadados mas, nas palavras do
                      README oficial, "only include vulnerabilities that we successfully retrieved
                      their metadata" — ou seja, é um SUBCONJUNTO: teste com 24.788 funções
                      (549 vulneráveis) e 435 pares. Perde 21% das vulneráveis do teste e 23% dos
                      pares, e a perda não é aleatória (sobram as que tinham CVE/CWE recuperáveis).

Fontes:
  --fonte drive  Pasta oficial dos autores no Google Drive (padrão da release original). Precisa de
                 `gdown`. Se o Drive recusar por cota, baixe pelo navegador e copie os .jsonl
                 para ../dados/ (ou espelhe uma vez num dataset PRIVADO seu no Hugging Face).
  --fonte hf     Espelho no Hugging Face. Só existe espelho confiável da v0.1 ("colin/PrimeVul",
                 idêntico a "ussooraj/PrimeVul" e "Andrefty/PrimeVul-v0.1-hf").

NÃO use o espelho "ASSERT-KTH/PrimeVul": ele tem as contagens da release original, mas a coluna
`is_vulnerable` está INVERTIDA (False para as 695 vulneráveis do teste, True para as 25.216 benignas).
Quem treinar com ele aprende a tarefa ao contrário.

No fim, o script conta as funções vulneráveis (1) e benignas (0) de cada arquivo e compara com os
números esperados DA RELEASE PEDIDA. Se não bater, ele avisa e termina com erro.

Uso:
  python 00_baixar_primevul.py                      # release do artigo, via Drive oficial
  python 00_baixar_primevul.py --release v01        # a v0.1, via espelho do Hugging Face
  python 00_baixar_primevul.py --so_conferir        # só confere o que já está em ../dados/
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

PASTA_DADOS = Path("../dados")

# Quantas funções vulneráveis (1) e benignas (0) cada arquivo deve ter, por release.
# "original" = Tabela III do artigo. "v01" = contagens medidas no espelho colin/PrimeVul (set/2026).
ESPERADO = {
    "original": {
        "primevul_train.jsonl":        {"1": 5574, "0": 178853},
        "primevul_valid.jsonl":        {"1": 699,  "0": 24731},
        "primevul_test.jsonl":         {"1": 695,  "0": 25216},
        "primevul_train_paired.jsonl": {"1": 4354, "0": 4354},
        "primevul_valid_paired.jsonl": {"1": 562,  "0": 562},
        "primevul_test_paired.jsonl":  {"1": 564,  "0": 564},
    },
    "v01": {
        "primevul_train.jsonl":        {"1": 4862, "0": 170935},
        "primevul_valid.jsonl":        {"1": 593,  "0": 23355},
        "primevul_test.jsonl":         {"1": 549,  "0": 24239},
        "primevul_train_paired.jsonl": {"1": 3789, "0": 3789},
        "primevul_valid_paired.jsonl": {"1": 480,  "0": 480},
        "primevul_test_paired.jsonl":  {"1": 435,  "0": 435},
    },
}

# Pastas oficiais no Google Drive, conforme o README do DLVulDet/PrimeVul.
DRIVE = {
    "original": "https://drive.google.com/drive/folders/19iLaNDS0z99N8kB_jBRTmDLehwZBolMY",
    "v01": "https://drive.google.com/drive/folders/1cznxGme5o6A_9tT8T47JUh3MPEpRYiKK",
}


def qual_release(caminho, n_linhas):
    """Diz de qual release é um arquivo, pelo nome e pelo número de linhas ('desconhecida' se não bater).
    Os outros scripts usam isto para gravar em cada linha da planilha em que dados ela foi calculada —
    é o que impede de comparar, sem perceber, um número da release original com um da v0.1."""
    alvo = Path(caminho).name
    for release, arquivos in ESPERADO.items():
        esperado = arquivos.get(alvo)
        if esperado and n_linhas == esperado["1"] + esperado["0"]:
            return release
    return "desconhecida"


def baixar_via_huggingface():
    """Baixa os subsets 'default' e 'paired' do espelho colin/PrimeVul (que é a release v0.1)."""
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


def baixar_via_drive(release, pasta=""):
    """Baixa uma pasta do Google Drive com gdown. Sem --pasta_drive, usa a pasta oficial dos autores
    (que pode falhar por cota); com ela, usa a sua cópia, que precisa estar compartilhada por link."""
    try:
        import gdown  # noqa: F401
    except ImportError:
        print("Instalando gdown...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "gdown"])
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    endereco = pasta or DRIVE[release]
    origem = "a SUA pasta" if pasta else "a pasta oficial dos autores"
    print(f"\n== Baixando a release '{release}' de {origem} no Google Drive ==\n{endereco}")
    subprocess.check_call([sys.executable, "-m", "gdown", "--folder", endereco,
                           "-O", str(PASTA_DADOS)])
    print("\nSe o download falhar por 'quota exceeded': baixe a pasta pelo navegador, copie os "
          f".jsonl para {PASTA_DADOS.resolve()} e rode: python 00_baixar_primevul.py --so_conferir")


def conferir(release):
    """Conta os rótulos de cada arquivo e compara com o esperado PARA A RELEASE PEDIDA.
    Devolve True só se os seis arquivos baterem."""
    print(f"\n================ CONFERÊNCIA (release: {release}) ================")
    tudo_ok, faltando = True, 0
    for nome, esperado in ESPERADO[release].items():
        caminho = PASTA_DADOS / nome
        if not caminho.exists():
            print(f"  {nome}: (não encontrado)")
            tudo_ok, faltando = False, faltando + 1
            continue
        cont = Counter()
        with caminho.open("r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    cont[str(int(json.loads(linha)["target"]))] += 1
        ok = (cont.get("1", 0) == esperado["1"] and cont.get("0", 0) == esperado["0"])
        tudo_ok = tudo_ok and ok
        print(f"  {nome}: vuln={cont.get('1', 0)}  benignas={cont.get('0', 0)}  "
              f"(esperado: {esperado['1']}/{esperado['0']}) -> {'OK' if ok else 'NÃO BATE'}")
    if tudo_ok:
        print(f"\nTudo certo: os seis arquivos são a release '{release}'.")
    else:
        outra = "v01" if release == "original" else "original"
        print("\n" + "!" * 72)
        print(f"[PARE] O que está em ../dados/ NÃO é a release '{release}'.")
        if not faltando:
            print(f"Talvez seja a outra release: confira com --release {outra} --so_conferir.")
        print("Misturar releases invalida a comparação entre as etapas. Resolva antes de treinar.")
        print("!" * 72)
    return tudo_ok


def main():
    ap = argparse.ArgumentParser(description="Baixa o PrimeVul e confere se é a release certa.")
    ap.add_argument("--release", choices=["original", "v01"], default="original",
                    help="original = o conjunto do artigo (padrão); v01 = o subconjunto com metadados")
    ap.add_argument("--fonte", choices=["hf", "drive"], default="",
                    help="drive = pasta oficial dos autores; hf = espelho (só existe para a v01)")
    ap.add_argument("--pasta_drive", default="",
                    help="baixa de OUTRA pasta do Drive (ex.: a sua própria cópia, compartilhada por link). "
                         "A conferência continua valendo: ela diz se o que veio é a release pedida.")
    ap.add_argument("--so_conferir", action="store_true",
                    help="não baixa nada; só conta os rótulos dos arquivos já em ../dados/")
    args = ap.parse_args()

    # Sem --fonte: Drive para a release do artigo, espelho do Hugging Face para a v0.1.
    fonte = args.fonte or ("drive" if args.release == "original" else "hf")
    if fonte == "hf" and args.release == "original":
        raise SystemExit("[ERRO] Não há espelho confiável da release original no Hugging Face "
                         "(o 'ASSERT-KTH/PrimeVul' tem o rótulo invertido). Use --fonte drive.")

    if not args.so_conferir:
        if fonte == "hf":
            baixar_via_huggingface()
        else:
            baixar_via_drive(args.release, args.pasta_drive)
    ok = conferir(args.release)
    print(f"\nPróximo passo: python 02_ver_dados.py")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
