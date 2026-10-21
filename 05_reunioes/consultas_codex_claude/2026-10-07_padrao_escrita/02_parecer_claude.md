# Parecer bruto do Claude — consultar decisão integrada

Modelo: claude-opus-5-5. Sugestões abaixo podem ter sido revistas na integração.

---

Li os quatro documentos inteiros e conferi trechos de A09, A10 e A11 e o `PLANO_EXECUCAO.md`. Não abri os PDFs nem o `A12_colunas.txt`.

## Ajustes do Codex

**Aceito os sete.**
- **1 a 3:** corrigem regras que eu tinha transformado em fórmula, sem apoio no corpus. Isso já está registrado em `ANALISE_CORPUS.md:55`.
- **4:** "categorias pareadas" é melhor que "noções pareadas", porque nomeia os desfechos de decisão.
- **5:** a formulação de `PADRAO_ESCRITA.md:72` está correta: essas palavras não são proibidas, desde que a comparação numérica e as condições as sustentem.
- **6:** retiro a suposta divergência. O limite de 10 linhas renderizadas está correto.
- **7:** de acordo.

## Correções indispensáveis

1. **A amostra contradiz o próprio guia sobre referentes** (`AMOSTRA_REDACAO.md:5`). Em "Essa avaliação permite examinar aspectos distintos", "essa avaliação" pode ser a pareada ou o conjunto das duas. É o caso que `PADRAO_ESCRITA.md:24` manda revisar. Sugestão: "A leitura conjunta dessas duas perspectivas permite…".

2. **A amostra descreve as receitas de forma incompleta** (`AMOSTRA_REDACAO.md:7`). O `PLANO_EXECUCAO.md:27-28` define o terceiro braço do 3B e o 7B como "**1:1 com controle de tamanho**". A amostra diz apenas "amostragem com controle de tamanho" e "a receita com controle de tamanho". Lida isoladamente, sugere uma receita sem balanceamento 1:1.

3. **A ressalva aponta para o fator errado** (`AMOSTRA_REDACAO.md:7`). "Sem atribuí-las … ao tamanho do modelo" encerra um período sobre diferenças *entre receitas do 3B*, em que o tamanho do modelo é constante. A ressalva sobre escala cabe na comparação 3B×7B (`PLANO_EXECUCAO.md:47`).

4. **A ressalva sobre épocas é genérica demais** (mesma linha). "Os braços do 3B também diferem no volume de treinamento e no número de épocas" sugere que todos diferem entre si. Pelo `PLANO_EXECUCAO.md:26`, é o braço com proporção real que tem uma época e orçamento distinto. É melhor nomeá-lo.

5. **A afirmação sobre páginas não declara a verificação parcial** (`ANALISE_CORPUS.md:3`). O texto afirma "Páginas abaixo são as páginas físicas do PDF", mas a conferência visual cobriu só as primeiras páginas dos 12 e páginas internas de A01, A08 e A12. As demais localizações herdaram meus marcadores de extração. Basta acrescentar uma frase dizendo isso. Também vale citar o `A12_colunas.txt` como a fonte das páginas de A12.

## Sugestões

- **Concordância** (`PADRAO_ESCRITA.md:87`): "FPR observado" → "FPR observada", pois é a *taxa*. O plano usa o masculino; basta escolher uma forma e mantê-la.
- **Escopo da memória e do tempo** (`PADRAO_ESCRITA.md:89-90`): convém acrescentar "na GPU e no ambiente medidos", em coerência com `README.md`.
- **Futuro na amostra** (`AMOSTRA_REDACAO.md:9`): "serão descritas" está justificado na linha 15. Mesmo assim, uma marcação inline (p.ex. "[ajustar ao estado final]") reduz o risco de o trecho ser copiado sem revisão.
- **Fonte para A04/A11 em desenvolvimento** (`ANALISE_CORPUS.md:45`): convém citar A04 p.14 e a seção "3. Resultados Preliminares" de A11 (conferida em `A11.txt:138`).
- **Primeira pessoa no corpus** (`ANALISE_CORPUS.md:33`): A09 e A11 usam "podemos" e "propomos" também em interpretação e proposta, não só em decisões (`A09.txt:352`, `A11.txt:61,150`). Trocar "principalmente para apresentar decisões" por "em decisões, propostas e interpretações".
- **Sequência de revisão** (`PADRAO_ESCRITA.md:104`): está boa. Sugiro marcar no checklist quais itens dependem da consolidação P2, como política de limiar, FPR/FNR e meio crédito, para não serem marcados antes dela.

## Consistência entre os documentos

- Os links relativos entre `PADRAO_ESCRITA.md` e `ANALISE_CORPUS.md` resolvem corretamente.
- A terminologia (validação/dev, P-C × ordenação, NF4/BF16 sem PTQ) está alinhada ao `PLANO_EXECUCAO.md:45-47,75`.
- O `README.md` do template evita corretamente afirmar que essa é a versão vigente da SBC e que houve compilação.

## Limites desta verificação

- Não conferi visualmente nenhum PDF nem os hashes do `.sty`/`.bst`. Aceito como relato do Codex que as cópias são idênticas por hash.
- Não li `SBC_PDF.txt` inteiro nem `A12_colunas.txt`.
- Os fatos da amostra foram comparados só com `PLANO_EXECUCAO.md`, não com logs nem planilhas.
- Nada aqui certifica resultados científicos.
