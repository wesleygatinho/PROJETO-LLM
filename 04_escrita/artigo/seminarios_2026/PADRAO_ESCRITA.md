# Padrão de escrita adotado para o artigo

Decisão editorial solicitada pelo pesquisador em 07/10/2026: aproximar a redação do corpus de artigos indicado, considerando coesão, coerência, construção das frases, verbos e tom acadêmico, e seguir o template SBC local. Guia integrado pelo Codex após consulta e crítica do Claude Opus 5.5.

Fontes e evidências: [análise do corpus](../../../02_referencias/padrao_escrita_anselmo_2026/ANALISE_CORPUS.md). Formatação: [template e proveniência](template_sbc/README.md). Este guia orienta uma redação original; não atribui autoria nem reproduz frases de outro trabalho.

## 1. Decisões editoriais

- Texto principal em **português acadêmico brasileiro**, com Abstract em inglês e Resumo em português conforme o template local para artigos em português.
- Formatação **SBC**, usando a base local preservada. Referências autor–ano conforme `sbc.bst`, com formas narrativas e parentéticas coerentes.
- Tom expositivo e analítico, com foco no problema, nas escolhas metodológicas e na interpretação da evidência.
- Predominância de construções impessoais e sujeitos concretos, como estudo, modelo, conjunto e tabela; preferência editorial, não proibição de primeira pessoa plural.
- Vocabulário técnico definido e consistente; explicação das condições de avaliação junto às conclusões que delas dependem.
- Estrutura de seções adaptável ao conteúdo e às regras da disciplina; limite de páginas, autoria, afiliação completa e título definitivo ainda precisam ser definidos.

O padrão é a referência de redação para as próximas versões. Ele não altera o recorte científico, amplia treinamentos ou valida resultados ainda não consolidados.

## 2. Coerência e progressão

A introdução deve partir do problema específico de avaliação, explicar por que ele exige investigação e chegar ao objetivo do estudo. Afirmações amplas sobre importância ou lacunas precisam de fontes; não abrir com superlativos ou generalidades que nada acrescentem ao objeto.

Cada parágrafo desenvolve uma ideia reconhecível: proposição principal, detalhamento ou evidência e implicação quando pertinente. Um parágrafo pode também apresentar uma transição necessária; não há número fixo de frases, linhas ou conectivos.

Os parágrafos devem construir uma sequência, não uma coleção de fatos. Retomar explicitamente o objeto quando houver risco de ambiguidade: essa regra de decisão, essa diferença de contexto, essa configuração de implantação. Demonstrativos sem referente claro, como isso ou esse resultado quando há vários resultados, exigem revisão.

Organizar procedimento como ação → condição/dado → finalidade → consequência ou limite. Organizar interpretação como evidência → contraste relevante → leitura possível → alcance. Não usar esse esquema como molde obrigatório para todas as frases.

## 3. Coesão e conectivos

| Relação pretendida | Recursos possíveis | Condição de uso |
|---|---|---|
| Enquadramento | Nesse contexto; para essa tarefa | O contexto precisa ser identificável no trecho anterior |
| Finalidade | Para avaliar; com o objetivo de; a fim de | Explicitar por que a operação foi realizada |
| Sequência | Inicialmente; em seguida; por fim | Deve corresponder à sequência efetiva, não à ordem inventada para o texto |
| Contraste/restrição | Contudo; no entanto; embora; diferentemente | Nomear o que muda e sob quais condições |
| Acréscimo | Além disso; também; paralelamente | Acrescentar informação distinta, sem repetir a anterior |
| Consequência | Assim; dessa forma; portanto | A conclusão deve decorrer das premissas, sem esconder um salto causal |
| Precisão | Nesse conjunto; nessa seed; nesse limiar | Restringir o alcance da observação |

Variar esses recursos conforme a relação, sem alternância mecânica por sinônimos. Um parágrafo pode começar diretamente pelo seu sujeito. Conectivos não substituem conteúdo ou ligação lógica.

## 4. Verbos, pessoa e voz

| Função do enunciado | Escolha preferencial | Exemplo original de construção |
|---|---|---|
| Objetivo do artigo | Presente | Este trabalho analisa o comportamento das configurações avaliadas. |
| Definição ou descrição de objeto | Presente | A ordenação pareada compara os scores das duas versões. |
| Operação efetivamente realizada | Pretérito perfeito | Foram treinadas três seeds para a configuração principal do 7B. |
| Decisão metodológica passada | Pretérito + motivo | O limiar foi escolhido na validação para separar calibração e teste. |
| Apresentação de tabela/figura | Presente | A tabela apresenta os resultados por seed. |
| Medida observada | Pretérito ou presente descritivo, conforme o foco | A configuração obteve… / Na tabela, a configuração apresenta… |
| Hipótese explicativa | Modalidade proporcional à evidência | Esse padrão é compatível com…; uma hipótese a investigar é… |
| Limite do desenho | Presente | Uma seed por receita restringe a interpretação das diferenças. |
| Continuidade e plano ainda não executado | Futuro, perífrase ou possibilidade | A comparação será ampliada… / Pretende-se avaliar… |

Não uniformizar todo o método no passado quando ele descreve uma estrutura atual, nem usar futuro para um experimento já realizado. O presente também serve para interpretação; o pretérito relata a ocorrência. A organização do texto pode usar presente, ou futuro metatextual se necessário, sem aparentar trabalho experimental pendente.

Alternar voz ativa e passiva é natural: a tabela apresenta; o modelo recebeu; foram avaliadas as configurações. Consistência refere-se à pessoa narrativa e ao foco, não a usar uma única voz gramatical por seção. Empregar passiva quando a operação importa mais que o executor; escolher sujeito concreto quando isso tornar a frase mais clara. A primeira pessoa plural pode explicitar uma decisão dos autores, mas seu uso deve ser deliberado e estável.

## 5. Objetivo e justificativa

Usar verbos compatíveis com o estudo realizado: avaliar, analisar, caracterizar, comparar, examinar. Apresentar um estudo não equivale a propor uma arquitetura nova. A expressão método proposto só cabe se houver efetivamente uma proposta metodológica correspondente.

O objetivo deve conter objeto, recorte e propósito. A formulação Este trabalho… é próxima ao corpus, mas pode variar; não repetir a mesma abertura em parágrafos consecutivos. O caráter exploratório precisa aparecer claramente, sem ser uma etiqueta que substitua a descrição da cronologia e das limitações.

Justificar escolhas por propriedades pertinentes: disponibilidade de scores, calibragem na validação, correspondência entre checkpoints, custo do erro ou recursos. Não afirmar que uma escolha garante representatividade, remove contaminação ou elimina atalhos apenas porque essa era sua intenção.

## 6. Resultados e discussão

Anunciar a tabela ou figura pelo conteúdo que ela permite examinar. Destacar os contrastes úteis para a pergunta; não recitar todas as células. Apresentar condições, política de decisão, denominador e unidade na legenda, texto ou nota apropriada, sem tornar cada frase uma repetição completa do método.

Separar medida, interpretação e hipótese. Indica ou sugere não tornam uma explicação causal demonstrada. Demonstrou, comprovou, garante, equivalente e superior exigem alcance sustentado pelo desenho; não são palavras proibidas, mas não podem ampliar o que foi medido. Diferença numérica pode ser descrita como tal, sem significância ou superioridade geral implícitas.

Resultados limitados ou negativos recebem o mesmo cuidado que resultados favoráveis. Evitar qualificação automática como promissor, robusto, eficiente ou satisfatório. Explicar em que aspecto a configuração atende ou não à pergunta, com a métrica e o contexto.

No estudo atual: separar os pilotos 3B da variação entre seeds do 7B; distinguir categorias pareadas e ordenação; explicitar calibração e FPR real; interpretar NF4/BF16 como configurações de implantação. Comparações externas precisam esclarecer diferenças de dados, tarefa, contexto e protocolo.

## 7. Terminologia

| Adotar no texto | Distinção necessária |
|---|---|
| Conjunto de validação (dev), definido na primeira ocorrência | Não alternar desenvolvimento/validação sem esclarecer que é o mesmo conjunto |
| Seed, definida como semente de aleatoriedade | Usar uma convenção consistente; não tratar seed como nova amostra independente do teste |
| Categorias pareadas P-C/P-V/P-B/P-R | São desfechos de decisão das duas versões; não ordenação contínua |
| Ordenação pareada com meio crédito para empates | Não chamar de P-C ajustado |
| Limiar de maior F1 na validação | Diferente do limiar escolhido para limitar FPR na validação |
| FNR no limiar calibrado no dev e taxa de falsos positivos (FPR) observada no teste | Não alegar FPR≤0,5% no teste se o valor medido ultrapassa esse limite |
| NF4 com adaptador; BF16 com adaptador mesclado | Não apresentar a comparação como PTQ completa AWQ/GPTQ/NF4 |
| Memória alocada após carga; pico na janela medida | Diferentes de memória reservada ou capacidade da GPU; delimitar GPU e ambiente medidos |
| Tempo amortizado por função em lotes | Diferente de latência individual, TTFT ou TPOT; delimitar GPU, ambiente e condições de medição |

Definir siglas e termos ingleses relevantes na primeira ocorrência. Usar itálico para estrangeirismos comuns de forma consistente; nomes próprios de modelos, métricas e bibliotecas não precisam de tratamento como palavras traduzíveis. Não introduzir um glossário interminável de termos que o artigo não utiliza.

## 8. Citações e peças visuais

Referência narrativa: autor integrado à frase com ano; referência parentética: fonte próxima da afirmação. O estilo SBC local organiza apresentação autor–ano. Verificar metadados e a proposição realmente sustentada; não transportar referências científicas dos artigos de estilo por conveniência.

Tabelas e figuras devem ser chamadas e interpretadas no texto, com legenda informativa. Tabelas: legenda acima. Figuras: legenda abaixo na implementação do manuscrito. Arredondamento, casas decimais e unidades devem corresponder à precisão/reprodutibilidade, preservando valores de trabalho completos nas saídas.

Resumo e Abstract terão o mesmo conteúdo científico e grau de cautela, respeitando até dez linhas cada na primeira página, conforme o template local. Não fixar limite de palavras como substituto do limite de linhas renderizadas.

## 9. Processo de revisão editorial

Revisão por seção: primeiro correspondência com evidência; depois progressão e clareza; em seguida verbos, pessoa, terminologia e citações; finalmente diagramação SBC. Codex integra revisões; Claude critica versões concretas; pesquisador decide e responde pelo texto.

Checklist:

- [ ] Objetivo, recorte e contribuição estão claros e sustentados.
- [ ] Os parágrafos têm foco e se encadeiam sem retomadas artificiais.
- [ ] Pronomes/demonstrativos possuem referentes identificáveis.
- [ ] Conectivos exprimem relações reais; portanto não encobre hipótese.
- [ ] Tempo verbal distingue definição, execução, interpretação e plano.
- [ ] Pessoa narrativa é consistente; voz ativa/passiva serve à clareza.
- [ ] Decisões técnicas têm motivo e limites explícitos quando pertinentes.
- [ ] Valores e comparações possuem condições, política, unidade e denominador acessíveis.
- [ ] P-C/ordenação, seeds/amostras e NF4/BF16 continuam distintos.
- [ ] Hipóteses e ausência de significância não viraram causalidade/equivalência.
- [ ] Referências, tabelas e figuras participam da argumentação.
- [ ] Termos são consistentes, siglas estão definidas e traduções não distorcem o conceito.
- [ ] Não há transcrição extensa de frases, erro de extração ou conteúdo alheio trazido do corpus.
- [ ] Resumo/Abstract e exportação obedecem ao template e às regras finais da disciplina.

Uma [amostra original de redação](AMOSTRA_REDACAO.md) demonstra estas escolhas. Ela é ilustrativa, não um trecho final já validado do artigo.

Itens sobre números, políticas de limiar, FPR/FNR, empates e comparações só podem ser concluídos após as verificações P2–P4 do plano técnico. A aprovação do guia de estilo não marca esses itens como cientificamente concluídos.
