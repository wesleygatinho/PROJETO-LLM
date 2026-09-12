# Código dos experimentos — Etapa 1 (primeira sessão no RunPod)

Ordem de uso (uma coisa de cada vez):

1. `01_setup_runpod.sh` - rode no terminal do pod, uma vez: instala as bibliotecas e faz login no Hugging Face.
2. `00_baixar_primevul.py` - baixa o PrimeVul para `../dados/` (padrao: espelho do Hugging Face; `--fonte drive` para a pasta oficial) e confere os totais contra o artigo.
3. `02_ver_dados.py` - abre o PrimeVul e mostra o formato (colunas, exemplos, quantos de cada rotulo). Serve para voce **entender** os dados antes de rodar.
4. `03_inferencia_etapa1.py` - o experimento em si: o modelo responde YES/NO para N funcoes, o script conta os acertos, mede memoria/tempo/custo e grava uma linha no CSV de resultados.

(Os numeros nos nomes dos arquivos sao so identificadores; a ordem de execucao e a desta lista.)

Onde ficam as coisas:
- dados baixados → `../dados/` (não vai para o Git)
- resultados → `../resultados/resultados_etapa1.csv` (uma linha por rodada)
- saídas detalhadas (a resposta crua do modelo para cada função) → `../logs/`

Primeira rodada recomendada: `python 03_inferencia_etapa1.py --n 50`
(50 funções = rápido, barato, e já mostra se o parsing das respostas está certo.)
