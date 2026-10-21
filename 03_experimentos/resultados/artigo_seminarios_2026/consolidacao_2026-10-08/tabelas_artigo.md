Tabela 1. Configurações de ajuste. Tempo corresponde ao treino registrado; custo inclui o tempo total registrado da rodada, ao preço histórico de US$ 0,50/h. As horas não representam orçamento igual entre receitas.

| Configuração | Vulneráveis | Benignas | Épocas | Selecionada | Treino (h) | Custo total (US$) |
| --- | --- | --- | --- | --- | --- | --- |
| 3B 1:1 | 5574 | 5574 | 3 | 1 | 3,37 | 1,85 |
| 3B real | 5574 | 178853 | 1 | 1 | 10,16 | 5,14 |
| 3B 1:1 tamanho | 5574 | 5574 | 3 | 3 | 4,98 | 2,65 |
| 7B 1:1 tamanho s1 | 5574 | 5574 | 3 | 3 | 7,89 | 4,21 |
| 7B 1:1 tamanho s2 | 5574 | 5574 | 3 | 2 | 7,89 | 4,21 |
| 7B 1:1 tamanho s3 | 5574 | 5574 | 3 | 3 | 7,91 | 4,23 |


Tabela 2. Prompting no teste global (25.911 funções) e categorias no teste pareado (564 pares), pela regra YES/NO. Contexto do código: 8.192 tokens.

| Modelo | F1 | Precisão | Revocação | FPR (%) | P-C | P-V | P-B | P-R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Prompt 3B | 0,119 | 0,102 | 0,144 | 3,49 | 16 | 67 | 463 | 18 |
| Prompt 7B | 0,062 | 0,038 | 0,160 | 11,00 | 14 | 78 | 454 | 18 |


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


Tabela 5. Recursos históricos do 7B na NVIDIA A40, Transformers, 32.768 tokens por lote e contexto de 2.048. GB decimais de memória alocada após carga e pico na janela que abrange dev/teste/pareado. Tempo amortizado do teste em lotes; custo computacional estimado ao preço histórico US$ 0,50/h. As seeds não são repetições independentes de desempenho.

| Configuração | Após carga (GB) | Pico (GB) | Tempo/função (ms) | Custo teste (US$) |
| --- | --- | --- | --- | --- |
| 7B NF4 s1 | 4,63 | 12,49 | 59,6 | 0,2145 |
| 7B BF16 s1 | 14,15 | 20,76 | 46,8 | 0,1684 |
| 7B NF4 s2 | 4,63 | 12,49 | 59,8 | 0,2152 |
| 7B BF16 s2 | 14,15 | 20,76 | 46,9 | 0,1687 |
| 7B NF4 s3 | 4,63 | 12,49 | 60,0 | 0,2160 |
| 7B BF16 s3 | 14,15 | 20,76 | 47,1 | 0,1696 |


Tabela 6. Ordenação pareada do 7B: média das três seeds, dispersão descritiva entre seeds e IC percentil de 95% por bootstrap de 550 grupos projeto/commit (10.000 réplicas), condicional aos três modelos observados. O intervalo da diferença mantém alinhamento entre variantes.

| Medida | Estimativa (%) ou p.p. | DP seeds (p.p.) | IC95% inferior | IC95% superior |
| --- | --- | --- | --- | --- |
| NF4 | 50,62 | 5,17 | 47,92 | 53,33 |
| BF16 | 49,97 | 4,63 | 47,14 | 52,73 |
| NF4 − BF16 (p.p.) | 0,65 | — | -1,22 | 2,54 |


Tabela 7 suplementar. Ordenação no conjunto oficial (564), sem cinco correspondências incompatíveis com os patches (559) e, entre esses, sem truncamento (460). Recortes retrospectivos; não certificam a correção de todos os pares restantes.

| Configuração | Ord. 564 (%) | Ord. 559 (%) | Ord. 460 (%) |
| --- | --- | --- | --- |
| Tamanho | 21,10 | 20,57 | 14,46 |
| 3B 1:1 | 42,38 | 42,40 | 39,02 |
| 3B real | 37,50 | 37,30 | 33,80 |
| 3B 1:1 tamanho | 49,20 | 49,02 | 48,48 |
| 7B NF4 s1 | 55,23 | 55,19 | 54,02 |
| 7B BF16 s1 | 53,28 | 53,22 | 51,85 |
| 7B NF4 s2 | 45,04 | 45,26 | 42,61 |
| 7B BF16 s2 | 44,68 | 44,90 | 42,17 |
| 7B NF4 s3 | 51,60 | 51,52 | 51,52 |
| 7B BF16 s3 | 51,95 | 51,88 | 51,96 |
