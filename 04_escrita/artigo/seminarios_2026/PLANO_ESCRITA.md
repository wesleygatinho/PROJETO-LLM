# Plano de escrita do artigo completo

Referência: [plano técnico](../../../01_planejamento/artigo_seminarios_2026/PLANO_EXECUCAO.md). Recorte: estudo empírico exploratório do bloco Qwen já executado. Padrão de redação e template definidos em 07/10/2026 após consulta Codex–Claude, conforme a solicitação do pesquisador.

## 1. Decisões editoriais e pendências

**Definido:** redação em português acadêmico brasileiro orientada pelos artigos indicados na pasta `artigos anselmo`; template SBC local; Abstract em inglês e Resumo em português; referências autor–ano pela base `sbc.bst`. O [guia de escrita](PADRAO_ESCRITA.md) trata de progressão, coesão, coerência, verbos, voz e interpretação; a [amostra original](AMOSTRA_REDACAO.md) demonstra sua aplicação sem fabricar resultados.

**Ainda a definir:** limite de páginas e regras do professor, autoria/afiliação, título definitivo, ferramenta de edição e duração/formato da apresentação. Base LaTeX de formatação preservada em [template_sbc](template_sbc/README.md); o arquivo `.tex` do projeto PLN já contém outro artigo e não será usado como fonte vazia.

A organização das seções depende do conteúdo e das regras finais. Fundamentação e trabalhos relacionados podem ser combinados; resultados e discussão podem ficar juntos; ameaças à validade podem integrar a discussão. O corpus orienta também a construção da prosa e não estabelece uma sequência rígida de tópicos. A redução editorial não autoriza omitir decisões metodológicas essenciais.

## 2. Linha argumentativa

O problema é avaliar classificadores de vulnerabilidade em condições nas quais métricas globais, prevalência baixa, pares vulnerável/corrigida e recursos computacionais precisam ser interpretados juntos. O artigo relata o que aconteceu nas configurações efetivamente executadas, incluindo pilotos e limitações; não precisa apresentar um modelo novo para ter uma estrutura científica completa.

Contribuições candidatas, a confirmar pela consolidação:

1. Caracterização conjunta de desempenho global e pareado das configurações Qwen disponíveis, com baseline explícito de tamanho e políticas de decisão documentadas.
2. Descrição da dispersão observada entre três seeds do 7B e da sensibilidade dos resultados pareados a empates/truncamento.
3. Comparação descritiva de qualidade e recursos entre NF4 com adaptador e BF16 mesclada, limitada ao ambiente e às medições disponíveis.

A relação com trabalhos anteriores deverá ser estabelecida antes de afirmar novidade. Uma replicação ou caracterização delimitada é uma posição possível para o artigo da disciplina. Não alegar contribuição inédita porque agentes concordaram ou porque o protocolo antigo a antecipava.

## 3. Estrutura e contrato de cada parte

| Parte | Conteúdo necessário | Evidência/dependência | Critério de conclusão |
|---|---|---|---|
| Título | Objeto, recorte e caráter do estudo | Resultados consolidados + padrão adotado | Não promete benchmark completo ou resultado causal |
| Resumo | Problema, objetivo, método, achados verificados e limites | Manuscrito integral | Cada número e conclusão existe no corpo |
| Introdução | Contexto, problema de avaliação, perguntas e contribuições delimitadas | Leitura primária e matriz de evidências | Explica por que este estudo é necessário sem inventar novidade |
| Fundamentação | Detecção em funções C/C++, geração/classificação, LoRA/QLoRA/NF4 e avaliação | PrimeVul, LoRA, QLoRA, Qwen | Apenas conceitos necessários à compreensão do método |
| Trabalhos relacionados | Diferenças em dados, tarefas, modelos, métricas e custo | Núcleo de leitura, especialmente PrimeVul, Risse e Huang | Comparações não tratam números de protocolos diferentes como competição direta |
| Método | Dataset/release/splits; modelos/revisões; prompting; receitas; seleção; implantação; métricas; estatística; ambiente | P0–P3 + código atual | Outro pesquisador entende quais decisões foram tomadas e quais fontes faltam |
| Resultados | Dados de integridade; prompting; pilotos 3B; seeds 7B; NF4/BF16; sensibilidades essenciais | P1–P4 | Texto distingue resultado medido, agregado, diagnóstico e indisponível |
| Discussão | Relação entre métricas, composição das receitas, seeds e recursos; implicações delimitadas | Resultados + literatura | Nenhuma explicação causal é apresentada como demonstrada pelo desenho |
| Ameaças à validade | Seleção exploratória, poucas seeds, truncamento, precisão dos registros, dataset/família única, hardware/motor | Relatórios técnicos | Limites concretos e efeito sobre a interpretação explicitados |
| Conclusão | Respostas às perguntas do artigo e continuidade do roteiro | Resultados/discussão | Não introduz novos números nem declara RQ2 maior concluída |
| Referências | Fontes primárias efetivamente usadas | Metadados verificados em PDFs/páginas oficiais | Toda citação tem entrada correta e vice-versa |
| Material suplementar/apêndice, se permitido | Versões, hashes, parâmetros e tabelas por seed | Manifesto e saídas | Complementa reprodutibilidade sem esconder limitações centrais |

## 4. Método: ordem de exposição proposta

1. Dataset: release original, divisão oficial, prevalência, teste global e pareado; disponibilidade e recuperação local dos dados.
2. Configurações: Instruct/geração versus Base/cabeça de classificação; três receitas 3B; receita principal 7B; seeds e épocas.
3. Seleção e cronologia: melhor época na validação, correção dos empates e verificação retrospectiva de que a época escolhida se manteve; acesso ao teste durante a investigação.
4. Calibração: algoritmo, conjunto usado, regra `>`, limiar zero histórico, limiar de maior F1 no dev e limiar de FPR no dev.
5. Métricas: global versus pareado, P-C/P-V/P-B/P-R versus ordenação; meio crédito para empates; FNR e FPR observado; limites da referência aleatória.
6. Estatística: unidade de reamostragem, comparações dentro da seed, dispersão entre seeds, intervalos condicionais e multiplicidade se houver p-valores.
7. Recursos: hardware, biblioteca/motor, batching, contexto, janela de memória/tempo e preço histórico; diferenças de construção NF4/BF16.
8. Reprodutibilidade: scripts, artefatos e metadados existentes; indisponibilidades declaradas.

Não afirmar que limiar zero equivale exatamente à prevalência 1:1: ele é a regra padrão dos logits; os dados de treino e a calibração explicam sua interpretação, sem identidade matemática garantida.

## 5. Resultados visuais planejados

| ID | Peça | Conteúdo e origem | Prioridade |
|---|---|---|---|
| T1 | Dados e configurações | Contagens/prevalência; contexto; recipe/seed/época; versões/seleção | Essencial; dividir em duas tabelas se necessário |
| T2 | Referência de prompting | F1, precisão, revocação, FPR e categorias pareadas na regra registrada | Essencial; tempos em bloco próprio |
| T3 | Qualidade global | Baseline + três pilotos + 7B por seed/variante; F1 calibrado, AUC, FNR no limiar dev e FPR real | Essencial |
| T4 | Qualidade pareada | P-* com política; ordenação ajustada, empates, denominadores e sensibilidade sem truncamento | Essencial; não misturar P-C e ordenação |
| T5 | Recursos de implantação | NF4/BF16 dentro da seed, memória após carga/pico, tempo em lotes e custo histórico estimado | Essencial quando sustentada pelos metadados |
| F1 | Ordenação por seed | Pontos das três seeds 7B e valor único do 3B, com incerteza amostral identificada | Essencial; não desenhar IC de treino inexistente |
| F2 | Recursos e qualidade | Painéis descritivos NF4/BF16 com unidades e condições explícitas | Útil; opcional se T5 já comunica adequadamente |
| F3 | Métricas globais e pareadas | Comparação descritiva por configuração, evitando normalizar métricas diferentes como se fossem iguais | Opcional |
| T6 | Análises adicionais | Faixas de tamanho, correlações, discordâncias e testes, quando reproduzidos | Opcional/suplementar |

Os identificadores serão fixados durante a exportação. Priorizar tabelas legíveis e figuras com função clara; não inserir todas as colunas do CSV em uma tabela. Tabelas canônicas serão CSVs em resultados; exports finais serão gerados no formato editorial escolhido.

## 6. Ordem prática de redação

- Em paralelo a P0/P1: fazer leitura focalizada, levantar trabalhos próximos e preparar contexto/problema com fontes.
- Com o padrão adotado: redigir método a partir das receitas e decisões verificadas, registrando lacunas sem preenchê-las por suposição.
- Conforme P2–P4 forem aceitos: escrever resultados em torno das tabelas oficiais.
- Depois dos resultados: escrever discussão e ameaças; validar correspondência entre alegação e desenho.
- Revisar trabalhos relacionados e posicionamento; finalizar introdução, contribuições e conclusão.
- Por último: título definitivo e resumo, conferindo números contra o corpo e as tabelas.

## 7. Revisão e apresentação

Revisão técnica pelo Codex: números, políticas de limiar, fontes, denominadores, unidades e correspondência entre tabela/figura/texto. Revisão crítica do Claude: força das alegações, estatística, comparabilidade e contradições. Revisão editorial dos agentes e pesquisador: progressão, retomadas, verbos, pessoa, terminologia e proximidade com o padrão adotado, usando o checklist do guia. Revisão do pesquisador: interpretação, autoria, clareza e aderência à disciplina. Revisão docente: solicitar quando houver material concreto e disponibilidade; não presumir aceite ou prazo de retorno.

Manter comentários/decisões em `revisao/`, sem inserir parecer bruto no artigo. Conferir citações no PDF original, porque os markdowns locais foram extraídos por OCR/modelo e podem conter erros.

A apresentação futura deverá percorrer: problema → pergunta/recorte → desenho → resultados essenciais → limitações → continuidade. O tempo e a quantidade de slides serão definidos depois. Preparar um apoio para responder sobre seeds, diferença entre P-C/ordenação, limiares, truncamento, custo e o que ainda não foi executado no roteiro maior. Ensaiar usando a versão final do artigo.

## 8. Critério de prontidão do texto

- Todas as partes essenciais estão presentes e respondem ao recorte.
- Toda alegação empírica possui resultado auditado ou está identificada como hipótese/limitação.
- Nenhum número foi copiado das notas sem reprodução ou justificativa de uso.
- Não há promessa de causalidade, equivalência, ausência de contaminação ou novidade não verificada.
- Normas escolhidas, referências, legibilidade de tabelas/figuras e exportação foram conferidas.
- Artigo e apresentação usam os mesmos resultados congelados.
