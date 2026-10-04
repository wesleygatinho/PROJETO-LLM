# Notas de leitura — Etapa 3 (QLoRA + cabeça de classificação), piloto do 3B

Rodadas de 24–25/set/2026, PrimeVul **release original**, A40, ambiente travado (peft 0.21.0, bitsandbytes 0.50.2).
Modelo: `Qwen/Qwen2.5-Coder-3B` (base, revisão `09d9bc5d376b`) em NF4, LoRA r=16/α=32 em todas as camadas
lineares + cabeça `score`, lr 2e-4, lote 16, até 2.048 tokens, seed 1. A escolha de época usa só a validação:
AUC numa amostra fixa (699 vulneráveis + 2.796 benignas) e **% de pares ordenados** no pareado da validação
(562 pares; acaso = 50% ± 4,1). O teste não foi tocado.

Pergunta do piloto: treinar com todas as benignas (~1:32) rende mais que 1 benigna por vulnerável?

## Resultado

| Treino | Época | Perda treino | AUC validação | Pares ordenados (validação) | P-C (validação) |
|---|---|---|---|---|---|
| 1:1 (11.148 funções/época) | 1 | 0,743 | 0,755 | **38,4%** | 0,2% |
| | 2 | 0,537 | 0,812 | 31,9% | 0,9% |
| | 3 | 0,358 | 0,832 | 35,6% | 1,2% |
| proporção real (184.427 funções) | 1 | 0,107 | **0,840** | **28,7%** | 0,0% |

| Treino | Tempo de treino | Custo | Tokens/s |
|---|---|---|---|
| 1:1, 3 épocas | 3,4 h | US$ 1,85 | 1.598 |
| proporção real, 1 época | 10,2 h | US$ 5,14 | 1.530 |

As duas rodadas estão **muito abaixo do acaso** no pareado: 38,4% fica 5,5 desvios abaixo de 50% e 28,7%, 10
desvios abaixo. Não é ruído: o modelo dá, de forma sistemática, **nota de "mais vulnerável" à versão corrigida**
da função.

## O que está acontecendo: o modelo aprende o tamanho da função

Nos quatro pontos medidos, quanto **maior** a AUC, **pior** o pareado:

| Ponto | AUC validação | Pares ordenados |
|---|---|---|
| 1:1, época 1 | 0,755 | 38,4% |
| 1:1, época 2 | 0,812 | 31,9% |
| 1:1, época 3 | 0,832 | 35,6% |
| real, época 1 | 0,840 | 28,7% |

É a assinatura de aprendizado por atalho (Risse & Böhme): a métrica que todo mundo reporta sobe enquanto a que
mede entendimento cai. O atalho é o tamanho, e os números do próprio PrimeVul explicam por quê:

- **Fora dos pares, "longa = vulnerável" funciona.** Só contar tokens dá AUC 0,81 no teste e 0,79 na validação
  (baseline do tamanho, abaixo). As vulneráveis têm 922 tokens em média contra 297 das benignas.
- **Dentro dos pares, a regra aponta para o lado errado.** No teste pareado, a versão corrigida é a mais longa em
  **67,9%** dos pares, as duas têm o mesmo tamanho em 22,0% e a vulnerável é a mais longa em só 10,1%.
  O conserto quase sempre acrescenta código (uma checagem, um `if`, um limite).
- **Mais dados = mais atalho.** A proporção real vê 32× mais benignas diferentes (178.853 contra 5.574), chega à
  maior AUC (0,840) e ao pior pareado (28,7%). Dentro do 1:1, da época 1 para a 2 acontece o mesmo.
- A perda da proporção real (0,107) fica abaixo da régua de "chutar a proporção das classes" (0,136): o modelo
  aprendeu algo além da proporção — e esse algo ordena os pares ao contrário.

A AUC do modelo (0,840) passa um pouco a do tamanho sozinho (0,79 na validação), então ele usa mais que o tamanho.
Mas o que usa a mais também não é o conserto, porque o pareado piora.

## Decisão do piloto (regra anotada antes de ver o resultado)

A regra era: se a proporção real ganhasse do 1:1 no pareado da validação por mais que a margem, o 7B usaria `real`.
**Ela perdeu**: 28,7% contra 38,4%, uma diferença de 9,8 pontos (z ≈ 3,5), custando 2,8× mais. Portanto a
proporção real está descartada. Mas as duas configurações estão abaixo do acaso, então **a proporção não é o
problema; o atalho do tamanho é**. Levar a receita atual para o 7B seria gastar ~8 h por seed para medir o custo
de um modelo que aprendeu a coisa errada.

## Baseline do tamanho (sem modelo, sem GPU)

Nota = nº de tokens da função (cortado em 2.048, como o modelo vê). Limiar de decisão escolhido na validação
(maior F1: 1.254 tokens).

| | F1 | Prec. | Rev. | FPR | AUC | VD-S | P-C | Pares ordenados |
|---|---|---|---|---|---|---|---|---|
| Tamanho da função | 0,200 | 0,152 | 0,294 | 4,5% | 0,810 | 100% | 0,4% (2/564) | 10,1% |

- **F1 0,20 é maior que o de qualquer modelo zero-shot** (3B 0,120; 7B 0,062).
- VD-S 100%: no regime de poucos alarmes falsos (FPR ≤ 0,5%) o tamanho não acha nada. AUC alta e VD-S péssimo
  medem regimes diferentes.
- No pareado ele desmorona (10,1% de pares ordenados), como esperado.
- *Correção em 26/set/2026:* a primeira versão do `08` calculava P-C/P-V/P-B/P-R com `nota > 0` em vez do limiar
  de decisão, e toda contagem de tokens é maior que 0 (a planilha dizia P-V = 564). Os valores certos foram
  recalculados do log, sem rodar de novo; a linha da planilha registra a correção.

## Consequência de método: o pareado também tem um atalho, só que invertido

Uma regra "curta = vulnerável" ordenaria certo **67,9%** dos pares do teste sem entender nada. Então um modelo
futuro que passe de 50% no pareado pode estar só usando o atalho ao contrário. Para separar entendimento de
tamanho, os próximos números precisam de uma checagem que o tamanho não explique.

A ideia inicial era olhar só os pares de mesmo tamanho, mas ela não se sustenta: dos 124 pares do teste com o
mesmo nº de tokens, **97 são pares em que as duas versões foram cortadas em 2.048 tokens** — o modelo muitas
vezes nem vê o conserto. Sobram 27 pares limpos, pouco demais para uma métrica. No lugar, desde 26/set/2026
todo treino e toda avaliação registram:

- **correlação nota × tamanho nos pares**: Spearman, entre os pares, da diferença de nota (vulnerável − corrigida)
  com a diferença de tamanho. Um detector que só olha o tamanho dá **+1** (é o valor do baseline); um que não usa
  o tamanho dá perto de **0**;
- **pares com nota idêntica**: em geral o conserto ficou depois do corte e o modelo viu duas entradas iguais;
- **AUC do tamanho no treino**: quanto o tamanho sozinho separa as classes no conjunto de treino montado
  (0,5 = nada).

## Terceiro braço do piloto: 1:1 com benignas de mesmo tamanho

Para cada vulnerável do treino, a benigna de tamanho mais próximo (em tokens, como o modelo vê), sem repetir.
Com os tamanhos reais do teste, isso leva a AUC do tamanho de **0,816** (1:1 sorteado) para **0,500**, com
diferença média de 0,11 token por par. Mesmos hiperparâmetros do 1:1 (3 épocas, seed 1), para comparar só o
efeito do pareamento. Custo estimado: ~5,4 h de treino, ~US$ 2,70.

**Regra de decisão, anotada em 26/set/2026, antes de rodar** (pares ordenados na validação, melhor época;
acaso = 50% ± 4,1):

| Resultado | Leitura | Consequência |
|---|---|---|
| **acima de 54,1%** | O modelo aprende algo além do tamanho. | Esta vira a receita do 7B. |
| **entre 45,9% e 54,1%** | Sem o atalho, não há sinal que o 3B aprenda. | Esta vira a receita do 7B mesmo assim (ao menos não aprende o contrário), e a dissertação registra que o ajuste fino só aprendia o atalho. |
| **abaixo de 45,9%** | O modelo achou outro atalho que aponta para a versão corrigida. | Investigar antes de gastar com o 7B. |

Em qualquer caso, confere-se a correlação nota × tamanho: ela deve cair para perto de 0. Se continuar alta, o
pareamento não tirou o atalho e o resultado não pode ser lido como acima.

Na mesma sessão, os dois adaptadores do piloto são avaliados no teste (a decisão deles já foi tomada) e entram
na dissertação como ablação ("proporção de treino × atalho").

Os adaptadores estão em `wesley2h/etapa3-adaptadores` (Hugging Face, privado).

## Resultado do terceiro braço (29/set/2026, só validação)

O pareamento funcionou: 99,7% das benignas têm exatamente o tamanho da sua vulnerável (diferença máxima de 2 tokens)
e a AUC do tamanho no treino ficou em 0,500.

| Época | Perda treino | AUC validação | Pares ordenados | Nota × tamanho nos pares | Empatados |
|---|---|---|---|---|---|
| 1 | 0,654 | 0,736 | 34,2% | +0,32 | 45 |
| 2 | 0,458 | 0,788 | 44,5% | +0,07 | 41 |
| 3 | 0,322 | 0,760 | **48,0%** | **−0,05** | 38 |

Treino: 5,0 h, US$ 2,65, 1.631 tokens/s. Melhor época pelo pareado: 3.

**Decisão, pela regra anotada antes de rodar:** 48,0% está dentro da faixa do acaso (45,9–54,1%) e a correlação com
o tamanho caiu para perto de zero (−0,05), então o resultado pode ser lido como previsto. É a linha do meio da tabela:
**sem o atalho do tamanho, o 3B não aprende nada que distinga a versão vulnerável da corrigida.** A receita do 7B
passa a ser **1:1 com benignas de mesmo tamanho, 3 épocas**.

O que mudou ao longo das épocas: na época 1 o modelo ainda ordenava os pares pelo tamanho (+0,32), mesmo sem o
tamanho ajudar no treino; com mais treino essa dependência some e o pareado sobe até o acaso — mas não passa dele.

## Adaptadores do piloto avaliados no teste (29/set/2026)

Variante nf4 (como foram treinados), melhor época de cada um. Teste: 25.911 funções; pareado: 564 pares.

| | F1 | FPR | AUC | VD-S (validação) | VD-S oráculo | Pares ordenados | Nota × tamanho | Empatados |
|---|---|---|---|---|---|---|---|---|
| 1:1 sorteado | 0,189 | 2,6% | 0,795 | 0,941 | 0,942 | 37,8% | +0,33 | 52 |
| Proporção real | 0,000 | 0,0% | **0,851** | **0,881** | **0,901** | **33,7%** | +0,42 | 43 |
| *Tamanho da função* | *0,200* | *4,5%* | *0,810* | *1,000* | *1,000* | *10,1%* | *+1,00* | *124* |

- **O teste confirma a validação:** os dois ficam muito abaixo do acaso no pareado (37,8% e 33,7%; o acaso é
  50% ± 4,1) e a nota acompanha o tamanho dentro dos pares (+0,33 e +0,42).
- **Pelo critério do artigo do PrimeVul, o melhor modelo é justamente o que mais aprendeu o atalho.** A proporção
  real tem a maior AUC (0,851) e o melhor VD-S (0,881; oráculo 0,901, na faixa dos modelos ajustados do artigo,
  entre ~0,88 e ~0,96) — e o pior pareado.
- F1 = 0 na proporção real: treinado com 1 vulnerável para 32 benignas, o modelo nunca passa do limiar padrão
  (nota > 0). A nota ainda ordena bem (AUC 0,851); é só o limiar 0 que fica sem sentido nesse desbalanceamento.
- O tamanho não explica tudo fora dos pares: dentro de faixas de tamanho parecido, a AUC no teste fica em média em
  0,60 (1:1) e 0,74 (proporção real). Mas o que o modelo usa a mais é algo que **as duas versões de um par têm
  igual** — o tipo de código, o projeto, o estilo —, porque no par ele não ajuda. Ou seja, o modelo aprende "que
  tipo de função costuma ter falha", não "esta versão tem a falha".
- O 1:1 sorteado tem AUC (0,795) e F1 (0,189) **abaixo** do baseline do tamanho (0,810 e 0,200).

## Próximo passo

1. Avaliar no teste o adaptador do terceiro braço (a decisão acima já está registrada).
2. Treinar o 7B com a receita escolhida, seeds 1, 2 e 3 (estimativa: ~12 h e ~US$ 6 por seed).
3. Ponto para o orientador: com o pareado no acaso, a comparação entre métodos de quantização (RQ2) vai depender
   de AUC, VD-S e F1, que ainda têm sinal; o pareado passa a servir como controle (a quantização não deve tirá-lo
   do acaso, nem em direção nenhuma).

## 7B: leitura anotada antes de rodar (04/out/2026)

Receita: 1:1 com benignas de mesmo tamanho, 3 épocas, seeds 1, 2 e 3; melhor época de cada seed pelo pareado da
validação, como no 3B. Pergunta: com 2,4× mais parâmetros, o modelo aprende a distinguir a versão vulnerável da
corrigida, que o 3B não aprendeu?

Medida: pares ordenados no pareado da validação (562 pares; acaso = 50% ± 4,1). As três seeds são avaliadas nos
mesmos pares, então a média delas não estreita essa margem.

| Resultado (média das 3 seeds) | Leitura | Consequência |
|---|---|---|
| **acima de 54,1%** e nenhuma seed abaixo de 50% | O 7B aprende algo que o 3B não aprendeu. | O pareado entra na RQ2 como métrica de qualidade: a quantização pode tirar esse ganho. |
| **acima de 54,1%**, mas alguma seed abaixo de 50% | O sinal depende da seed. | Registra-se como instável; não conta como "aprende". |
| **entre 45,9% e 54,1%** | Como no 3B: sem o atalho do tamanho, o ajuste fino não aprende a distinguir as versões, nem no 7B. | Cenário-base do protocolo (§11). A RQ2 se apoia em AUC, VD-S e F1; o pareado fica como controle. |
| **abaixo de 45,9%** | Outro atalho que aponta para a versão corrigida. | Investigar antes de gerar as variantes quantizadas. |

Como no terceiro braço, confere-se a correlação nota × tamanho na melhor época de cada seed: ela deve ficar perto
de 0. Se não ficar, o pareamento não tirou o atalho e o resultado não pode ser lido pela tabela.

O teste (F1, AUC, VD-S, pares ordenados) é avaliado na mesma sessão, mas não muda a leitura acima; entra na tabela
custo × qualidade ao lado do 3B e do baseline do tamanho.
