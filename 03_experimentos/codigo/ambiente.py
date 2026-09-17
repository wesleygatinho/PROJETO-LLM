"""
ambiente.py — trava e confere as versões do ambiente (bibliotecas, torch e GPU).

Por que existe: o pod é apagado ao fim de cada sessão e recriado na seguinte. Sem trava, cada pod
novo instalaria a versão mais recente das bibliotecas, e uma versão nova pode mudar respostas
do modelo, do mesmo jeito que trocar de placa muda (ver ../logs/descartados/LEIA.md).
Com a trava, todo pod usa exatamente as mesmas versões e a mesma GPU oficial.

Quem chama este arquivo é o 01_setup_runpod.sh. Você só roda à mão para consultar:
  python ambiente.py                      # mostra o ambiente atual e compara com a trava
  python ambiente.py --travar             # 1ª vez: cria requisitos_travados.txt com as versões atuais
  python ambiente.py --conferir_torch     # para (erro) se o torch do template do pod for outro
  python ambiente.py --travar --refazer   # quando instalar biblioteca nova (ex.: peft, bitsandbytes)

O arquivo requisitos_travados.txt deve ir para o Git (commit + push logo depois de criado).
"""

import argparse
import platform
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path

ARQUIVO_TRAVA = Path(__file__).with_name("requisitos_travados.txt")
GPU_OFICIAL = "NVIDIA A40"

# Bibliotecas que entram na trava (as que não estiverem instaladas são ignoradas).
BIBLIOTECAS = [
    "transformers", "tokenizers", "accelerate", "safetensors", "huggingface_hub",
    "datasets", "scikit-learn", "numpy", "pandas", "tqdm", "gdown",
    "peft", "bitsandbytes",  # entram quando forem instaladas (etapa do QLoRA): rode --travar --refazer
]


def versao(pacote):
    try:
        return metadata.version(pacote)
    except metadata.PackageNotFoundError:
        return None


def ler_trava():
    """Devolve (bibliotecas, extras). bibliotecas = {nome: versão}; extras = {torch, cuda, gpu, python}."""
    libs, extras = {}, {}
    if not ARQUIVO_TRAVA.exists():
        return libs, extras
    for linha in ARQUIVO_TRAVA.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith("# trava:") and "=" in linha:
            chave, valor = linha[len("# trava:"):].split("=", 1)
            extras[chave.strip()] = valor.strip()
        elif linha and not linha.startswith("#") and "==" in linha:
            nome, v = linha.split("==", 1)
            libs[nome.strip()] = v.strip()
    return libs, extras


def descrever_ambiente():
    """Versões que vão para cada linha da planilha de resultados."""
    import torch
    return {
        "torch": torch.__version__,
        "cuda": torch.version.cuda or "",
        "transformers": versao("transformers") or "",
        "tokenizers": versao("tokenizers") or "",
    }


def conferir(gpu_atual=None):
    """Compara o pod atual com a trava. Devolve 'sim', 'nao' ou 'sem trava' (vai para a planilha)."""
    import torch
    libs, extras = ler_trava()
    if not libs:
        print("[AVISO] Não existe requisitos_travados.txt. Rode o 01_setup_runpod.sh antes de gerar resultados oficiais.")
        return "sem trava"
    diferencas = [f"{nome}: travado {v}, instalado {versao(nome)}"
                  for nome, v in libs.items() if versao(nome) != v]
    if extras.get("torch") and torch.__version__ != extras["torch"]:
        diferencas.append(f"torch: travado {extras['torch']}, instalado {torch.__version__}")
    if gpu_atual and extras.get("gpu") and gpu_atual != extras["gpu"]:
        diferencas.append(f"GPU: oficial {extras['gpu']}, este pod tem {gpu_atual}")
    if diferencas:
        print("\n" + "!" * 72)
        print("[ATENÇÃO] Este pod é DIFERENTE do ambiente travado.")
        print("Serve para teste e depuração, mas NÃO para resultado oficial:")
        for d in diferencas:
            print("  - " + d)
        print("!" * 72 + "\n")
        return "nao"
    print("Ambiente confere com a trava (bibliotecas, torch e GPU).")
    return "sim"


def travar(refazer=False):
    import torch
    if ARQUIVO_TRAVA.exists() and not refazer:
        sys.exit(f"[ERRO] {ARQUIVO_TRAVA.name} já existe. Para regravar (ex.: biblioteca nova), use --travar --refazer.")
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else ""
    linhas = [
        "# Versões travadas do ambiente dos experimentos. NÃO edite à mão.",
        f"# Gerado por ambiente.py em {datetime.now():%Y-%m-%d %H:%M}. O 01_setup_runpod.sh instala exatamente isto.",
        "# torch vem do template do pod (não é instalado por aqui); se o template for outro, o setup para.",
        f"# trava: torch={torch.__version__}",
        f"# trava: cuda={torch.version.cuda}",
        f"# trava: gpu={gpu}",
        f"# trava: python={platform.python_version()}",
        "",
    ]
    for nome in BIBLIOTECAS:
        v = versao(nome)
        if v:
            linhas.append(f"{nome}=={v}")
    ARQUIVO_TRAVA.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    print(f"\nTrava gravada em {ARQUIVO_TRAVA.name}. GPU oficial registrada: {gpu or '(nenhuma)'}")
    if gpu != GPU_OFICIAL:
        print(f"[ATENÇÃO] A GPU oficial do trabalho é a {GPU_OFICIAL}. Se este pod não tem essa placa, "
              f"apague o arquivo e trave num pod com ela.")
    print("Agora faça commit + push deste arquivo para que os próximos pods usem as mesmas versões.")


def conferir_torch():
    import torch
    _, extras = ler_trava()
    esperado = extras.get("torch")
    if esperado and torch.__version__ != esperado:
        sys.exit(f"\n[PARE] O torch deste pod é {torch.__version__}, mas o travado é {esperado}.\n"
                 f"Apague este pod e crie outro com o template PyTorch que traz o torch {esperado} "
                 f"(o nome do template mostra a versão).")
    if extras.get("gpu") and torch.cuda.is_available() and torch.cuda.get_device_name(0) != extras["gpu"]:
        print(f"[AVISO] GPU deste pod: {torch.cuda.get_device_name(0)}. GPU oficial: {extras['gpu']}. "
              f"Use só para teste.")
    print(f"torch confere com a trava ({torch.__version__}).")


def main():
    ap = argparse.ArgumentParser(description="Trava e confere o ambiente dos experimentos.")
    ap.add_argument("--travar", action="store_true", help="cria requisitos_travados.txt")
    ap.add_argument("--refazer", action="store_true", help="com --travar: regrava a trava existente")
    ap.add_argument("--conferir_torch", action="store_true", help="para se o torch do pod for outro")
    args = ap.parse_args()
    if args.travar:
        travar(refazer=args.refazer)
    elif args.conferir_torch:
        conferir_torch()
    else:
        import torch
        gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        print(descrever_ambiente(), "| GPU:", gpu)
        conferir(gpu)


if __name__ == "__main__":
    main()
