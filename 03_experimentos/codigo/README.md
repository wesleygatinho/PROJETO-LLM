# Código dos experimentos

## Rotina de cada sessão (o pod é apagado no fim e recriado na próxima)

Crie o pod sempre igual: **1× A40 48 GB** e **o mesmo template PyTorch**.

1. Baixe o repositório no pod (`git clone`) e entre em `03_experimentos/codigo`.
2. `bash 01_setup_runpod.sh` instala as bibliotecas nas **versões travadas**, faz login no Hugging Face e confere a GPU.
3. `python 00_baixar_primevul.py` baixa o PrimeVul de novo (os dados não vão para o Git).
4. Rode os experimentos.
5. Antes de apagar o pod: `git add`, `git commit` e `git push` dos resultados e logs. Na Etapa 3, confira também se o adaptador foi para o Hugging Face.

## O que cada arquivo faz

| Arquivo | Para que serve |
|---|---|
| `01_setup_runpod.sh` | Prepara o pod. Na primeira vez cria a trava de versões; nas seguintes, instala exatamente o que está nela. |
| `ambiente.py` | A trava. Grava e confere versões das bibliotecas, do torch e a GPU oficial. Quem chama é o setup. |
| `requisitos_travados.txt` | Criado na primeira sessão com trava. **Vai para o Git.** Não edite à mão. |
| `00_baixar_primevul.py` | Baixa o PrimeVul para `../dados/` (padrão: espelho do Hugging Face; `--fonte drive` para a pasta oficial) e confere os totais. |
| `02_ver_dados.py` | Mostra o formato dos dados (colunas, exemplos, quantos de cada rótulo). |
| `03_inferencia_etapa1.py` | Etapa 1: o modelo responde YES/NO, o script mede acertos, memória, tempo e custo e grava uma linha na planilha. |
| `04_metricas_pareadas.py` | Depois do 03 rodado no arquivo pareado: calcula P-C, P-V, P-B e P-R. |
| `05_comparar_logs.py` | Compara duas rodadas função por função (Etapa 1 ou Etapa 3). Diz se as respostas são idênticas. |
| `06_treinar_qlora.py` | Etapa 3: treina o adaptador QLoRA + cabeça de classificação no PrimeVul-train. |
| `07_avaliar_classificador.py` | Etapa 3: avalia um adaptador na validação, no teste e no pareado (F1, AUC, VD-S, P-C). |
| `08_baseline_tamanho.py` | O baseline burro: só o tamanho da função. Sem GPU, sem modelo. É o piso das tabelas. |
| `classificador.py` | Peças comuns do 06, 07 e 08 (carregar modelo, notas, VD-S, pareado). Não é para rodar sozinho. |

(Os números nos nomes são só identificadores; a ordem de uso é a da rotina acima.)

## Quando uma linha vale como resultado oficial

- Rodou na **A40**.
- A coluna `ambiente_confere` da planilha diz **sim**. Se o pod fugir da trava, o script avisa em destaque antes de carregar o modelo.
- Teste rápido em outra placa pode, mas a linha não entra nas tabelas da dissertação.
- Na Etapa 3, a coluna `depuracao` diz **nao**.
- Rodada descartada: o log vai para `../logs/descartados/`, com o motivo e as linhas removidas no `LEIA.md` de lá.

## Etapa 3 — QLoRA + cabeça de classificação

### Uma vez só: pôr peft e bitsandbytes na trava

No primeiro pod da Etapa 3, depois do `01_setup_runpod.sh`:

```bash
pip install -c requisitos_travados.txt peft bitsandbytes
python ambiente.py --travar --refazer
git diff requisitos_travados.txt
```

O `-c` impede que o pip troque as versões já travadas (transformers etc.) ao instalar as novas.
No `git diff`, só podem aparecer **duas linhas novas** (peft e bitsandbytes). Se outra linha mudou,
as rodadas da Etapa 1 deixam de ser reproduzíveis nesse ambiente: pare e refaça o teste do
`05_comparar_logs.py` no pareado do 3B antes de seguir. Depois: commit + push da trava.

### Regras

- Modelo **Base** (`Qwen/Qwen2.5-Coder-3B`, `Qwen/Qwen2.5-Coder-7B`), não Instruct (protocolo §2).
- O **teste nunca decide nada**: o limiar do VD-S sai da validação e a melhor época sai do **pareado da validação**
  (`primevul_valid_paired.jsonl`). Não use a AUC para escolher: no PrimeVul as vulneráveis são muito mais longas
  (922 tokens contra 297), e só o tamanho da função já dá AUC 0,82 no teste — escolher pela AUC premia esse atalho.
- Seeds oficiais: **1, 2 e 3** (protocolo §6).
- A mesma rodada treina e avalia com o mesmo `max_tokens` (o 07 lê da receita do 06).
- O pod é apagado: use `--repo_hf SEU_USUARIO/etapa3-adaptadores` (repositório **privado**) ou avalie antes de apagar.

### Depuração (primeira sessão, poucos minutos)

```bash
python 06_treinar_qlora.py --benignas_por_vul 1 --limite_treino 400 --preco_hora 0.50
python 07_avaliar_classificador.py --rodada ../adapters/NOME_QUE_O_06_IMPRIMIU --limite 400 --preco_hora 0.50
```

Os números da depuração não valem nada; ela serve para ver o fluxo inteiro rodar e para ler os
**tokens/s** que o 06 imprime (é deles que sai o tempo real de uma época completa).

### Rodada completa

A proporção de benignas (`real` ou um número `k`) e o número de épocas ainda vão ser fixados num piloto
com o 3B, comparado pelo **pareado da validação**. O exemplo abaixo usa `real`.

```bash
python 06_treinar_qlora.py --modelo Qwen/Qwen2.5-Coder-7B --benignas_por_vul real --epocas 1 --seed 1 --preco_hora 0.50 --repo_hf SEU_USUARIO/etapa3-adaptadores
python 07_avaliar_classificador.py --rodada hf:SEU_USUARIO/etapa3-adaptadores/NOME --variante nf4 --preco_hora 0.50
python 07_avaliar_classificador.py --rodada hf:SEU_USUARIO/etapa3-adaptadores/NOME --variante bf16 --preco_hora 0.50
```

- `nf4` = base em 4 bits + adaptador (o modelo como foi treinado). `bf16` = adaptador mesclado num base de 16 bits
  (a referência de onde sairão as variantes AWQ/GPTQ/NF4 da RQ2). A Etapa 1 usou float16 para gerar texto; aqui o
  16 bits é bfloat16, o tipo nativo do Qwen2.5 e o mesmo do treino.
- Tempo e memória do 07 são indicativos (transformers, em lotes; não comparáveis ao tempo por função da Etapa 1).
  O custo oficial da curva será medido com o vLLM, na etapa de quantização.

### Piloto do 3B: decidir a proporção de benignas (uma sessão de ~14 h, ~US$ 7)

Pergunta do piloto: **treinar com todas as benignas (~1:35) rende mais que 1 benigna por vulnerável?**
Quem responde é o **pareado da validação**. O teste não entra nesta decisão.

1. Trava e dados (ver a seção acima), depois um teste de 4 min do fluxo já com a checagem pareada:

```bash
python 06_treinar_qlora.py --benignas_por_vul 1 --limite_treino 400 --preco_hora 0.50
```

2. O baseline do tamanho (CPU, ~5 min) — é o piso da tabela:

```bash
python 08_baseline_tamanho.py --observacoes "piloto 3B: baseline do tamanho"
```

3. Os dois treinos, um atrás do outro, em segundo plano. O `nohup` é o que impede o treino de morrer
   quando o terminal do RunPod fecha; o `&&` faz o segundo só começar se o primeiro terminar bem:

```bash
nohup bash -c "python 06_treinar_qlora.py --benignas_por_vul 1 --epocas 3 --seed 1 --preco_hora 0.50 --repo_hf SEU_USUARIO/etapa3-adaptadores --observacoes 'piloto 3B 1:1' && python 06_treinar_qlora.py --benignas_por_vul real --epocas 1 --seed 1 --preco_hora 0.50 --repo_hf SEU_USUARIO/etapa3-adaptadores --observacoes 'piloto 3B proporcao real'" > ../logs/piloto_3b.out 2>&1 &
```

Acompanhe com `tail -f ../logs/piloto_3b.out`. Tempos esperados (medidos na depuração, 1.523 tokens/s):
1:1 com 3 épocas ≈ 3,3 h; proporção real com 1 época ≈ 10,2 h. A cada 2.000 passos o script salva um
adaptador `parcial`, para uma queda do pod não zerar a rodada.

4. A decisão, lendo `../resultados/treinos_etapa3.csv` (colunas `pareado_val_melhor_pct` e `pareado_val_margem_acaso`):

- proporção real ganha do 1:1 por **mais** que a margem do acaso → o 7B usa `real` e paga as ~23 h/época;
- diferença **dentro** da margem → o 7B usa `1:1`, e o piloto vira uma ablação para a dissertação
  ("a proporção de treino não muda o resultado pareado"), que é o que economiza dias de pod;
- as duas abaixo de 50% + margem → é o cenário-base do protocolo (§11): resultado, não fracasso.

Anote a decisão **antes** de rodar o `07`. Só depois avalie no teste (US$ 0,25 por variante).

### O baseline do tamanho (rode uma vez, antes de comparar qualquer modelo)

```bash
python 08_baseline_tamanho.py
```

Não usa GPU nem modelo treinado: ele só mede o tamanho da função e segue o mesmo protocolo (limiar escolhido na
validação, VD-S, pareado). Serve de piso para toda tabela: **um modelo de 7B só compensa se ganhar disto.**
No teste desbalanceado ele vai bem (o artefato do tamanho); no pareado ele desmorona, porque a versão corrigida
costuma ser a maior — o conserto acrescenta código. `--medida linhas` ou `--medida caracteres` dispensa o tokenizer.

## Onde ficam as coisas

- dados baixados → `../dados/` (não vai para o Git)
- resultados → `../resultados/resultados_etapa1.csv` e `../resultados/resultados_pareado.csv` (uma linha por rodada)
- Etapa 3 → `../resultados/treinos_etapa3.csv` (um treino por linha) e `../resultados/resultados_etapa3.csv` (uma avaliação por linha)
- adaptadores treinados → `../adapters/` (não vai para o Git; guarde no Hugging Face)
- respostas cruas do modelo, função por função → `../logs/` (na Etapa 3: notas por função, receita do treino e perda por passo)
- leitura dos resultados → `../resultados/NOTAS_etapa1.md`
