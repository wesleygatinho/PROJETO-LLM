# Plano de implementação e fechamento do artigo de Seminários

Data-base: 07/10/2026. Entrega e apresentação: 11/11/2026. Estado do projeto examinado: `5b4b969d3643f30c80e2678f67efdce1e24d67dd`. A revisão histórica de cada execução ainda deverá ser identificada quando houver registro; este commit não pode ser atribuído retroativamente a todas as rodadas.

## 1. Resultado pretendido

Produzir um artigo completo, com problema, fundamentação, método, resultados, discussão, limitações, conclusão e referências, sobre **o bloco Qwen já executado**. O artigo apresentará uma caracterização exploratória da qualidade de classificação e dos recursos observados nas configurações avaliadas. Não é necessário terminar a matriz experimental da dissertação para concluir esse artigo.

Pergunta central proposta: **Como os classificadores Qwen avaliados se comportam nas métricas globais e pareadas do PrimeVul, e quais recursos exigem as configurações de implantação executadas?**

Subperguntas operacionais:

- Q1: Como prompting, receitas exploratórias de ajuste e baseline de tamanho se comportam no teste global e no teste pareado, com regras de decisão explícitas?
- Q2: Qual variação foi observada entre as três seeds do 7B na receita principal?
- Q3: Quais diferenças de qualidade e recursos foram observadas entre NF4 com adaptador e BF16 mesclada, para os checkpoints correspondentes do 7B?

Estas perguntas delimitam a entrega da disciplina e não substituem as RQs da pesquisa maior. O eixo qualidade × recursos permanece, mas os dados atuais não respondem à comparação completa AWQ/GPTQ/NF4, à energia, a um ponto ótimo de implantação ou a uma curva completa de Pareto.

## 2. Material existente e estatuto de cada resultado

| Bloco | Evidência disponível | Uso no artigo |
|---|---|---|
| Prompting 3B/7B Instruct | Quatro logs da release original; resultados globais e pareados | Referência descritiva; 8.192 tokens, geração e política YES/NO documentadas |
| Baseline de tamanho | Linha de resultados e logs de teste global/pareado | Controle descritivo; reconstrução da calibração ainda depende dos dados de validação |
| 3B 1:1 sorteado | Uma seed, receita e logs de avaliação | Piloto exploratório |
| 3B proporção real | Uma seed, receita e logs de avaliação | Piloto exploratório; uma época, distinto do orçamento dos outros braços |
| 3B 1:1 com controle de tamanho | Uma seed, receita e logs de avaliação | Piloto exploratório e referência descritiva para o 7B |
| 7B 1:1 com controle de tamanho | Três seeds; receitas e avaliações NF4/BF16 | Bloco principal com resultados por seed e agregações explicitamente definidas |
| NF4 versus BF16 do 7B | Seis avaliações correspondentes | Comparação de configurações de implantação; não isola apenas os bits, pois também muda o merge |

**Já implementado antes deste plano:** ordenação com meio crédito para empates; gravação do F1 no limiar escolhido na validação. Preservar colunas históricas e novas definições. Não reabrir essas correções como se estivessem ausentes.

**Ainda não demonstrado:** reprodução das estatísticas das notas por um procedimento versionado; integridade documental de todos os pares; comparabilidade completa dos recursos; rastreabilidade de todas as afirmações às fontes.

**Dependência local constatada:** `03_experimentos/dados/` contém apenas `.gitkeep`. Os registros indicam a release original, mas os dados deverão ser recuperados e conferidos antes da auditoria definitiva. Checkpoints remotos não foram acessados nesta etapa; sua disponibilidade não deve ser presumida.

O CSV atual da etapa 3 contém **10 linhas de dados**: baseline, três pilotos 3B e seis avaliações 7B. Seus totais registrados não indicam perda de cobertura pareada, mas não certificam identidade nem substituem auditoria dos logs e dados completos.

## 3. Limites do recorte

Para esta entrega, não são requisitos: novos treinos 3B/7B, UniXcoder, StarCoder2, DeepSeek, AWQ/GPTQ/INT8, QA-LoRA, perturbações, novos benchmarks, energia ou novas medições com vLLM. Esses itens permanecem no roteiro maior, com prioridades a retomar depois do artigo.

O artigo deve expor que o desenvolvimento foi exploratório e teve acesso ao teste durante a investigação. A seleção de época e limiar pela validação deve ser documentada, sem transformar retrospectivamente o estudo inteiro em confirmação independente. Divisão temporal e deduplicação do dataset não comprovam ausência de contaminação do pré-treinamento dos modelos.

Registrar especificamente a mudança retrospectiva para meio crédito nos empates em 06/10. As planilhas indicam que as melhores épocas permaneceram as mesmas; P2 deverá reproduzir essa conferência a partir dos registros por época antes de afirmar isso no artigo. Não sugerir que todas as decisões históricas já usavam o critério corrigido.

Diferenças entre 3B e 7B não isolam causalmente o efeito da escala: os pilotos têm uma seed, diferentes receitas e, em um braço, diferente número de épocas. NF4/BF16 mede a configuração completa disponível. Correlação baixa com tamanho não comprova ausência de outros atalhos.

## 4. Sequência de trabalho

### P0 — Inventário e recuperação das fontes

Entradas: CSVs atuais, logs, receitas JSON, código e fontes primárias locais. Recuperar a **mesma release original**, preferencialmente a cópia já usada pelo pesquisador ou a fonte oficial registrada em `00_baixar_primevul.py`. Não executar novamente inferência para recuperar dados.

Criar manifesto com identificador da execução, modelo/revisão, receita, seed, época, precisão, contexto, split, paths, contagens, GPU/motor, versões, hashes atuais completos e hashes históricos disponíveis. Registrar separadamente revisão histórica ausente, hash histórico abreviado e hash completo calculado agora. Identificar rodadas oficiais; excluir depuração, `v01/` e `descartados/` da análise principal, mantendo a justificativa e os registros.

**Aceite:** cada resultado candidato aponta para sua fonte; ausências estão enumeradas; dados recuperados batem com contagens e impressões digitais históricas disponíveis. Contagem sozinha não identifica release nem conteúdo. Divergência de hash bloqueia a junção daquele conjunto até esclarecer sua causa.

### P1 — Auditoria de identidade e pareamento

Validar `pos`, `idx`, projeto, commit, alvo e outros identificadores disponíveis. `func_hash` nulo não serve de prova de identidade. A ordem de execução pode diferir da ordem dos dados: usar `pos` conferido contra a fonte, nunca a ordem de leitura do log. Comprovar cobertura esperada de 25.911 funções e 1.128 funções/564 pares de teste, conforme o split; a validação pareada tem 562 pares, não 564.

Conferir unicidade, duplicatas, IDs ausentes, metadados divergentes, rótulos opostos e correspondência oficial de cada par. Um mesmo projeto/commit pode ter várias funções: não parear listas arbitrariamente. Usar consecutividade apenas quando validada contra o arquivo oficial. Não aceitar fallback silencioso nem tolerância percentual a descarte.

Regra concreta a verificar contra o artigo/repositório oficial: membros consecutivos no arquivo da release, alvos {1,0}, mesmo projeto/commit, posições e IDs únicos, nenhuma reutilização indevida. Onde disponíveis, conferir caminho, nome/assinatura e diff da função. Nome igual sozinho não comprova identidade; renomeação, macros ou mudança de assinatura podem ser legítimas, exigindo inspeção documentada em vez de exclusão automática. Gerar `par_id` a partir das duas identidades verificadas, sem inventar um ID oficial inexistente.

**Aceite:** todos os pares incluídos possuem duas versões identificadas e auditadas; eventuais exclusões e denominadores aparecem no relatório. O caminho atual que tolera falhas não deve ser usado como certificação de integridade. Se houver impacto real, recalcular somente resultados derivados com os logs corretos.

**Contingência em 13/10:** se a release exata não estiver acessível, registrar tentativas e esclarecer se a divergência é de serialização ou conteúdo. Comparar hashes históricos abreviados apenas como tal; não substituir dados silenciosamente. Uma reconstrução pelos logs pode apoiar descrição preliminar, identificada como não certificada contra a fonte oficial. Não apresentar p-valores/ICs como confirmação de pares verdadeiros sem identidade demonstrada. Nesse caso, estreitar as alegações afetadas, priorizar resultados verificáveis e registrar a decisão com o pesquisador; a adequação acadêmica do recorte precisará ser discutida com a disciplina/orientação. O bloqueio de uma comparação não deve impedir escrever as partes sustentadas do artigo.

### P2 — Reconstrução das métricas e decisões

Recalcular métricas globais com limiares reconstruídos da validação quando os scores existem; verificar seleção de época contra receitas. Guardar limiar com precisão suficiente, operador `>` e regra de desempate. CSVs e logs arredondados podem produzir diferenças na fronteira: registrar e explicar, sem esconder divergências sob uma tolerância ampla.

Prompting usa a resposta e o parser registrados, sem criar scores contínuos artificiais. Para os classificadores, F1 principal é `f1_limiar_validacao`; a coluna antiga `f1` usa limiar zero. O baseline já grava F1 calibrado na coluna antiga. Mostrar FNR no limiar calibrado no dev junto com FPR realmente observado no teste; se FPR ultrapassar 0,5%, não rotular o ponto como cumprimento de FPR≤0,5% no teste. O resultado com limiar escolhido no teste é diagnóstico de oráculo, separado do principal.

Conferir a implementação própria das métricas contra definições e avaliação oficial do PrimeVul; o protocolo antigo pede script oficial, mas o código atual é próprio. No baseline de tamanho truncado a 2.048 tokens, a planilha registra limiar VD-S de 2.048: pela regra `>`, nenhum score limitado ao teto dispara. Explicar esse resultado como efeito da configuração/teto, sem generalizar que tamanho nunca detecta vulnerabilidades. Recalcular baseline/calibração em CPU escrevendo apenas saídas novas; o script histórico 08 acrescenta linhas à planilha e não deve ser executado sem controlar destinos.

No pareado, distinguir: categorias P-C/P-V/P-B/P-R; ordenação estrita; empates; ordenação com meio crédito. Reproduzir as categorias históricas no limiar original e produzir, como análise derivada, categorias no limiar escolhido no dev, claramente identificadas. Não comparar categorias calibradas do baseline com categorias no limiar zero dos classificadores como se a política fosse idêntica. Para prompting, manter sua própria regra explícita.

**Aceite:** contagens fecham, métricas reproduzem os valores publicados dentro do arredondamento explicado e toda diferença possui diagnóstico. Se precisão histórica impedir reconstrução exata, registrar o limite e avaliar sua consequência antes de propor inferência.

### P3 — Estatística e análises de sensibilidade

Resultados individuais das três seeds são indispensáveis. A média representa três modelos treinados observados, não um ensemble de scores nem nove observações independentes. Para NF4/BF16, comparar dentro da mesma seed/checkpoint. Não agregar os pilotos 3B como repetições de uma mesma configuração.

Separar duas fontes de variação: dispersão entre seeds e incerteza amostral condicional aos modelos treinados. No pareado, bootstrap reamostra pares inteiros e os mesmos índices para as configurações comparadas; para a média das três seeds, mantém o vetor das três previsões de cada par. No teste global, usar reamostragem alinhada por função, estratificada por classe quando necessário, e explicitar a hipótese de independência; verificar agrupamento por commit/projeto para uma sensibilidade se houver recursos. Não misturar o pareado e o teste global como amostras independentes.

Definir famílias de comparações antes de gerar novos p-valores, reconhecendo o caráter retrospectivo. Para ordenação com meio empate, usar diferenças e intervalos por bootstrap pareado. O evento binário complementar de McNemar será **P-C no `limiar_decisao`, escolhido para maior F1 na validação**, e não no `limiar_vds`, comparando NF4/BF16 dentro da mesma seed. Informar discordâncias e teste exato; aplicar Holm à família de três comparações se apresentadas como testes de hipótese. NF4/BF16 calibram esse limiar separadamente; a comparação inclui mudança de score e de calibração. Poucos P-C/discordantes podem reduzir o poder. McNemar/Holm são opcionais no percurso essencial. P-valores históricos exigem reprodução do evento e cálculo originais; um teste novo de outro evento não os valida. Retirar p-valores sem reprodução é preferível a exigir nova execução apenas para mantê-los.

O limiar fica fixo nos intervalos condicionais ao modelo e à calibração observada. Reamostrar validação e recalibrar é extensão, identificada como outra fonte de incerteza. Três seeds não sustentam uma estimativa robusta da população de futuros treinos. Ausência de significância não demonstra equivalência, ausência de sinal ou efeito zero.

Sensibilidades indispensáveis para discutir o pareado: todos os pares versus pares com ambas as versões não truncadas, com denominadores e prevalência dos empates. Scores iguais não provam entradas tokenizadas idênticas; isso exige dados e tokenizer da revisão correta. AUC por faixas de tamanho é descritiva, precisa de faixas definidas e tratamento de faixas sem duas classes; não é demonstração causal de eliminação de atalhos.

**Aceite:** estatísticas geradas por código versionado, parâmetros e unidade de reamostragem registrados; nenhuma inferência excede os limites acima.

### P4 — Recursos e exportação dos resultados

Reproduzir tabelas de treino, memória alocada após carga, pico, tempo amortizado por função e custo computacional calculado a partir do preço histórico registrado. Inspecionar a janela efetiva de medição do pico e do tempo no código: não chamar memória alocada de memória reservada ou total da placa, nem tempo médio em lotes de latência individual, TTFT ou TPOT.

Comparar tempos diretamente apenas nas condições compatíveis. O README atual avisa que tempos de prompting e classificação não são diretamente comparáveis. Para NF4/BF16, apontar ausência de repetições independentes de desempenho; três seeds não são um benchmark controlado de latência. Não extrapolar energia, tarifas atuais ou fatura efetiva.

Produzir tabelas estruturadas, figuras e relatório de divergências em saídas novas. Congelar a versão validada para alimentar o texto; toda revisão posterior deve regenerar as saídas e indicar sua origem.

**Aceite:** cada tabela/figura possui fonte, regra, denominador, unidade e script; figuras de qualidade e recursos não sugerem comparação causal indevida.

### P5 — Escrita, revisão e apresentação

Começar problema, fundamentação e método enquanto P0–P2 avançam. Fechar resultados depois dos respectivos aceites; discussão deve seguir evidências, não notas antigas tomadas como conclusão final. O [plano de escrita](../../04_escrita/artigo/seminarios_2026/PLANO_ESCRITA.md) define o conteúdo e aponta o guia editorial adotado em 07/10, com redação orientada pelo corpus indicado e template SBC local.

Antes de fechar as contribuições, conferir no PDF o estudo local de Huang sobre *Semantic Trap*, além de PrimeVul e Risse. A sobreposição potencial pede posicionamento cuidadoso, não expansão automática de treinos. O [cronograma](CRONOGRAMA_CHECKLIST.md) distingue percurso completo (~72h) e essencial (~50h), sem garantia de produtividade ou cumprimento.

Solicitar revisão docente com uma versão concreta, se houver disponibilidade, e prever uma revisão técnica pelo pesquisador mesmo sem retorno externo. Preparar apresentação usando somente tabelas e conclusões do artigo validado.

## 5. Gatilhos para nova execução

| Lacuna encontrada | Primeira resposta | Quando GPU pode ser necessária |
|---|---|---|
| Dados locais ausentes | Recuperar release e conferir identidade | Não é necessária para isso |
| CSV diverge dos logs | Recalcular em CPU, diagnosticar limiar e arredondamento | Somente se scores essenciais forem irrecuperáveis e a conclusão depender deles |
| Pares mal associados | Reconstituir associação oficial e recalcular | Somente se faltar previsão de um membro essencial |
| Falta log de calibração do tamanho | Recontar tokens no dev com tokenizer correto, em CPU | Não é necessária |
| Falta revisão do tokenizer | Procurar registro/cache/versionamento; registrar limite | GPU não resolve metadado histórico ausente |
| Falta medição repetida de tempo/energia | Limitar a afirmação aos recursos observados | Apenas se o pesquisador decidir ampliar o recorte |
| Checkpoint não acessível | Recuperar artefato existente ou retirar a comparação afetada | Não iniciar novo treino automaticamente |

Reinferência, se indispensável, usa checkpoint existente e um escopo diagnosticado. Novo treino só entra por decisão explícita do pesquisador após justificar a lacuna, custo e impacto no prazo. Retirar uma afirmação não sustentada é uma alternativa válida à expansão de experimentos.

## 6. Critério final de conclusão

- [ ] Resultados oficiais identificados e divergências resolvidas ou limitadas explicitamente.
- [ ] Integridade dos pares e das junções demonstrada, sem descarte silencioso.
- [ ] Métricas, limiares, seeds e intervalos definidos sem ambiguidades.
- [ ] Conclusões e referências vinculadas às evidências da matriz de escrita.
- [ ] Artigo completo no padrão de redação e template SBC adotados, revisado e exportado.
- [ ] Apresentação consistente com o artigo, ensaiada e pronta para 11/11.

Orçamento adicional planejado de GPU: **US$ 0** no percurso de consolidação local. Não inclui armazenamento/Pods já ativos, consumo de serviços de IA ou uma eventual reinferência aprovada. Este plano não verifica a disponibilidade financeira nem promete aceitação/publicação.
