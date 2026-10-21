# Matriz efetivamente conferida da introdução

Texto canônico: `texto/secoes/introducao_01.md`, v003, SHA256 `bb424d8ba924f3f15fb9421f9dee0e850f3db61d7b6a953cb5f3c70b1e5b6edb`. Conferência: Codex, 07/10/2026. Há 25 checagens com alegação literal, fonte, localizador e alcance em [verificacao_integracao.json](../revisao/introducao_2026-10-07/verificacao_integracao.json), preservadas também como entrada do controlador na integração.

| Bloco da narrativa | Evidência | Decisão de escrita |
|---|---|---|
| Limites de acurácia/F1; global/pareado; FNR/FPR | Ding, PDF pp. físicas 2 e 6 | Manter com atribuição; nenhum desempenho ou limite de FPR local anunciado |
| Funções C/C++, rotulação, deduplicação e split temporal | Ding, PDF pp. 1–2 e 5–6 | Descrever o benchmark; não certificar a release histórica nem descontaminação do pré-treino |
| Dificuldade vulnerável/corrigida e características sem relação com vulnerabilidade | Risse, p. física 2/impressa 4247 e p. física 14/impressa 4259 | Limitar às técnicas/dados estudados; não usar como resultado Qwen local |
| TrapEval, V2P/V2N, raciocínio e inclusão de Qwen | Huang, PDF pp. 2, 4, 7–8 | Reconhecer sobreposição; explicitar diferenças do desenho; não diagnosticar Semantic Trap nos dados locais |
| Qwen, LoRA, QLoRA e NF4 | Hui p. 1; Hu pp. 1 e 4; Dettmers pp. 1 e 4 | Descrever conceitos necessários; não transferir equivalência/eficiência ao estudo |
| Braços e existência de execuções | CSVs históricos, receitas JSON e código lidos | Manter prompting, referência de tamanho, pilotos 3B/uma seed, receita 7B/três seeds e avaliações NF4/BF16; sem estatística reconstruída |
| Cabeça classificatória/escores versus geração do TrapEval | classificador.py 58–73 e 120–132; Huang pp. 4 e 7–8; avaliação 07, 66–68 | Contraste concreto e explícito, sem reivindicar novidade |
| Decisões pareadas versus ordenação | classificador.py 199–244 | Definir os dois objetos e restringir ordenação aos classificadores com escores disponíveis |
| Recursos e NF4/BF16 | avaliação 07, 113–157; CSV de seis avaliações 7B | Comparação completa de implantação; recursos vinculados às medições, sem números ou conclusão de eficiência |
| Caráter exploratório e acesso ao teste | PLANO_EXECUCAO, seção 3 | Declarar; não apresentar confirmação independente |
| Poucas seeds e escopo parcial de quantização | PLANO_EXECUCAO, seções 1 e 3, P3 | Limitar generalização; sem arquitetura nova, AWQ/GPTQ/energia/Pareto ou implantação ótima |

Essa matriz não altera a matriz de planejamento congelada na rodada, nem as notas históricas. Foram excluídos desta introdução: números de qualidade, intervalos/p-valores não reproduzidos, superioridade causal de escala, eliminação de atalhos, ausência de contaminação, equivalência NF4/BF16 e pioneirismo bibliográfico. Contribuição declarada: reunião descritiva do bloco documentado, sem anúncio de achados não auditados.

Dados originais, identidade dos pares, reconstrução de limiares/métricas e auditoria/comparabilidade dos recursos permanecem como tarefas do artigo. Aprovar essa narrativa não atesta resultados ainda não consolidados.
