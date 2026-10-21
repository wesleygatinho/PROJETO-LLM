## 3. Materiais e métodos

### 3.1. Visão geral

O estudo trata a detecção como classificação binária de funções C/C++ e compara três grupos de configurações: variantes Instruct do Qwen2.5-Coder usadas por instrução textual, classificadores Base ajustados com LoRA e uma heurística de comprimento. O protocolo seguiu esta sequência. Primeiro, cada classificador foi treinado por até três épocas, e a época foi escolhida em dados de validação. Em seguida, dois limiares foram calibrados na validação global e aplicados ao teste sem recalibração: o de maior F1, às métricas globais e às categorias pareadas; o de FPR de até 0,5%, à taxa de falsos negativos e à de falsos positivos do teste global. Depois, os checkpoints 7B foram avaliados em duas implantações, com registro de memória e tempo. Por fim, a ordenação pareada do 7B foi resumida entre sementes, com intervalos por reamostragem e análises de sensibilidade. Este é um estudo retrospectivo e exploratório: as métricas foram recalculadas a partir das previsões registradas nas execuções originais, alinhadas às partições oficiais, e o conjunto de teste foi consultado enquanto as receitas eram desenvolvidas. Os procedimentos de alinhamento e a proveniência dos registros estão no Material Suplementar (Seções S1 e S2).

### 3.2. Conjunto de dados

Foi utilizada a distribuição original do PrimeVul, composta por funções C/C++ de projetos de código aberto, com rótulos derivados de commits de correção, deduplicação e divisão cronológica [Ding et al. 2024]. A Tabela 1 apresenta as partições usadas e os pares vulnerável/corrigida de cada uma.

Tabela 1. Partições do PrimeVul utilizadas: número de funções, funções rotuladas como vulneráveis e pares vulnerável/corrigida.

| Partição | Funções | Vulneráveis | Pares |
| --- | --- | --- | --- |
| Treino | 184.427 | 5.574 | 4.354 |
| Validação | 25.430 | 699 | 562 |
| Teste | 25.911 | 695 | 564 |

A classe vulnerável corresponde a 2,68% do teste global, o que torna a acurácia pouco informativa e motiva o uso de F1, precisão, revocação e taxas de erro. Cada par reúne uma função rotulada como vulnerável e outra rotulada como sua versão corrigida, no mesmo projeto e commit. Os 564 pares de teste pertencem a 550 grupos projeto/commit, unidade usada na reamostragem (Seção 3.6). Os classificadores e a heurística usaram contexto de 2.048 tokens, preservando o início da função; nos 465 pares de teste, as duas versões cabem integralmente nesse limite.

### 3.3. Configurações avaliadas

Nas avaliações por instrução, as variantes Qwen2.5-Coder-3B-Instruct e 7B-Instruct, carregadas em FP16, receberam uma instrução sem exemplos que pedia uma única palavra, YES ou NO, para cada função. A decodificação foi determinística, com até cinco novos tokens. Os registros históricos dessas rodadas indicam limite de 8.192 tokens para o código. Um analisador aceitou a primeira palavra de decisão reconhecida; respostas indefinidas seriam contadas como não vulneráveis, mas nenhuma ocorreu nas quatro avaliações. Essas configurações produzem apenas decisões e, por isso, não entram na ordenação pareada.

A heurística de comprimento atribui a cada função um escore igual ao número de tokens visíveis após o corte em 2.048 tokens, obtido com o tokenizador do Qwen2.5-Coder. Sua função no estudo é servir de referência: ela não usa nenhuma informação sobre a vulnerabilidade, de modo que seu desempenho indica quanto uma característica superficial correlacionada ao rótulo consegue alcançar em cada métrica.

Os classificadores partiram dos modelos Base Qwen2.5-Coder-3B e 7B, com uma cabeça de duas saídas. O escore de vulnerabilidade é a diferença entre o logit da classe vulnerável e o da não vulnerável. No ajuste, a base foi carregada em NF4 com dupla quantização e computação em BF16. LoRA foi aplicada às projeções de atenção (q, k, v, o) e às projeções do bloco MLP (gate, up, down), com posto \(r = 16\), \(\alpha = 32\) e *dropout* de 0,05, e a cabeça de classificação também foi treinada. O otimizador foi o AdamW convencional, e não os otimizadores paginados do QLoRA, com taxa de aprendizado inicial de \(2 \times 10^{-4}\), sem decaimento de pesos, aquecimento em 3% dos passos e decaimento linear. O lote efetivo teve 16 funções, com divisão por orçamento de tokens, *checkpointing* de gradientes e corte da norma do gradiente em 1,0. A perda foi a entropia cruzada, sem peso adicional para a classe vulnerável.

Três receitas de amostragem do treino foram exploradas no 3B. A primeira manteve todas as funções vulneráveis e sorteou igual número de não vulneráveis (1:1). A segunda usou o treino completo, na proporção original. A terceira formou o conjunto 1:1 escolhendo, sem reposição, para cada função vulnerável, a não vulnerável de comprimento tokenizado mais próximo, com o comprimento limitado a 2.048 tokens (1:1 com controle de tamanho). Essa última receita procura reduzir a diferença de tamanho entre as classes no treino, sem eliminar necessariamente outras características correlacionadas ao rótulo. O 7B usou somente essa receita, com três sementes de aleatoriedade (*seeds*); cada configuração 3B teve uma única semente. A Tabela 2 resume as configurações.

Tabela 2. Configurações de ajuste. Contagens de funções do treino usadas por receita; épocas executadas e época selecionada; horas de treino registradas. As horas não representam orçamento igual entre receitas. O custo financeiro das rodadas foi migrado para o Material Suplementar (Seção S5).

| Configuração | Vulneráveis | Não vulneráveis | Épocas | Selecionada | Treino (h) |
| --- | --- | --- | --- | --- | --- |
| 3B 1:1 | 5574 | 5574 | 3 | 1 | 3,37 |
| 3B proporção original | 5574 | 178853 | 1 | 1 | 10,16 |
| 3B 1:1 + tamanho | 5574 | 5574 | 3 | 3 | 4,98 |
| 7B 1:1 + tamanho, semente 1 | 5574 | 5574 | 3 | 3 | 7,89 |
| 7B 1:1 + tamanho, semente 2 | 5574 | 5574 | 3 | 2 | 7,89 |
| 7B 1:1 + tamanho, semente 3 | 5574 | 5574 | 3 | 3 | 7,91 |

Como as receitas diferem em composição, número de exemplos, épocas e duração, a comparação entre elas é descritiva. Ela não identifica efeito causal do balanceamento, do controle de tamanho ou da escala.

### 3.4. Seleção de época, implantação e recursos

Nas execuções originais, a época de cada classificador foi escolhida pela ordenação pareada estrita nos 562 pares de validação, contando empates como erro, e a AUC em uma amostra da validação global (699 vulneráveis e 2.796 não vulneráveis) serviu de critério de desempate. Depois, os empates passaram a receber meio crédito, como na métrica definida na Seção 3.5. Nos quatro treinos com controle de tamanho, os registros por época permitiram reconstruir retrospectivamente a seleção com esse critério, e a época escolhida não mudou. Nas receitas 3B 1:1 e de proporção original, os empates por época não foram registrados, e os checkpoints históricos foram mantidos (Material Suplementar, Seção S6); a configuração de proporção original teve uma única época.

Cada checkpoint 7B selecionado foi avaliado em duas implantações. Na implantação NF4, a base permaneceu quantizada e o adaptador separado; na implantação BF16, a base foi carregada em BF16 e o adaptador foi mesclado aos pesos. As duas compartilham semente e época, mas diferem em dois aspectos ao mesmo tempo: a representação da base e a incorporação do adaptador. Por isso, são tratadas como configurações completas de implantação, e não como um experimento que isola a quantização.

Os recursos foram registrados nas execuções originais em uma GPU NVIDIA A40, com PyTorch e Transformers (versões no Material Suplementar, Seção S11), lotes de até 32.768 tokens, incluindo preenchimento, e contexto de 2.048 tokens. A memória é a memória CUDA alocada, em GB decimais, medida após a carga do modelo. O pico foi reiniciado após a carga e a eventual mesclagem e observado durante a pontuação da validação, do teste e dos pares; por isso, pode não incluir o pico transitório da mesclagem. O tempo por função é o tempo de pontuação do teste dividido pelo número de funções, ou seja, um tempo amortizado em lotes, e não a latência de uma requisição individual. O custo estimado multiplica esse tempo pelo preço histórico de US$ 0,50 por hora de GPU e não corresponde a faturamento.

### 3.5. Regras de decisão e métricas

A decisão dos classificadores e da heurística segue a regra \(s > t\), em que \(s\) é o escore e \(t\) o limiar. Dois limiares foram calibrados na validação global completa, cada um com uma finalidade. O primeiro maximiza F1 e serve às métricas globais e às categorias pareadas. O segundo é o menor limiar, entre os escores das \(n\) funções não vulneráveis da validação, que pela regra \(s > t\) admite no máximo \(\lfloor 0{,}005\,n \rfloor\) falsos positivos, o que mantém a taxa de falsos positivos (FPR) em no máximo 0,5% na validação; ele aproxima o cenário de poucos falsos alarmes do VD-Score e serve para medir a taxa de falsos negativos (FNR) no teste global. Ambos foram aplicados ao teste sem recalibração. Como o segundo limiar foi escolhido na validação, a FPR observada no teste pode ultrapassar 0,5% e é reportada junto à FNR. O procedimento separa calibração e teste e usa desigualdade estrita, ao passo que a implementação oficial do VD-Score escolhe o ponto na própria curva ROC do conjunto avaliado; por isso, os valores locais não reproduzem o VD-Score oficial.

No teste global, foram calculados F1, precisão, revocação, FPR e AUC ROC; a AUC só se aplica às configurações com escore. No teste pareado, cada par recebe uma de quatro categorias, segundo as decisões sobre a versão vulnerável e a corrigida, nessa ordem: P-C, (1,0), ambas corretas; P-V, (1,1), ambas vulneráveis; P-B, (0,0), ambas não vulneráveis; e P-R, (0,1), decisões invertidas. As categorias dependem do limiar. A ordenação pareada, ao contrário, independe de limiar e resume a frequência com que a versão vulnerável recebe escore maior que a corrigida, dando meio crédito aos empates:

\[A_{\text{par}} = \frac{1}{N}\sum_{j=1}^{N}\left[\mathbf{1}(s_{v,j} > s_{c,j}) + \tfrac{1}{2}\,\mathbf{1}(s_{v,j} = s_{c,j})\right]\]

em que \(s_{v,j}\) e \(s_{c,j}\) são os escores da versão vulnerável e da corrigida no par \(j\), e \(N = 564\). Por causa do meio crédito, \(A_{\text{par}}\) não é a fração de pares em que a versão vulnerável recebeu escore maior, e um escore sem relação com as versões tende a 50%. Valores abaixo de 50% indicam que, entre os pares sem empate, a versão corrigida recebeu escore maior com mais frequência que a vulnerável. Ordenar bem os pares não implica entendimento do código, e uma ordenação favorável não garante que o limiar produza a categoria P-C.

### 3.6. Análise estatística e sensibilidades

No 7B, a variação entre treinamentos foi descrita pelos valores de cada semente, pela média e pelo desvio padrão amostral das três execuções; as configurações 3B não foram agregadas como repetições. A incerteza amostral da ordenação no teste foi estimada por *bootstrap* percentil de 95% com 10.000 réplicas. A unidade reamostrada foi o grupo projeto/commit: os 550 grupos foram sorteados com reposição, mantendo todos os pares de cada grupo, como no *bootstrap* de agrupamentos discutido por Field e Welsh (2007). As propriedades desse procedimento dependem do modelo de dependência considerado, e a dependência entre commits do mesmo projeto não foi eliminada. Em cada réplica, os mesmos grupos foram usados para todas as configurações e sementes, o que permite calcular a diferença NF4 − BF16 de forma pareada. Os intervalos são condicionais aos três modelos treinados e não descrevem a variação de treinamentos futuros. As três sementes também não triplicam o tamanho da amostra para 1.692 pares. Não foram realizados testes de hipótese.

Duas sensibilidades retrospectivas acompanham a análise principal. A primeira restringe a ordenação aos 465 pares sem truncamento. A segunda remove cinco pares cuja correspondência não representa a correção da mesma função (Seção 4.4); sua interseção com o recorte sem truncamento contém 460 pares. Ambas alteram a composição do teste e não substituem os 564 pares oficiais como referência.
