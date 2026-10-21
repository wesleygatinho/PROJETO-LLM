# Parecer original do Claude — não substitui a decisão integrada

Modelo efetivo: claude-opus-5-5.

Sugestões e constatações abaixo devem ser lidas junto com o README deste registro e os documentos finais.

---

# Plano de consolidação e escrita: artigo de Seminários (PPGCC/UFMA, entrega e apresentação em 11/11/2026)

**Consulta somente leitura.** Não modifiquei arquivos, não executei comandos e não li `.env` nem credenciais. Pelo ambiente, o modelo desta consulta é o **Opus 5.5 (`claude-opus-5-5`)**. A identificação verificável é a que o CLI retorna. Este parecer não é validação científica.

---

## 0. O que conferi e o que mudou nas premissas

**Li:** o protocolo, o cronograma, o README do código, as NOTAS das etapas 1 e 3, os três CSVs de resultados e o CSV de treinos (todas as linhas), os scripts 04, 07, 08 e `classificador.py` inteiros, trechos do 06, 05 e 06 em parte, uma linha de cada formato de log, e o inventário de `02_referencias`.

**Não li:** os PDFs, os logs inteiros e `03_experimentos/dados/`, que localmente só tem `.gitkeep` (os dados do PrimeVul não estão na máquina). Não recalculei nenhum número.

### Constatações que mudam premissas

1. **A tolerância a falhas do `04` não afetou os dados gravados.** No `formar_pares` (`04_metricas_pareadas.py:42-52`), o arquivo do teste pareado tem 1.128 linhas, o que gera 564 tentativas de par. Todas as linhas dos CSVs registram `pares_avaliados=564` e `metodo_pareamento=consecutivos`, então nenhuma tentativa falhou. Na validação pareada (`n_funcoes: 1124` no `rodada.json`, `pareado_val_pares=562`) também não houve falha.
   - O risco que sobra é outro. A regra consecutiva só confere o `commit_id`. Um commit que mexe em várias funções pode juntar a vulnerável de uma função com a corrigida de outra. Isso precisa de auditoria por ID.
   - Também resta o descarte silencioso, que não aconteceu desta vez mas existe no código: o `continue` em `classificador.py:232` e no `04:85`.
   - O limite `len(dados)//20` dá 56 falhas toleradas sobre 564 tentativas, ou seja, ~10%, e não os 5% do comentário. A premissa do Codex está correta.

2. **O P-C não usa o mesmo limiar em todas as linhas.** O baseline do tamanho usa `limiar_decisao` (`08:98`). Os modelos usam `nota > 0` (`07:154`), e no treino 1:1 isso dá FPR de 27–34%. Por isso as categorias P-C/P-V/P-B/P-R da tabela atual não são comparáveis entre o baseline e os modelos.

3. **O VD-S = 1,000 do baseline é um artefato do corte em 2.048 tokens.** O CSV mostra `limiar_vds = 2048.0`: com muitas benignas no teto, a regra "nota > 2048" nunca dispara. O número tem que ser lido assim, e não como "o tamanho não acha nada".

4. **Etapa 1: "F1 no nível do acaso" e "P-C abaixo do acaso (25%)" não se sustentam.**
   - Faço a conta pelos CSVs, sem executar nada. A taxa de YES do 3B é 979/25.911 ≈ 3,8%. Um previsor aleatório com essa taxa teria F1 ≈ 2·0,027·0,038/(0,065) ≈ 0,03, e o 3B tem 0,12. No 7B, a referência fica em ≈ 0,04 contra 0,062 medidos.
   - O acaso do P-C depende da política de previsão. Com previsões independentes à taxa q, a referência é q(1−q), que fica ≈ 13% para q ≈ 15% no pareado. Com previsões correlacionadas dentro do par, ela cai para perto de 0.
   - O código também propaga o "25%" fixo, em `04:13` e `04:104`.

5. **Várias afirmações das NOTAS não têm código no repositório.** Uma busca no código por `mcnemar|bootstrap|binom|faixa|decil` não encontrou nenhum procedimento. Ficam sem reprodução:
   - o IC95% de 48,0–53,3;
   - os p-valores de McNemar (0,28/1,00/0,91) e as "73 a 87 trocas", sem evento binário declarado;
   - a "AUC dentro de faixas de tamanho";
   - a concordância entre seeds (58–61%), a correlação entre seeds (0,71–0,76) e a "média das três notas, 51,1%";
   - os quartis e os "26 acertos em comum" da Etapa 1.

   Cada uma precisa ser reproduzida por script ou retirada do texto.

6. **Comparações confundidas nas NOTAS:**
   - "Tirar o atalho piora todas as métricas" compara o 3B na proporção real com o 7B de mesmo tamanho, ou seja, muda o modelo e a receita ao mesmo tempo. A comparação limpa é entre as três receitas do 3B.
   - As receitas do 3B também não diferem só na proporção. O 1:1 treinou 3 épocas e a proporção real treinou 1 época, com volumes de dados diferentes.
   - "O 7B não é melhor que o 3B" compara 3 seeds com 1 seed. O texto deve dizer "não observamos diferença", nunca "equivalentes".

7. **As regras de decisão foram escritas para a métrica antiga.** A coluna de empates corrigida (`_ajust`) só apareceu em 06/out, depois dos resultados. Conferi no `treinos_etapa3.csv` que a melhor época não muda em nenhuma rodada (s1: 3/3; s2: 2/2; s3: 3/3; 3B mesmo tamanho: 3/3). O artigo deve relatar essa troca de critério de forma explícita.

8. **Os logs da validação pareada guardam só agregados por época,** não notas por função. Não dá para calcular incerteza por bootstrap na validação. Isso não é motivo para rodar de novo: as decisões ficam relatadas como foram registradas.

9. **O baseline não gravou log da validação.** Ele só tem os logs do teste e do pareado (`08:105`). Para conferir o limiar de 1.254 tokens é preciso reexecutar o `08`, que roda em CPU, depois de baixar os dados de novo.

10. **Protocolo §10 versus código.** O protocolo pede o "script oficial de avaliação pareada do PrimeVul", mas o projeto usa uma implementação própria. É preciso conferir a definição contra o artigo do PrimeVul (Ding et al.) ou declarar o desvio.

11. **Risco de novidade.** Há um PDF local de Huang et al., 2026 ("Do Fine-Tuned LLMs Understand Vulnerabilities? … Semantic Trap"). O trecho na linha 447 do markdown conclui que o ajuste fino "tend[s] to reinforce shortcut learning" e que a avaliação pareada é essencial. Isso se sobrepõe ao achado central. É leitura integral obrigatória antes de escrever qualquer contribuição.

12. **Fontes e documentos:**
   - Os markdowns de `02_referencias` vieram de OCR com `qwen2.5vl:7b`. Servem para busca, mas toda citação precisa ser conferida no PDF.
   - O `LEITURA_INTEGRAL_LOG.md` se contradiz: o "status final" diz que tudo foi verificado, e a lista de "Pendentes" continua lá.

---

## 1. Escopo, contribuição e perguntas (limitadas aos dados)

**Tipo de artigo:** estudo empírico exploratório. Usa só o bloco Qwen2.5-Coder já realizado, sem treinos obrigatórios novos. O roteiro da dissertação fica intacto, e a RQ2 completa (AWQ/GPTQ/INT8), o UniXcoder, a energia e a robustez continuam lá.

**Contribuições que os dados sustentam:**
- (a) Caracterizar como métricas não pareadas (F1 no limiar da validação, AUC, VD-S) e a ordenação pareada (empate vale meio acerto) podem divergir entre receitas de treino que expõem ou removem o atalho do tamanho. O baseline do tamanho entra como piso.
- (b) Mostrar a sensibilidade do resultado pareado à seed no 7B (n = 3), separada da incerteza amostral.
- (c) Comparar de forma descritiva NF4+adaptador e BF16 mesclado no eixo qualidade × recursos medidos no `transformers`.

**Perguntas:**

| ID | Pergunta | Base de dados | Natureza |
|---|---|---|---|
| Q1 | O ranking das configurações muda entre métricas não pareadas e a ordenação pareada? | Baseline, 3 receitas do 3B, 7B ×3 | Descritiva + IC por bootstrap |
| Q2 | No 3B, como as métricas se movem entre 1:1 sorteado, proporção real e 1:1 de mesmo tamanho? | 1 seed por receita | Descritiva; a receita vem confundida com seed e épocas |
| Q3 | Na receita de mesmo tamanho, que diferença se observa entre 7B e 3B? | 7B ×3 contra 3B ×1 | Descritiva; sem afirmar equivalência |
| Q4 | Quanto da variação pareada vem da seed e quanto da amostra de pares? | 7B ×3, logs por par | Inferencial limitada |
| Q5 | NF4+adaptador e BF16 mesclado diferem em qualidade e em memória/tempo? | 7B ×3, ambas as variantes | Descritiva + McNemar exato com evento declarado |
| Q0 | Qual é o piso do prompting zero-shot? | Etapa 1, 3B e 7B Instruct | Descritiva, com referência aleatória à mesma taxa de YES |

**O artigo não deve prometer:** a RQ2 completa, curva de Pareto ou "joelho", ausência de contaminação, equivalência a partir de não significância, generalização para outras famílias de modelo ou linguagens, nem custo "oficial" via vLLM.

---

## 2. Status: feito e pendente

| Item | Status | Evidência |
|---|---|---|
| Prompting 3B/7B (teste + pareado) | Feito | 4 linhas no `resultados_etapa1.csv` e 2 no `resultados_pareado.csv` |
| Baseline do tamanho | Feito, com ressalvas (VD-S no teto; sem log da validação) | `resultados_etapa3.csv`, linha 2 |
| Três receitas do 3B | Feito (1 seed cada) | `treinos_etapa3.csv`, linhas 3, 4 e 6; `resultados_etapa3.csv`, linhas 3–5 |
| 7B mesmo tamanho, 3 seeds, NF4 e BF16 | Feito | `resultados_etapa3.csv`, linhas 6–11 |
| Empates com meio crédito e F1 no limiar da validação | Gravados | Colunas `_ajust_pct` e `_limiar_validacao` |
| Auditoria dos pares por ID | Pendente | — |
| Recálculo das métricas a partir dos logs, conciliado com os CSVs | Pendente | — |
| P-C no mesmo limiar da validação para todos | Pendente | — |
| IC por bootstrap, McNemar exato, Holm | Pendente (sem código) | — |
| Reproduzir ou retirar as afirmações sem código (item 0.5) | Pendente | — |
| Conferir a definição do P-C contra o PrimeVul | Pendente | — |
| Leitura integral do núcleo e verificação de novidade | Pendente | — |
| Escrita, slides e revisão docente | Pendente | — |

---

## 3. Organização de pastas (só arquivos novos; nada é movido)

```
01_planejamento/artigo_seminarios_2026/
  00_LEIA.md                       índice e status
  01_escopo_perguntas.md           seção 1 deste plano
  02_inventario_proveniencia.md    mapa linha de CSV → log → commit
  03_plano_analise.md              eventos, bootstrap, famílias de teste (fechado ANTES de rodar a04)
  04_especificacao_scripts.md
  05_leitura_citacoes.md           fichamento com página do PDF
  06_roteiro_escrita.md
  07_cronograma_riscos.md
  08_registro_decisoes.md          afirmações das NOTAS: manter / reescrever / retirar
04_escrita/artigo/seminarios_2026/
  README.md   texto/   tabelas/   figuras/   referencias/ (só .bib, sem cópia de PDF)
  apresentacao/   revisao/ (pareceres recebidos, datados)
05_reunioes/2026-10-07_consulta_codex_claude_plano_artigo.md
03_experimentos/codigo/consolidacao_artigo/   (a01…a06, comum_artigo.py, testes/)
03_experimentos/resultados/artigo_seminarios_2026/   (CSVs derivados + manifesto)
```

**Como evitar duplicação:**
- Os CSVs derivados ficam só em `resultados/artigo_seminarios_2026`.
- Tabelas formatadas e figuras finais são geradas direto em `04_escrita/.../tabelas` e `figuras`, por script, com o commit de origem no rodapé ou no nome.
- As NOTAS antigas não são editadas. As correções ficam no `08_registro_decisoes.md`.

---

## 4. Sequência técnica (dependências e critérios verificáveis)

| # | Etapa | Depende de | Pronto quando |
|---|---|---|---|
| E1 | Inventário e proveniência (a01) | — | As 11 linhas do etapa3, 4 do etapa1 e 2 do pareado estão ligadas a logs existentes. O nº de linhas de cada log confere (25.911 / 1.128 / validação). O SHA-256 completo de cada log fica no manifesto. Nenhuma linha "órfã". |
| E2 | Auditoria dos 564 pares (a02) | E1 | Cada par tem `par_id`, as duas posições, os dois `idx`, `project`, `commit_id`, os alvos {1,0} e o `n_tokens`/`truncada` de cada lado. Os IDs são idênticos em todos os logs pareados. Qualquer divergência levanta exceção, sem fallback. Opcional, com os dados baixados de novo: SHA confere com `54a16a5ab663`, e a assinatura/nome da função é igual nos dois lados. |
| E3 | Recálculo e conciliação (a03) | E2 | F1, AUC, VD-S, `limiar_decisao`, `limiar_vds`, P-C/V/B/R, ordenados, empates e `corr_tamanho` recalculados dos logs conferem com o CSV até o arredondamento. Atenção: o log grava a nota com 5 casas (`classificador.py:147`), o que pode criar ou desfazer empates; a diferença é registrada. Os limiares vêm do log `_validacao` (não existe para o baseline; ver item 0.9). |
| E4 | Métrica pareada comparável (a03) | E3 | P-C/V/B/R recalculados para todos no `limiar_decisao` da validação, já gravado. O valor em `nota > 0` fica como histórico. Nada é escolhido no teste. |
| E5 | Plano de análise fechado | E3 | `03_plano_analise.md` versionado (commit) antes de rodar a04. |
| E6 | Incerteza e testes (a04) | E5 | ICs por bootstrap determinísticos (seed fixa, B declarado), McNemar exato, Holm. Testes unitários passando. |
| E7 | Descritivas (a05) | E3 | Cada afirmação do item 0.5 aparece como "reproduzida (valor)", "diverge (novo valor)" ou "retirada" no `08_registro_decisoes.md`. |
| E8 | Tabelas e figuras (a06) | E4, E6, E7 | Cada célula sai de um CSV derivado. Os números do texto não são digitados à mão. |

---

## 5. Métricas e estatística (para fechar no `03_plano_analise.md`)

**Duas fontes de variação, reportadas separadamente:**

1. **Incerteza amostral, condicionada aos modelos treinados.**
   - Bootstrap por **par** (564 pares) para a ordenação ajustada e as categorias P-*.
   - Bootstrap por **função**, estratificado por rótulo, para F1, AUC e VD-S. Os limiares ficam fixos, vindos da validação.
   - Diferenças entre configurações usam bootstrap pareado: as mesmas reamostragens nos dois braços.
   - Sensibilidade opcional: bootstrap por cluster de `commit_id`.
2. **Variação entre seeds (n = 3).**
   - Relatar os três valores, o intervalo e a média. Não apresentar IC t com n = 3 como estimativa precisa.
   - Para "média das 3 seeds", usar bootstrap por par aplicado às três seeds juntas. Esse IC é condicionado a estas três seeds e diz isso no texto.

**Notas sobre a ordenação pareada:**
- A referência de 50% vale sob simetria.
- A "margem de 4,1" do `06:117` supõe Bernoulli(0,5) sem empates; os empates reduzem a variância. No artigo, usar o bootstrap ou declarar a aproximação.

**McNemar exato:**
- Evento binário declarado: E = "nota da vulnerável estritamente maior que a da corrigida".
- O empate conta como não-E e não entra no meio crédito. O número de pares empatados em cada braço é relatado à parte.
- Discordantes: b = E só em A; c = E só em B. O p-valor é binomial bilateral exato sobre b + c.
- Família principal: NF4 × BF16 nas 3 seeds (3 testes, com Holm). Opcional: o evento P-C no limiar da validação.
- As comparações entre receitas e modelos ficam descritivas, com IC das diferenças. Se algum p-valor for relatado, entra numa família declarada com Holm.

**Controle de comparações múltiplas:**
- Declarar que todo o estudo é exploratório.
- As famílias e o Holm ficam fixados antes de rodar a04.
- Relatar o p-valor bruto e o ajustado.
- Usar linguagem de "observado/compatível com"; nunca "equivalente".

**Referências de acaso:**
- Para a ordenação: 50%.
- Para F1 e P-C do prompting: um previsor aleatório com a mesma taxa de YES. É a fórmula do item 0.4, e o texto deve declarar a independência que ela supõe.

**Truncamento e comparabilidade (vai explícito em Método e Ameaças):**
- A Etapa 1 cortou em 8.192 tokens (76 funções truncadas no teste, 38 no pareado) e usou o modelo Instruct em fp16, gerando texto.
- A Etapa 3 cortou em 2.048 tokens (649 truncadas no teste) e usou o modelo Base com cabeça de classificação, em bf16/nf4.
- Os empates nos pares vêm em boa parte do corte: as NOTAS dizem que 97 dos 124 pares de mesmo tamanho tinham as duas versões cortadas. A2 confirma isso pelos logs.
- Análise descritiva de sensibilidade, definida agora e não pelo teste: a ordenação restrita aos pares em que nenhum lado foi truncado.
- O baseline com `--max_tokens 0` (CPU) só entra como sensibilidade declarada do VD-S. Não substitui a linha principal.

**Recursos:**
- GPU-h de treino (`tempo_treino_s`), memória do modelo e de pico, e tempo por função no `transformers`.
- Os tempos da geração (Etapa 1) e da pontuação em lote (Etapa 3) ficam em colunas separadas, porque não são comparáveis entre si.
- Custo em US$ só como valor histórico, com data, GPU e preço/h registrados (0,50/h na época). Não estimar tarifas atuais.

---

## 6. Especificação dos scripts futuros (não executar agora)

Todos ficam em `codigo/consolidacao_artigo/`, leem só logs e CSVs (e, opcionalmente, os dados baixados de novo) e não usam GPU. Cada saída grava um manifesto com o commit, o SHA dos insumos e a data.

| Script | Entradas | Saídas | Testes úteis |
|---|---|---|---|
| `comum_artigo.py` | — | carregadores; `formar_pares_estrito()` (lança exceção em qualquer falha); ordenação ajustada; McNemar exato | — |
| `a01_inventario.py` | os 3 CSVs; `logs/` | `manifesto_rodadas.csv` | log ausente → erro; nº de linhas divergente → erro |
| `a02_auditar_pares.py` | logs pareados (Etapa 1 e 3, baseline); opcional `--dados` | `pares_teste_auditoria.csv` (564 linhas), `auditoria_pares.md` | par desalinhado sintético → exceção; `commit_id` diferente → exceção; IDs diferentes entre logs → exceção |
| `a03_recalcular.py` | logs + manifesto | `metricas_recalculadas.csv`, `conciliacao.csv` (CSV original × recalculado, com Δ) | caso pequeno calculado à mão; empate vale 0,5; limiar estritamente ">" |
| `a04_incerteza.py` | logs + `03_plano_analise.md` (parâmetros) | `ic_bootstrap.csv`, `mcnemar.csv` (b, c, p, p_Holm) | determinismo com a mesma seed; McNemar com b=0, c=5 contra o valor binomial conhecido; Holm contra um exemplo publicado |
| `a05_descritivas.py` | logs | `descritivas.csv` (concordância entre seeds, correlação NF4×BF16, AUC por faixa com definição escrita, subconjunto sem truncamento, F1 aleatório na mesma taxa) | definição de faixa idêntica para todos os braços |
| `a06_tabelas_figuras.py` | CSVs derivados | `04_escrita/.../tabelas/*`, `figuras/*` | toda célula rastreável à sua origem; falha se faltar insumo |

Fica fora dos scripts novos: corrigir o `04`/`classificador.py` (tolerância e `continue`). Se for feito, vai em commit separado, sem mudar os números históricos, e com `a03` mostrando que nada mudou.

---

## 7. Tabelas e figuras por seção

| Peça | Conteúdo | Seção |
|---|---|---|
| T1 | Release original: contagens, prevalência e truncamento a 2.048/8.192 | Método |
| T2 | Configurações: modelo, receita, épocas, época escolhida (critério antigo e ajustado), seeds, GPU-h | Método |
| T3 | Prompting: F1/P/R/FPR, taxa de YES, F1 aleatório na mesma taxa, P-C/V/B/R | Resultados (Q0) |
| T4 (central) | Baseline + 3 receitas do 3B + 7B s1–s3 + média: F1 no limiar da validação, AUC, VD-S (com nota do teto), ordenação ajustada [IC], empates, `corr_tamanho`, P-* no limiar da validação | Resultados (Q1–Q3) |
| T5 | NF4 × BF16 por seed: Δ das métricas, correlação das notas, McNemar (b, c, p, Holm), memória e tempo | Resultados (Q5) |
| F1 | AUC (não pareada) × ordenação pareada, por configuração, com IC | Resultados e Discussão (Q1) |
| F2 | Ordenação por seed: validação por época e teste, com a faixa de 50% | Resultados (Q4) |
| F3 (opcional) | Diferença de nota × diferença de tamanho nos pares (baseline × modelo) | Discussão |

---

## 8. Leitura e citações (fontes primárias locais)

**Núcleo (leitura integral no PDF, fichamento com página):**
- Ding 2024 (PrimeVul: definições de P-C e VD-S, releases);
- Risse & Böhme 2024;
- **Huang 2026 (Semantic Trap)**;
- Steenhoek 2024;
- Du 2025 (Vul-RAG/PairVul);
- Ouchebara 2025;
- Dettmers 2023 (QLoRA/NF4);
- Hu 2021 (LoRA);
- Hui 2024 (Qwen2.5-Coder).

**Secundário:** Ullah 2024, Chen 2023 (DiverseVul), Fan 2020, Chakraborty 2020, Li Z 2025 (IRIS), Kaniewski 2026, Shuzheng Gao 2025, Ahmed 2025, Li Y 2025.

**Faltam localmente:** fontes primárias de McNemar, bootstrap e Holm. O pesquisador precisa obtê-las; não citar de memória.

**Regras:**
- O markdown OCR serve só para localizar trechos. A citação é sempre conferida no PDF.
- O `.bib` é montado a partir do DOI ou da página da editora.

**Verificação de novidade:**
- Reaproveitar o `PROMPT_verificacao_originalidade.md` com as alegações reescritas. Saem C1, C2 e C4, porque não fazem parte deste artigo.
- A C5 é reescrita sem o "25%".
- Entra uma alegação nova: "o treino pareado por tamanho remove a dependência do tamanho, mas a ordenação fica perto de 50%". Ela é confrontada diretamente com Huang 2026 e Risse & Böhme.
- Registrar a data e as consultas usadas. A formulação no texto fica limitada às fontes consultadas até aquela data.
- Parecer de agente não conta como verificação.

---

## 9. Roteiro estrutural (sem estilo, idioma ou template)

1. **Resumo.**
2. **Introdução:** problema, por que avaliar em pares, Q0–Q5, contribuições delimitadas.
3. **Fundamentação e trabalhos relacionados:**
   - benchmarks e contaminação;
   - avaliação pareada e atalhos;
   - LLMs de código e PEFT/QLoRA;
   - quantização, só o necessário para NF4 × BF16.
4. **Método:**
   - dados e release;
   - modelos e revisões;
   - prompting;
   - classificador QLoRA e receitas;
   - seleção de época e limiares, só na validação, incluindo a troca para o critério ajustado;
   - métricas e baseline;
   - estatística;
   - ambiente e reprodutibilidade.
5. **Resultados:** Q0 → Q1/Q2 → Q3 → Q4 → Q5.
6. **Discussão:** o que cada métrica premia, implicações para a avaliação, leitura qualidade × recursos.
7. **Ameaças à validade:**
   - interna: 1 seed no 3B, receitas com épocas diferentes, seleção;
   - de construto: P-C × ordenação, empates, teto do VD-S;
   - externa: um dataset, uma família de modelos, C/C++;
   - de conclusão: n = 3, multiplicidade.
8. **Conclusão e ligação com a dissertação:** RQ2/PTQ, UniXcoder e robustez como trabalho futuro.
9. **Apêndice:** versões, hashes, comandos e custos históricos.

---

## 10. Cronograma (07/10 → 11/11; horas de trabalho ativo)

| Bloco | Horas | Janela |
|---|---|---|
| Fechar o plano e o padrão editorial (pesquisador) | 2 | 07–09/10 |
| a01–a03, E1–E4 | 9 | 08–14/10 |
| Plano de análise + a04 | 5 | 13–17/10 |
| a05 + registro de decisões | 6 | 15–19/10 |
| a06, tabelas e figuras v1 | 4 | 18–21/10 |
| Leitura do núcleo + verificação de novidade | 10 | 08–24/10, em paralelo |
| Escrita: Método e Resultados | 9 | 20–26/10 |
| Escrita: Fundamentação, Introdução, Discussão, Ameaças, Conclusão, Resumo | 11 | 25/10–31/10 |
| `.bib` e conferência das citações | 2 | 30–31/10 |
| **Rascunho completo para a docente** | — | **meta: 01/11** (pedir data; não presumir que a revisão já está marcada) |
| Incorporar a revisão (se chegar) | 4 | 04–08/11 |
| Slides e ensaio | 6 | 04–10/11 |
| Margem | 4 | 08–10/11 |
| **Total** | **~72 h** | |

**Isso não cabe em 10 h/semana.** De 07/10 a 10/11 há ~50 h disponíveis nesse ritmo. São duas saídas: subir para ~14 h/semana ou aplicar a versão enxuta abaixo, de ~50 h.

**Prioridades:**
- **Indispensável:** E1–E4, T4 com IC por bootstrap por par, T2, T3, F1, a reescrita das afirmações fortes, a leitura de Ding, Risse, Huang e Dettmers, o texto completo e os slides.
- **Opcional, cortado nesta ordem:**
  1. F3 e AUC por faixa (se cortadas, a afirmação correspondente sai do texto);
  2. as descritivas da Etapa 1 (quartis, acertos em comum);
  3. McNemar (ficam só b e c, de forma descritiva);
  4. o bootstrap por cluster;
  5. a leitura secundária;
  6. a redução da Fundamentação.

**Versão enxuta (~50 h):** a02 + a03 + a04 só com bootstrap por par, T2/T3/T4/T5 sem McNemar, F1, leitura de 4 fontes, revisão docente de 2 h e slides de 4 h.

---

## 11. Quando rodar de novo (somente se a evidência essencial não puder ser reconstruída)

**Rodar de novo só nestes casos:**
- Um log de uma linha da T4/T5 sumiu, está corrompido ou tem nº de linhas errado, **e** a métrica não pode ser recalculada. Nesse caso, reavaliar com o `07` a partir do adaptador no Hugging Face, na A40 com o ambiente travado. O histórico registra ~0,9 h (NF4) ou 0,7 h (BF16) de GPU por avaliação do 7B. Se o adaptador não estiver disponível, a configuração sai do artigo e isso é declarado.
- A conciliação a03 diverge além do arredondamento sem explicação. Primeiro, investigar o código. Rodar de novo só a avaliação daquela configuração.
- Conferir o limiar do baseline exige rodar o `08` de novo. É CPU, com novo download dos dados e mesmos argumentos.

**Parar sem rodar de novo:** se os dados baixados de novo tiverem SHA diferente de `7f0db8408bdd`/`54a16a5ab663`/`9fea452f1b7c`, registrar e não substituir nada.

**Não justificam rodar de novo:**
- IC largo ou falta de significância;
- vontade de ter mais seeds;
- o teto do VD-S do baseline;
- vontade de ter vLLM, AWQ ou GPTQ.

**Custo:** em GPU-h, com o valor em US$ calculado na hora pela tarifa vigente, sem estimativa agora.

---

## 12. Riscos e incompatibilidades com as premissas do Codex

| Risco | Mitigação |
|---|---|
| Huang 2026 antecipa o achado de atalho | Ler antes de escrever a Introdução. Posicionar o artigo como replicação ou extensão com treino pareado por tamanho e baseline explícito. |
| Afirmações das NOTAS sem código acabam no artigo | `08_registro_decisoes.md`: nada entra sem a04/a05. |
| Comparação 3B × 7B confundida pela seed | Relatar o intervalo do 7B (45,0–55,2% no teste) ao lado do valor único do 3B. |
| As receitas do 3B não isolam a proporção | Descrever como "receitas", não como "efeito da proporção". |
| P-C em limiares diferentes | E4. |
| Ordem "artigo depois da dissertação" (cronograma §4) | Este artigo é de disciplina e não substitui o M5. Registrar no `00_LEIA.md`. |
| Revisão docente sem data | Pedir a data na semana 1; se ela não vier, o plano segue sem esse bloco. |
| Carga acima de 10 h/semana | Seção 10. |

**Limites desta verificação:**
- Não abri PDFs nem logs inteiros e não executei nada.
- Os dados do PrimeVul não estão locais.
- Os valores citados aqui vêm dos CSVs e das NOTAS, e as contas do item 0.4 foram feitas à mão a partir dos CSVs.
- Não confirmei que o `06` usa o mesmo `formar_pares` na validação; vi o import (`06:54`), mas não li a chamada.

Nada disso garante aceitação ou avaliação favorável.
