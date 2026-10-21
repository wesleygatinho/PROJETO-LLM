## 4. Resultados

### 4.1. Classificação por instrução

A Tabela 3 mostra como as variantes Instruct se comportaram com a instrução YES/NO, tanto no teste global quanto nos pares.

Tabela 3. Classificação por instrução no teste global (25.911 funções) e categorias no teste pareado (564 pares), pela decisão YES/NO. Contexto do código registrado: 8.192 tokens.

| Modelo | F1 | Precisão | Revocação | FPR (%) | P-C | P-V | P-B | P-R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3B Instruct | 0,119 | 0,102 | 0,144 | 3,49 | 16 | 67 | 463 | 18 |
| 7B Instruct | 0,062 | 0,038 | 0,160 | 11,00 | 14 | 78 | 454 | 18 |

O F1 foi baixo nas duas escalas, e o 7B ficou abaixo do 3B. A revocação um pouco maior do 7B, 0,160 contra 0,144, veio acompanhada de FPR de 11,00%, contra 3,49%, o que reduziu sua precisão a 0,038. Nos pares, a categoria P-B, em que as duas versões são declaradas não vulneráveis, reuniu 463 e 454 dos 564 casos, enquanto P-C ocorreu em 16 e 14 pares. Esses resultados descrevem a instrução e a regra de decisão utilizadas, e não todo o espaço de instruções possíveis.

### 4.2. Desempenho global e ordenação pareada

A Tabela 4 apresenta o desempenho global das configurações com escore, e a Tabela 5 mostra, para as mesmas configurações, as categorias pareadas e a ordenação. As duas tabelas devem ser lidas em conjunto, porque o contraste entre elas responde à primeira questão do estudo.

Tabela 4. Teste global, 25.911 funções. F1, precisão, revocação e FPR usam o limiar de maior F1 na validação. FNR* e FPR* usam outro limiar, calibrado para FPR ≤ 0,5% na validação; FPR* é o valor observado no teste. s1–s3 indicam as sementes do 7B.

| Configuração | F1 | Precisão | Revocação | FPR (%) | AUC | FNR* (%) | FPR* (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Heurística de comprimento | 0,200 | 0,152 | 0,294 | 4,53 | 0,810 | 100,00 | 0,00 |
| 3B 1:1 | 0,195 | 0,142 | 0,312 | 5,19 | 0,795 | 94,10 | 0,54 |
| 3B proporção original | 0,262 | 0,200 | 0,380 | 4,19 | 0,851 | 88,06 | 0,65 |
| 3B 1:1 + tamanho | 0,121 | 0,083 | 0,224 | 6,86 | 0,746 | 96,26 | 0,63 |
| 7B NF4 s1 | 0,114 | 0,077 | 0,222 | 7,36 | 0,738 | 97,99 | 0,69 |
| 7B BF16 s1 | 0,119 | 0,081 | 0,229 | 7,19 | 0,740 | 98,13 | 0,67 |
| 7B NF4 s2 | 0,142 | 0,103 | 0,229 | 5,47 | 0,726 | 98,71 | 0,38 |
| 7B BF16 s2 | 0,148 | 0,115 | 0,207 | 4,41 | 0,728 | 98,71 | 0,38 |
| 7B NF4 s3 | 0,127 | 0,084 | 0,258 | 7,75 | 0,765 | 98,27 | 0,56 |
| 7B BF16 s3 | 0,124 | 0,087 | 0,220 | 6,39 | 0,765 | 98,27 | 0,52 |

Tabela 5. Teste pareado oficial, 564 pares. As categorias usam o limiar de maior F1 na validação. Empates são pares com escores iguais nas duas versões. A ordenação dá meio crédito aos empates e independe de limiar; a coluna 465 considera apenas pares com as duas versões não truncadas.

| Configuração | P-C | P-V | P-B | P-R | Empates | Ord. 564 (%) | Ord. 465 (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Heurística de comprimento | 2 | 156 | 398 | 8 | 124 | 21,10 | 15,16 |
| 3B 1:1 | 13 | 155 | 372 | 24 | 52 | 42,38 | 39,03 |
| 3B proporção original | 6 | 200 | 344 | 14 | 43 | 37,50 | 34,09 |
| 3B 1:1 + tamanho | 6 | 120 | 422 | 16 | 37 | 49,20 | 48,71 |
| 7B NF4 s1 | 7 | 116 | 435 | 6 | 39 | 55,23 | 54,09 |
| 7B BF16 s1 | 6 | 125 | 425 | 8 | 39 | 53,28 | 51,94 |
| 7B NF4 s2 | 5 | 128 | 423 | 8 | 40 | 45,04 | 42,37 |
| 7B BF16 s2 | 7 | 113 | 434 | 10 | 34 | 44,68 | 41,94 |
| 7B NF4 s3 | 6 | 134 | 412 | 12 | 32 | 51,60 | 51,61 |
| 7B BF16 s3 | 8 | 113 | 434 | 9 | 32 | 51,95 | 52,04 |

O contraste mais nítido envolve a heurística de comprimento. Usando apenas o número de tokens, ela alcançou AUC global de 0,810 e F1 de 0,200, valores próximos aos do classificador 3B 1:1. A AUC indica que, no teste global, as funções vulneráveis tendem a ser mais longas que as não vulneráveis. Nos pares, porém, a ordenação pareada da mesma heurística foi de apenas 21,10%. Como esse valor está abaixo de 50%, a versão corrigida teve mais tokens visíveis que a vulnerável com mais frequência do que o inverso, entre os pares sem empate. Os 124 empates são pares em que as duas versões têm o mesmo número de tokens visíveis; entre eles estão necessariamente os pares cujas duas versões atingem o teto de 2.048 tokens e os 32 pares com entradas idênticas após o corte. Assim, a característica que separa as classes no teste global não separa, e tende a inverter, as duas versões de uma mesma correção.

Nas configurações 3B, os classificadores repetem esse contraste em menor grau. As duas de maior F1 e AUC na Tabela 4, a de proporção original (0,262 e 0,851) e a 1:1 (0,195 e 0,795), tiveram ordenações pareadas de 37,50% e 42,38%, abaixo das obtidas pelas configurações com controle de tamanho, que ficaram entre 44,68% e 55,23% com F1 entre 0,114 e 0,148 e AUC entre 0,726 e 0,765. Esse contraste é compatível com a hipótese de que parte do desempenho global dependa de características correlacionadas ao rótulo, como o comprimento, e não da diferença introduzida pela correção. O desenho, contudo, não identifica essa causa, porque as receitas também diferem em composição, número de exemplos e duração. Dentro do 7B, que usou uma única receita, os seis casos observados não formam um padrão descritivo uniforme entre métricas globais e ordenação: a semente 2 teve o maior F1, a menor AUC e as menores ordenações, a semente 3 teve a maior AUC, e a semente 1, as maiores ordenações. Essa observação descreve os casos da Tabela 4 e da Tabela 5 e não estima uma associação estatística.

As categorias pareadas complementam essa leitura. Com o limiar de maior F1, a categoria P-B predominou em todas as configurações, e P-C ficou entre 2 e 13 pares; nas seis avaliações 7B, entre 5 e 8. Mesmo quando a ordenação se aproxima ou supera 50%, a diferença entre os escores das duas versões raramente atravessa o limiar. Uma ordem relativa favorável, portanto, não se converte em decisões corretas para ambas as versões.

O segundo limiar mostra outra face das mesmas configurações. Quando a FPR é limitada a 0,5% na validação, a FNR no teste foi de 88,06% na configuração 3B de proporção original e ficou entre 97,99% e 98,71% no 7B. Apenas as avaliações da semente 2 do 7B e a heurística mantiveram a FPR do teste em até 0,5%; nas demais, a FPR observada ficou entre 0,52% e 0,69%. Na heurística, esse limiar coincidiu com o teto de 2.048 tokens, e pela regra estrita nenhuma função o ultrapassou, o que resultou em FNR de 100% e FPR nula. Esse resultado decorre da combinação entre truncamento e regra de decisão e não contradiz a AUC de 0,810. Em um cenário de poucos falsos alarmes, nenhuma configuração deixou de perder a maior parte das funções vulneráveis.

### 4.3. Dispersão entre sementes e incerteza no 7B

A Tabela 6 resume a ordenação das três sementes 7B em cada implantação, separando a dispersão entre treinamentos da incerteza amostral do teste.

Tabela 6. Ordenação pareada do 7B: média das três sementes, desvio padrão entre sementes e intervalo percentil de 95% por *bootstrap* de 550 grupos projeto/commit (10.000 réplicas), condicional aos três modelos observados. O intervalo da diferença mantém os mesmos grupos nas duas implantações.

| Medida | Estimativa (%) ou p.p. | DP sementes (p.p.) | IC95% inferior | IC95% superior |
| --- | --- | --- | --- | --- |
| NF4 | 50,62 | 5,17 | 47,92 | 53,33 |
| BF16 | 49,97 | 4,63 | 47,14 | 52,73 |
| NF4 − BF16 (p.p.) | 0,65 | — | -1,22 | 2,54 |

As médias foram 50,62% em NF4 e 49,97% em BF16, com desvios padrão de 5,17 e 4,63 pontos percentuais entre sementes. Esses desvios são da mesma ordem que a amplitude dos intervalos condicionais das médias, e as sementes isoladas apontam em direções opostas: a semente 1 ficou acima de 50% nas duas implantações, e a semente 2, abaixo. Uma única semente poderia, assim, sugerir conclusões contrárias. A diferença média NF4 − BF16 foi de 0,65 ponto percentual, com intervalo de −1,22 a 2,54. Esse intervalo inclui diferenças nas duas direções e não distingue as implantações; ele também não estabelece equivalência, que exigiria uma margem definida antes da análise. Já os intervalos das médias, de 47,92% a 53,33% em NF4 e de 47,14% a 52,73% em BF16, incluem 50%, o que não prova que os modelos ordenem ao acaso.

### 4.4. Sensibilidades ao truncamento e à correspondência dos pares

A última coluna da Tabela 5 repete a ordenação nos 465 pares sem truncamento. A heurística caiu de 21,10% para 15,16%. No 7B, as maiores reduções ocorreram na semente 2, de 45,04% para 42,37% em NF4 e de 44,68% para 41,94% em BF16, enquanto a semente 3 praticamente não mudou. Após o corte em 2.048 tokens, 32 pares têm sequências de entrada idênticas nas duas versões, ao passo que as avaliações 7B registraram de 32 a 40 empates; parte dos empates decorre, portanto, de entradas idênticas, mas um empate de escore não prova essa identidade. Como o recorte também muda a composição do teste, a diferença não pode ser atribuída apenas ao truncamento.

Uma inspeção focalizada examinou os 15 pares de teste cujas versões diferem no cabeçalho ou na assinatura. A verificação nos repositórios de origem (Material Suplementar, Seção S3) confirmou cinco casos em que a função rotulada como corrigida já existia antes do commit e corresponde a outra função, e não à versão corrigida da vulnerável. Removidos esses cinco pares, a maior alteração absoluta nas seis avaliações 7B foi de 0,22 ponto percentual, e o padrão descrito nas Seções 4.2 e 4.3 se manteve (Tabela S1 do Material Suplementar). Esse resultado indica que esses casos não alteram as conclusões, mas não certifica os 559 pares restantes nem estima a frequência desse problema no PrimeVul.

### 4.5. Recursos das implantações 7B

A Tabela 7 apresenta os recursos registrados para cada checkpoint 7B nas duas implantações.

Tabela 7. Recursos do 7B na NVIDIA A40, com Transformers, lotes de até 32.768 tokens e contexto de 2.048 tokens. Memória CUDA alocada após a carga e pico na janela de pontuação da validação, do teste e dos pares, em GB decimais. Tempo amortizado por função no teste, em lotes. Custo estimado da pontuação do teste ao preço histórico de US$ 0,50/h. As sementes não são repetições independentes da medição de desempenho computacional.

| Configuração | Após carga (GB) | Pico (GB) | Tempo/função (ms) | Custo estimado do teste (US$) |
| --- | --- | --- | --- | --- |
| 7B NF4 s1 | 4,63 | 12,49 | 59,6 | 0,2145 |
| 7B BF16 s1 | 14,15 | 20,76 | 46,8 | 0,1684 |
| 7B NF4 s2 | 4,63 | 12,49 | 59,8 | 0,2152 |
| 7B BF16 s2 | 14,15 | 20,76 | 46,9 | 0,1687 |
| 7B NF4 s3 | 4,63 | 12,49 | 60,0 | 0,2160 |
| 7B BF16 s3 | 14,15 | 20,76 | 47,1 | 0,1696 |

A implantação NF4 alocou 4,63 GB após a carga, cerca de 67% menos que os 14,15 GB da BF16, e atingiu pico de 12,49 GB, contra 20,76 GB, uma redução de cerca de 40%. Em contrapartida, o tempo amortizado foi maior em NF4, de 59,6 a 60,0 ms por função, contra 46,8 a 47,1 ms em BF16. Com o mesmo preço por hora, o custo estimado acompanhou essa diferença. Nesse ambiente, portanto, a implantação NF4 trocou memória por tempo, sem diferença distinguível na ordenação pareada (Tabela 6).
