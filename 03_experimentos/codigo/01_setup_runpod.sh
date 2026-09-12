#!/usr/bin/env bash
# Setup da primeira sessão no RunPod — rode UMA vez no terminal do pod.
# Pré-requisito: pod criado com template "PyTorch" e 1 GPU de 24 GB (ex.: RTX 4090).
set -e

echo "== 1) Bibliotecas =="
pip install --upgrade pip
pip install "transformers>=4.44" "accelerate" "datasets" "scikit-learn" "pandas" "tqdm" "huggingface_hub"

echo "== 2) Login no Hugging Face (cole o seu token quando pedir; ele NÃO fica no código) =="
hf auth login

echo "== 3) Pastas de trabalho =="
mkdir -p ../dados ../resultados ../logs

echo "== 4) Conferir GPU =="
nvidia-smi --query-gpu=name,memory.total --format=csv

echo
echo "Pronto. Próximo passo: python 00_baixar_primevul.py   (depois: python 02_ver_dados.py)"
echo "Lembrete: ao terminar a sessão, DESLIGUE o pod para não gastar crédito."