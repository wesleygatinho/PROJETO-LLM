# Código dos experimentos — Etapa 1 (primeira sessão no RunPod)

Ordem de uso (uma coisa de cada vez):

1. `01_setup_runpod.sh` — rode no terminal do pod, uma vez, para instalar as bibliotecas e entrar no Hugging Face.
2. `02_ver_dados.py` — abre o PrimeVul e mostra o formato (colunas, exemplos, quantos de cada rótulo). Serve para você **entender** os dados antes de rodar.
3. `03_inferencia_etapa1.py` — o experimento em si: o modelo responde SIM/NÃO para N funções, o script conta os acertos, mede memória/tempo/custo e grava uma linha no CSV de resultados.

Onde ficam as coisas:
- dados baixados → `../dados/` (não vai para o Git)
- resultados → `../resultados/resultados_etapa1.csv` (uma linha por rodada)
- saídas detalhadas (a resposta crua do modelo para cada função) → `../logs/`

Primeira rodada recomendada: `python 03_inferencia_etapa1.py --n 50`
(50 funções = rápido, barato, e já mostra se o parsing das respostas está certo.)
