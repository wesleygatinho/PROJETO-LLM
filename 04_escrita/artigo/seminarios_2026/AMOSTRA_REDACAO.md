# Amostra original do padrão de redação

Exemplo editorial construído com fatos metodológicos já registrados. Não contém achados numéricos novos nem substitui o manuscrito. Formulações sobre procedimentos e resultados devem ser conferidas contra a consolidação antes de uso final.

> Este trabalho tem como objetivo analisar, de forma exploratória, o comportamento de configurações da família Qwen na detecção de vulnerabilidades em funções C/C++ do PrimeVul. Para isso, o estudo considera tanto as métricas calculadas sobre o conjunto de teste quanto a avaliação de pares formados por uma função vulnerável e sua versão corrigida. A leitura conjunta dessas duas perspectivas permite examinar aspectos distintos do desempenho, enquanto as medições de recursos caracterizam as condições de implantação efetivamente utilizadas.
>
> Nos experimentos com o modelo de 3B parâmetros, foram executadas três receitas de ajuste fino, cada uma com uma única seed: amostragem na proporção de uma função benigna por vulnerável, uso da proporção original dos dados e amostragem 1:1 com controle de tamanho. Para o modelo de 7B, a receita 1:1 com controle de tamanho foi executada com três seeds. A receita 3B na proporção original foi treinada por uma época, enquanto as duas receitas 1:1 foram executadas por três épocas, com volumes distintos de dados. Dessa forma, as diferenças entre as receitas do 3B são interpretadas de maneira descritiva, sem atribuí-las exclusivamente à proporção de classes ou ao controle de tamanho.
>
> A comparação de implantação considera, dentro de cada seed do 7B, a configuração NF4 com adaptador e a configuração BF16 com o adaptador mesclado aos pesos. Como essas configurações diferem tanto na representação dos pesos quanto na incorporação do adaptador, a análise caracteriza as condições completas de implantação. As diferenças de qualidade, memória e tempo serão descritas no alcance das medições disponíveis, sem tratar a comparação como isolamento do efeito da quantização.

## Por que esta amostra aproxima a construção do corpus

- O primeiro parágrafo delimita objetivo e encadeia avaliação/recursos, sem afirmar inovação inexistente.
- O segundo combina ação passada, condições experimentais e uma ressalva que decorre do desenho.
- O terceiro retoma um objeto claro, explica a comparação e limita a interpretação. Seu último período está no futuro porque a consolidação ainda é uma tarefa planejada; no manuscrito final deverá assumir a forma correspondente ao estado efetivamente concluído.
- Os conectivos articulam finalidade, consequência e restrição, sem aparecer obrigatoriamente em todas as frases.
- Predominam impessoalidade e sujeitos concretos, com pretérito para operações e presente para propósito e limitações.
