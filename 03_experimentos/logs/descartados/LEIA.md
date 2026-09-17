# Rodadas descartadas

## etapa1_20260917_003514.jsonl — 3B pareado 8192 na RTX A5000 (16/set/2026)

**Por que saiu dos resultados:** rodou numa placa diferente da oficial (A40). Todas as comparações do trabalho usam o mesmo tipo de GPU.
A versão oficial dessa mesma configuração, na A40, é `etapa1_20260913_010615.jsonl`.

**Por que o arquivo foi guardado:** é a medida do ruído de hardware. Com modelo, prompt, seed e decodificação iguais,
9 das 870 respostas mudaram em relação à A40 (F1 0,227 × 0,239). Serve para a seção de ameaças à validade.
Para conferir: `python 05_comparar_logs.py ../logs/etapa1_20260913_010615.jsonl ../logs/descartados/etapa1_20260917_003514.jsonl`

Obs.: a linha foi gravada com preço/hora 0,50 (o da A40) por engano. O preço real da A5000 era US$ 0,28/h,
o que dá cerca de US$ 0,012 para os 153 s da rodada.

### Linhas removidas das planilhas

`resultados/resultados_etapa1.csv`

```csv
data,modelo,tamanho_B,precisao_bits,metodo_quantizacao,prompt_versao,seed,n_funcoes,amostra,f1,precisao,revocacao,fpr,acuracia,tp,fp,fn,tn,indefinidos,truncadas,memoria_gpu_gb,tempo_por_funcao_s,tempo_total_s,gpu,preco_hora_usd,custo_total_usd,log,observacoes
2026-09-17 00:37,Qwen/Qwen2.5-Coder-3B-Instruct,3.09,16,nenhum,v1,42,870,proporcao_real,0.2274,0.5,0.1471,0.1471,0.5,64,64,371,371,0,30,7.17,0.17,153.3,NVIDIA RTX A5000,0.5,0.0213,etapa1_20260917_003514.jsonl,3B pareado 8192
```

`resultados/resultados_pareado.csv`

```csv
data,log,dados,pares_avaliados,metodo_pareamento,P_C,P_V,P_B,P_R,P_C_pct,P_V_pct,P_B_pct,P_R_pct,rotulo
2026-09-16 21:45,etapa1_20260917_003514.jsonl,primevul_test_paired.jsonl,433,consecutivos,13,50,357,13,3.0,11.55,82.45,3.0,"3B 16bit prompt v1 8192 RTX A5000 (calculado do log, mesma regra do 04)"
```
