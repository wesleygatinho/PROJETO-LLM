# Código dos experimentos

## Rotina de cada sessão (o pod é apagado no fim e recriado na próxima)

Crie o pod sempre igual: **1× A40 48 GB** e **o mesmo template PyTorch**.

1. Baixe o repositório no pod (`git clone`) e entre em `03_experimentos/codigo`.
2. `bash 01_setup_runpod.sh` instala as bibliotecas nas **versões travadas**, faz login no Hugging Face e confere a GPU.
3. `python 00_baixar_primevul.py` baixa o PrimeVul de novo (os dados não vão para o Git).
4. Rode os experimentos.
5. Antes de apagar o pod: `git add`, `git commit` e `git push` dos resultados e logs.

## O que cada arquivo faz

| Arquivo | Para que serve |
|---|---|
| `01_setup_runpod.sh` | Prepara o pod. Na primeira vez cria a trava de versões; nas seguintes, instala exatamente o que está nela. |
| `ambiente.py` | A trava. Grava e confere versões das bibliotecas, do torch e a GPU oficial. Quem chama é o setup. |
| `requisitos_travados.txt` | Criado na primeira sessão com trava. **Vai para o Git.** Não edite à mão. |
| `00_baixar_primevul.py` | Baixa o PrimeVul para `../dados/` (padrão: espelho do Hugging Face; `--fonte drive` para a pasta oficial) e confere os totais. |
| `02_ver_dados.py` | Mostra o formato dos dados (colunas, exemplos, quantos de cada rótulo). |
| `03_inferencia_etapa1.py` | O experimento: o modelo responde YES/NO, o script mede acertos, memória, tempo e custo e grava uma linha na planilha. |
| `04_metricas_pareadas.py` | Depois do 03 rodado no arquivo pareado: calcula P-C, P-V, P-B e P-R. |
| `05_comparar_logs.py` | Compara duas rodadas função por função. Diz se as respostas são idênticas. |

(Os números nos nomes são só identificadores; a ordem de uso é a da rotina acima.)

## Quando uma linha vale como resultado oficial

- Rodou na **A40**.
- A coluna `ambiente_confere` da planilha diz **sim**. Se o pod fugir da trava, o script avisa em destaque antes de carregar o modelo.
- Teste rápido em outra placa pode, mas a linha não entra nas tabelas da dissertação.
- Rodada descartada: o log vai para `../logs/descartados/`, com o motivo e as linhas removidas no `LEIA.md` de lá.

Quando chegar a etapa do QLoRA e instalar biblioteca nova:
`pip install peft bitsandbytes` e depois `python ambiente.py --travar --refazer` (e commit da trava).

## Onde ficam as coisas

- dados baixados → `../dados/` (não vai para o Git)
- resultados → `../resultados/resultados_etapa1.csv` e `../resultados/resultados_pareado.csv` (uma linha por rodada)
- respostas cruas do modelo, função por função → `../logs/`
- leitura dos resultados → `../resultados/NOTAS_etapa1.md`
