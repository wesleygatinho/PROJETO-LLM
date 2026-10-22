#!/usr/bin/env bash
# Verificação da implementação no 3B (21/out/2026): o pareado no acaso seria culpa das nossas escolhas?
#   A) treino com pares: a benigna de cada vulnerável é a sua versão corrigida (lr padrão, 2e-4)
#   B) receita oficial (1:1 com benignas de mesmo tamanho) com lr 2e-5
#   C) receita oficial com lr 5e-5
# Todos: 3B, seed 1, 3 épocas. Cada treino é seguido da avaliação no teste (nf4).
# Um treino que falha não impede os seguintes.
# A leitura foi anotada ANTES de rodar, no fim de ../resultados/NOTAS_etapa3.md.
#
# Uso (de dentro de 03_experimentos/codigo, depois do setup e do 00_baixar_primevul.py):
#   nohup bash sessao_verificacao_3b.sh > ../logs/verificacao_3b.out 2>&1 &
cd "$(dirname "$0")"
PRECO=0.50
REPO=wesley2h/etapa3-adaptadores

rodar() {  # $1 = começo do nome da rodada, $2 = observação para a planilha; o resto vai para o 06
    local prefixo="$1" obs="$2"
    shift 2
    if python 06_treinar_qlora.py "$@" --epocas 3 --seed 1 --preco_hora "$PRECO" --repo_hf "$REPO" --observacoes "$obs"; then
        local r
        r=$(ls -d ../adapters/"${prefixo}"_s1_* | grep -v depuracao | tail -1)
        python 07_avaliar_classificador.py --rodada "$r" --preco_hora "$PRECO" --observacoes "$obs" \
            || echo "[ERRO] avaliação falhou: $obs (refaça depois a partir do Hugging Face)"
    else
        echo "[ERRO] treino falhou: $obs (seguindo para o próximo)"
    fi
}

rodar etapa3_Qwen2.5-Coder-3B_benpar          "verificacao 3B: treino com pares" --benignas_por_vul par
rodar etapa3_Qwen2.5-Coder-3B_ben1tam_lr2e-05 "verificacao 3B: lr 2e-5" --benignas_por_vul 1 --parear_tamanho --lr 2e-5
rodar etapa3_Qwen2.5-Coder-3B_ben1tam_lr5e-05 "verificacao 3B: lr 5e-5" --benignas_por_vul 1 --parear_tamanho --lr 5e-5
echo "FIM DA SESSÃO"
