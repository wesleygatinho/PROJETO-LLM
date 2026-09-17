#!/usr/bin/env bash
# Setup de cada sessão no RunPod: rode no terminal do pod SEMPRE que criar um pod novo.
#
# Pod (sempre igual, para os resultados serem comparáveis):
#   - GPU: 1x NVIDIA A40 48 GB  (placa oficial do trabalho)
#   - Template: PyTorch, sempre o mesmo  (a versão do torch vem do template e está travada)
set -e
cd "$(dirname "$0")"   # roda de dentro de 03_experimentos/codigo, venha de onde vier

echo "== 1) Bibliotecas =="
pip install --upgrade pip
if [ -f requisitos_travados.txt ]; then
    echo "Encontrei requisitos_travados.txt: instalando as versões TRAVADAS."
    python ambiente.py --conferir_torch      # para aqui se o template do pod trouxer outro torch
    pip install -r requisitos_travados.txt
else
    echo "Primeira vez: instalando as versões atuais e criando a trava."
    pip install transformers accelerate datasets scikit-learn pandas tqdm huggingface_hub gdown
    python ambiente.py --travar
    echo
    echo ">>> IMPORTANTE: faça commit + push de requisitos_travados.txt antes de apagar este pod. <<<"
    echo
fi

echo "== 2) Login no Hugging Face (cole o seu token quando pedir; ele NÃO fica no código) =="
hf auth login

echo "== 3) Pastas de trabalho =="
mkdir -p ../dados ../resultados ../logs

echo "== 4) Conferir GPU e ambiente =="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
python ambiente.py

echo
echo "Pronto. Próximo passo: python 00_baixar_primevul.py   (os dados não ficam no Git; baixe a cada pod novo)"
echo "Lembrete: antes de apagar o pod, faça commit + push dos resultados e logs."
