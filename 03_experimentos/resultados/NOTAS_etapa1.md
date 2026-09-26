# Notas de leitura — Etapa 1 (baseline 16 bits, prompt v1 zero-shot)

Dados: **PrimeVul, release original do artigo** (Google Drive oficial dos autores), teste = 25.911 funções
(695 vulneráveis, 2,7%); pareado = 1.128 funções / **564 pares**, todos avaliados. Pod: A40 48 GB, US$ 0,50/h.
Todas as rodadas com `--max_tokens_entrada 8192`, seed 42, decodificação gulosa, ambiente travado (`ambiente_confere = sim`).
Rodadas de 23–24/set/2026. As rodadas anteriores, feitas na release v0.1 (um subconjunto), estão em `v01/`.

## Tabela resumo

| Modelo | F1 | Prec. | Rev. | FPR | Alarmes falsos | P-C (pareado) | VRAM | Tempo/função | Custo (teste completo) |
|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5-Coder-3B-Instruct | 0,120 | 0,102 | 0,144 | 3,5% | 879 | 2,8% (16/564) | 7,2 GB | 0,071 s | US$ 0,26 |
| Qwen2.5-Coder-7B-Instruct | 0,062 | 0,039 | 0,160 | 11,0% | 2.774 | 2,5% (14/564) | 16,9 GB | 0,112 s | US$ 0,41 |
| *Tamanho da função (baseline, sem modelo)* | *0,200* | *0,152* | *0,294* | *4,5%* | — | *0,4% (2/564)* | *0* | *~0* | *~0* |

Acaso no pareado ≈ 25% de P-C. O baseline do tamanho está detalhado em `NOTAS_etapa3.md`; ele entra aqui
porque é o piso de qualquer tabela: **só contar os tokens da função dá F1 0,20, acima dos dois modelos.**

Pareado completo: 3B = P-C 16 · P-V 67 · P-B 463 · P-R 18; 7B = P-C 14 · P-V 78 · P-B 454 · P-R 18.

## O que os logs mostram (cruzamento 3B × 7B, mesmas 25.911 funções)

- O 3B acerta 100 das 695 vulneráveis e o 7B acerta 111, mas só **26** são as mesmas (seriam 16 se os dois
  chutassem de forma independente). Os acertos não são "conhecimento" em comum.
- Nos pares, o 3B distingue 16 e o 7B distingue 14 — **nenhum par em comum**.
- O 7B diz YES 3× mais (2.885 contra 979) e acha só 11 vulneráveis a mais: o resto são alarmes falsos.
- Taxa de YES na função vulnerável × na corrigida: 3B 14,7% / 15,1%; 7B 16,3% / 17,0%. A resposta não muda
  quando a falha é consertada — se muda, é para dizer YES um pouco mais na versão corrigida.
- **Tamanho.** Por quartil de tokens (Q1 = mais curtas):

  | Quartil | % vulneráveis | YES do 3B | YES do 7B |
  |---|---|---|---|
  | Q1 | 0,3% | 0,4% | 8,3% |
  | Q2 | 0,9% | 0,6% | 11,1% |
  | Q3 | 2,1% | 2,3% | 14,9% |
  | Q4 | 7,5% | 11,7% | 10,2% |

  O 3B diz YES quase só nas funções longas — o "sinal" que ele usa é o tamanho, e o tamanho de fato separa
  (7,5% de vulneráveis no Q4 contra 0,3% no Q1). O 7B diz YES em todos os quartis, até onde quase não há
  vulnerável: nem esse sinal ele usa.
- Truncagem a 8192 tokens afeta 76 funções do teste (0,3%) e 38 do pareado. Na release v0.1, trocar 2048 por
  8192 mudou o F1 do 3B de 0,111 para 0,113: a truncagem não explica o desempenho.

## Comparação com a release v0.1 (as mesmas quatro rodadas, antes da migração)

| | F1 3B | F1 7B | P-C 3B | P-C 7B |
|---|---|---|---|---|
| v0.1 (24.788 funções, 433 pares) | 0,113 | 0,051 | 3,2% | 2,3% |
| original (25.911 funções, 564 pares) | 0,120 | 0,062 | 2,8% | 2,5% |

Nenhuma conclusão muda de uma release para a outra. Isso também vale como conferência de robustez: os achados
não dependem do recorte feito pela v0.1.

## Teste de reprodutibilidade: mesma rodada em GPU diferente (feito na v0.1, fora dos resultados)

O pareado do 3B foi rodado duas vezes com tudo igual (modelo, prompt, seed, decodificação gulosa), uma na A40 e
outra na RTX A5000. A rodada da A5000 saiu das planilhas: log e linhas removidas em `../logs/descartados/`.

| GPU | F1 | P-C | P-V | P-B | P-R |
|---|---|---|---|---|---|
| A40 | 0,239 | 14 | 53 | 353 | 13 |
| RTX A5000 | 0,227 | 13 | 50 | 357 | 13 |

- **9 das 870 respostas mudaram** (~1%). Na mesma GPU, repetir dá resultado idêntico.
- Causa: contas em 16 bits usam rotinas diferentes em placas diferentes; arredondamentos mínimos viram outra
  palavra em casos-limite.
- Consequência: diferença de ~1 ponto de F1 ou de 1–2 pares de P-C **é ruído de hardware**, não efeito do método.
  Toda comparação (16 × 4 bits, NF4 × AWQ × GPTQ) deve rodar **no mesmo tipo de GPU** (protocolo §10).
- A mesma fonte de ruído vale para versões de bibliotecas: por isso as versões são travadas
  (`../codigo/requisitos_travados.txt`) e cada linha da planilha registra torch, transformers, revisão do modelo
  e impressão digital dos dados.

## Reprodutibilidade em pod novo, com ambiente travado (17/set/2026, na v0.1)

O pareado do 3B refeito num pod A40 novo, já com a trava, deu **870 de 870 respostas idênticas** à rodada de
13/set, inclusive o texto cru. Mesma placa + mesmas versões reproduzem o resultado exatamente, mesmo com o pod
recriado. A conclusão é de método e não depende da release.

Referências para conferir as próximas rodadas (release original):

| O quê | Valor |
|---|---|
| Revisão do Qwen2.5-Coder-3B-Instruct | `488639f1ff80` (a mesma da v0.1) |
| Revisão do Qwen2.5-Coder-7B-Instruct | `c03e6d358207` |
| Impressão digital do teste | `7f0db8408bdd` |
| Impressão digital do teste pareado | `54a16a5ab663` |

Se um desses valores mudar numa rodada futura, o modelo ou os dados mudaram.

## Conclusão para a qualificação

Sem treino, nem o 3B nem o 7B detectam vulnerabilidade no PrimeVul: F1 no nível do acaso, pareado abaixo do acaso
(2,5–2,8% de P-C, contra 25% de um chute) e o modelo maior custa 2,4× a memória e 1,6× o tempo para ficar **pior**.
Um contador de tokens, sem modelo nenhum, tem F1 0,20 — acima dos dois. Isso reproduz PrimeVul (Ding et al.),
Risse & Böhme e Vul-RAG (acurácia pareada 0,06–0,14 sem RAG). O zero-shot é o "chão" da curva custo × qualidade;
o que acontece com o ajuste fino está em `NOTAS_etapa3.md`.
