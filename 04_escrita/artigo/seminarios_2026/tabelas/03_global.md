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
