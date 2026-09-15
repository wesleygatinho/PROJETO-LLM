# Notas de leitura — Etapa 1 (baseline 16 bits, prompt v1 zero-shot)

Dados: PrimeVul v0.1 (espelho HF `colin/PrimeVul`), teste = 24.788 funções (549 vulneráveis, 2,2%);
pareado = 870 funções / 433 pares avaliados. Pod: A40 48 GB, US$ 0,50/h. Todas as linhas abaixo com `--max_tokens_entrada 8192`
(exceto o pareado do 3B, feito com 2048 — refazer com 8192 para ficar comparável).

## Tabela resumo

| Modelo | F1 | Prec. | Rev. | FPR | Alarmes falsos | P-C (pareado) | VRAM | Tempo/função | Custo (teste completo) |
|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5-Coder-3B | 0,113 | 0,090 | 0,151 | 3,5% | 838 | 3,7% (16/433) | 7,2 GB | 0,074 s | US$ 0,26 |
| Qwen2.5-Coder-7B | 0,051 | 0,030 | 0,151 | 10,9% | 2.652 | 2,3% (10/433) | 16,9 GB | 0,113 s | US$ 0,40 |

Acaso no pareado ≈ 25% de P-C.

## O que os logs mostram (cruzamento 3B × 7B, mesmas 24.788 funções)

- Os dois modelos encontram **exatamente 83** das 549 vulneráveis, mas só **19** são as mesmas. Os acertos não são "conhecimento", são coincidência.
- Nos pares, o 3B distingue 16 e o 7B distingue 10 — **nenhum par em comum**.
- O 7B diz YES 3× mais (2.735 vs 921) sem achar nenhuma vulnerável a mais: só multiplica alarmes falsos.
- Taxa de YES na função vulnerável vs. na corrigida: 3B 15,9% / 14,7%; 7B 15,4% / 15,9%. Resposta não muda quando a falha é consertada.
- O 3B diz YES quase só em funções longas (11% no quartil mais longo, onde 6% são de fato vulneráveis); o 7B diz YES em funções curtas também (7% no quartil mais curto, onde 0,1% são vulneráveis). Ou seja: o "sinal" que o 3B usa é o tamanho da função; o 7B nem isso.
- Truncagem a 8192 tokens afeta 72 funções (0,3%); a 2048, 621. O resultado do 3B quase não mudou (F1 0,111 → 0,113), logo a truncagem NÃO explicava a FPR alta do pareado — o pareado é simplesmente mais difícil (funções maiores, casos com versão corrigida disponível).

## Conclusão para a qualificação

Sem treino, nem o 3B nem o 7B detectam vulnerabilidade no PrimeVul: F1 no nível do acaso, pareado abaixo do acaso,
e o modelo maior custa 2,3× a memória e 1,5× o tempo para ficar **pior**. Isso reproduz PrimeVul (Ding et al.),
Risse & Böhme e Vul-RAG (acurácia pareada 0,06–0,14 sem RAG). Consequência para o trabalho: a curva custo × qualidade
só começa a existir depois do ajuste fino (QLoRA + cabeça de classificação) — o zero-shot é o "chão" da curva.
