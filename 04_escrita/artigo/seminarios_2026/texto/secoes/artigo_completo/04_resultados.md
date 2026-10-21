## 4. Resultados

### 4.1. Conferência e avaliação global

A junção dos 33 arquivos de previsão das 14 avaliações selecionadas com os splits oficiais não apresentou divergências de posição, idx, projeto, commit ou rótulo e manteve cobertura integral. A reconstrução não exigiu alterar CSVs ou registros históricos. O teste pareado tem 1.128 posições, mas 1.126 identidades idx distintas por causa das duas reutilizações oficiais documentadas. A distinção entre correspondência documental e correspondência de correção é relevante: os cinco casos confirmados pelos patches afetam a interpretação do pareado, embora não indiquem erro de alinhamento dos logs.

Tabela 2. Prompting no teste global (25.911 funções) e categorias no teste pareado (564 pares), pela regra YES/NO. Contexto do código: 8.192 tokens.

| Modelo | F1 | Precisão | Revocação | FPR (%) | P-C | P-V | P-B | P-R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Prompt 3B | 0,119 | 0,102 | 0,144 | 3,49 | 16 | 67 | 463 | 18 |
| Prompt 7B | 0,062 | 0,038 | 0,160 | 11,00 | 14 | 78 | 454 | 18 |

No prompting global, o 3B apresentou F1 de 0,119 e o 7B de 0,062. A maior revocação do 7B, 0,160 frente a 0,144, foi acompanhada de FPR de 11,00%, contra 3,49% no 3B, reduzindo a precisão. Nos pares, a categoria P-B concentrou 463 e 454 dos 564 casos, respectivamente; apenas 16 e 14 tiveram decisões P-C. Esses resultados descrevem a instrução e o parser utilizados, e não o desempenho de toda forma de prompting possível.

Tabela 3. Teste global, 25.911 funções. F1/precisão/revocação/FPR usam o limiar de maior F1 no dev; FNR* e FPR* usam outro limiar, calibrado para FPR ≤ 0,5% no dev. FPR* é o valor efetivamente observado no teste. AUC usa os scores disponíveis.

| Configuração | F1 | Precisão | Revocação | FPR (%) | AUC | FNR* (%) | FPR* (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tamanho | 0,200 | 0,152 | 0,294 | 4,53 | 0,810 | 100,00 | 0,00 |
| 3B 1:1 | 0,195 | 0,142 | 0,312 | 5,19 | 0,795 | 94,10 | 0,54 |
| 3B real | 0,262 | 0,200 | 0,380 | 4,19 | 0,851 | 88,06 | 0,65 |
| 3B 1:1 tamanho | 0,121 | 0,083 | 0,224 | 6,86 | 0,746 | 96,26 | 0,63 |
| 7B NF4 s1 | 0,114 | 0,077 | 0,222 | 7,36 | 0,738 | 97,99 | 0,69 |
| 7B BF16 s1 | 0,119 | 0,081 | 0,229 | 7,19 | 0,740 | 98,13 | 0,67 |
| 7B NF4 s2 | 0,142 | 0,103 | 0,229 | 5,47 | 0,726 | 98,71 | 0,38 |
| 7B BF16 s2 | 0,148 | 0,115 | 0,207 | 4,41 | 0,728 | 98,71 | 0,38 |
| 7B NF4 s3 | 0,127 | 0,084 | 0,258 | 7,75 | 0,765 | 98,27 | 0,56 |
| 7B BF16 s3 | 0,124 | 0,087 | 0,220 | 6,39 | 0,765 | 98,27 | 0,52 |

A referência de tamanho alcançou F1 de 0,200 e AUC de 0,810. Entre os pilotos 3B, a receita de proporção real apresentou o maior F1 global observado, 0,262, e AUC de 0,851; a receita 1:1 com controle de tamanho apresentou F1 de 0,121 e AUC de 0,746. Esse contraste é descritivo, pois número de exemplos, duração, composição e repetições diferem. Nas seis avaliações 7B, F1 variou entre 0,114 e 0,148 e AUC entre 0,726 e 0,765. Não houve predominância global consistente de NF4 ou BF16 entre as três seeds.

O limiar F1 e o limiar de restrição de falsos positivos expressam escolhas diferentes. Na receita 3B real, por exemplo, FNR foi 88,06% no limiar de FPR calibrado no dev, acompanhado de FPR de 0,65% no teste, acima da restrição nominal. No 7B, FNR variou de 97,99% a 98,71%; somente as avaliações da seed 2 tiveram FPR de teste inferior a 0,5%. A referência de tamanho resultou em FNR de 100% e FPR zero nesse ponto: seu limiar foi o teto de 2.048 tokens e, pela regra estrita, nenhum escore truncado o ultrapassou. Esse efeito não demonstra que comprimento seja incapaz de discriminar classes; sua AUC e seu F1 sob outra calibração mostram que as interpretações dependem da regra adotada.

### 4.2. Avaliação pareada e sensibilidades

Tabela 4. Teste pareado oficial, 564 pares. Categorias P-* usam o limiar F1 do dev; ordenação usa meio crédito para empates e independe de limiar. A coluna 465 considera apenas pares com ambas as versões não truncadas.

| Configuração | P-C | P-V | P-B | P-R | Empates | Ord. 564 (%) | Ord. 465 (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tamanho | 2 | 156 | 398 | 8 | 124 | 21,10 | 15,16 |
| 3B 1:1 | 13 | 155 | 372 | 24 | 52 | 42,38 | 39,03 |
| 3B real | 6 | 200 | 344 | 14 | 43 | 37,50 | 34,09 |
| 3B 1:1 tamanho | 6 | 120 | 422 | 16 | 37 | 49,20 | 48,71 |
| 7B NF4 s1 | 7 | 116 | 435 | 6 | 39 | 55,23 | 54,09 |
| 7B BF16 s1 | 6 | 125 | 425 | 8 | 39 | 53,28 | 51,94 |
| 7B NF4 s2 | 5 | 128 | 423 | 8 | 40 | 45,04 | 42,37 |
| 7B BF16 s2 | 7 | 113 | 434 | 10 | 34 | 44,68 | 41,94 |
| 7B NF4 s3 | 6 | 134 | 412 | 12 | 32 | 51,60 | 51,61 |
| 7B BF16 s3 | 8 | 113 | 434 | 9 | 32 | 51,95 | 52,04 |

A ordenação da referência de tamanho foi 21,10%, embora sua AUC global tenha sido 0,810. O piloto 3B real, que apresentou o maior F1 global observado, ordenou 37,50% dos pares com meio crédito para empates. O piloto 3B com controle de tamanho atingiu 49,20%. No 7B, a ordenação variou de 45,04% a 55,23% em NF4 e de 44,68% a 53,28% em BF16. As decisões P-C no limiar F1 do dev permaneceram baixas: de cinco a oito pares nas seis avaliações. Uma ordem relativa favorável dos scores não implica que o limiar escolhido produza simultaneamente as duas decisões corretas.

Tabela 5. Ordenação pareada do 7B: média das três seeds, dispersão descritiva entre seeds e IC percentil de 95% por bootstrap de 550 grupos projeto/commit (10.000 réplicas), condicional aos três modelos observados. O intervalo da diferença mantém alinhamento entre variantes.

| Medida | Estimativa (%) ou p.p. | DP seeds (p.p.) | IC95% inferior | IC95% superior |
| --- | --- | --- | --- | --- |
| NF4 | 50,62 | 5,17 | 47,92 | 53,33 |
| BF16 | 49,97 | 4,63 | 47,14 | 52,73 |
| NF4 − BF16 (p.p.) | 0,65 | — | -1,22 | 2,54 |

A média de ordenação das três seeds foi 50,62% para NF4, com desvio padrão de 5,17 pontos percentuais, e 49,97% para BF16, com desvio padrão de 4,63 pontos. Os intervalos condicionais por grupo de commit são apresentados na Tabela 5. A diferença média NF4 − BF16 foi 0,65 ponto percentual, com intervalo de −1,22 a 2,54 pontos. Esse intervalo abrange diferenças em ambas as direções e não estabelece equivalência. A dispersão entre as seeds observadas é distinta dessa incerteza condicional do teste e não foi substituída pelo intervalo da média.

Nos 465 pares sem truncamento, a ordenação NF4 foi 54,09%, 42,37% e 51,61%, nas seeds 1, 2 e 3; BF16 apresentou 51,94%, 41,94% e 52,04%. A retirada das funções truncadas reduziu principalmente os resultados da seed 2. A inspeção das entradas encontrou 32 pares com sequências idênticas após o corte, enquanto as seis avaliações 7B registraram de 32 a 40 empates de score. Portanto, parte dos empates corresponde a entradas idênticas, mas scores empatados não são, isoladamente, prova dessa identidade. A mudança de denominador também impede atribuir toda diferença da sensibilidade exclusivamente ao truncamento.

Ao remover os cinco pares cuja correspondência não representa o patch da mesma função, a ordenação ficou entre 45,26% e 55,19% em NF4 e entre 44,90% e 53,22% em BF16. A maior alteração absoluta nos seis resultados 7B foi 0,22 ponto percentual, arredondada a duas casas. O padrão descritivo de variação entre seeds permaneceu, mas esse resultado não valida os outros 559 pares nem recupera avaliações das verdadeiras versões corrigidas. A tabela completa dos recortes 564/559/460 integra o suplemento.

### 4.3. Recursos de implantação

Tabela 6. Recursos históricos do 7B na NVIDIA A40, Transformers, 32.768 tokens por lote e contexto de 2.048. GB decimais de memória alocada após carga e pico na janela que abrange dev/teste/pareado. Tempo amortizado do teste em lotes; custo computacional estimado ao preço histórico US$ 0,50/h. As seeds não são repetições independentes de desempenho.

| Configuração | Após carga (GB) | Pico (GB) | Tempo/função (ms) | Custo teste (US$) |
| --- | --- | --- | --- | --- |
| 7B NF4 s1 | 4,63 | 12,49 | 59,6 | 0,2145 |
| 7B BF16 s1 | 14,15 | 20,76 | 46,8 | 0,1684 |
| 7B NF4 s2 | 4,63 | 12,49 | 59,8 | 0,2152 |
| 7B BF16 s2 | 14,15 | 20,76 | 46,9 | 0,1687 |
| 7B NF4 s3 | 4,63 | 12,49 | 60,0 | 0,2160 |
| 7B BF16 s3 | 14,15 | 20,76 | 47,1 | 0,1696 |

NF4 registrou 4,63 GB alocados após carga e pico de 12,49 GB, contra 14,15 GB e 20,76 GB em BF16 mesclada. A redução observada após carga foi aproximadamente 67%, e a diferença dos picos correspondeu a cerca de 40%. Entretanto, o tempo amortizado de pontuação por função foi maior em NF4: 59,6–60,0 ms, frente a 46,8–47,1 ms em BF16. No mesmo preço histórico por hora, o custo computacional estimado de pontuação do teste acompanhou essa diferença de tempo.

Os registros mostram, assim, uma troca entre memória alocada e tempo nessas formas de implantação. Como não houve repetições independentes de desempenho, controle completo das condições do hardware ou isolamento entre representação dos pesos e merge, as pequenas diferenças entre seeds não foram tratadas como um benchmark de latência. A evidência sustenta a descrição do ambiente executado, sem determinar a configuração de melhor custo para outros ambientes ou cargas.
