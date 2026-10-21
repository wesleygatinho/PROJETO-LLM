Tabela 6. Recursos históricos do 7B na NVIDIA A40, Transformers, 32.768 tokens por lote e contexto de 2.048. GB decimais de memória alocada após carga e pico na janela que abrange dev/teste/pareado. Tempo amortizado do teste em lotes; custo computacional estimado ao preço histórico US$ 0,50/h. As seeds não são repetições independentes de desempenho.

| Configuração | Após carga (GB) | Pico (GB) | Tempo/função (ms) | Custo teste (US$) |
| --- | --- | --- | --- | --- |
| 7B NF4 s1 | 4,63 | 12,49 | 59,6 | 0,2145 |
| 7B BF16 s1 | 14,15 | 20,76 | 46,8 | 0,1684 |
| 7B NF4 s2 | 4,63 | 12,49 | 59,8 | 0,2152 |
| 7B BF16 s2 | 14,15 | 20,76 | 46,9 | 0,1687 |
| 7B NF4 s3 | 4,63 | 12,49 | 60,0 | 0,2160 |
| 7B BF16 s3 | 14,15 | 20,76 | 47,1 | 0,1696 |
