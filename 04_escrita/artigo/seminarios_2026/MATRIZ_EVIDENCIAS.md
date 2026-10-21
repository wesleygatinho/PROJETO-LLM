# Matriz de evidências, referências e decisões de redação

**Estado: planejamento.** As linhas abaixo definem o que verificar; não declaram auditoria completa nem leitura integral já realizada. Acrescentar durante a execução: arquivo/versão, página ou identificador exato, resultado reproduzido, decisão e data.

## 1. Alegações candidatas

| Alegação/tema | Fonte interna inicial | Verificação necessária | Regra de redação |
|---|---|---|---|
| Composição e prevalência do PrimeVul | CSVs, downloader, NOTAS | Recuperar release, conferir hashes e contagens; artigo/repositório oficial | Nomear release e splits, sem confundir com v0.1 |
| Prompting 3B/7B no teste | CSV etapa1/pareado + quatro logs | Recalcular contagens, parser e cobertura | Comparação limitada às configurações executadas |
| Baseline tamanho versus modelos | CSV etapa3 + logs tamanho/classificador | Mesmo procedimento de calibração, métricas reconstruídas e limiares explícitos | Não afirmar que o baseline supera todos os modelos |
| Pilotos 3B e composição de treino | Receitas, CSV treinos e logs | Seeds, épocas, volumes e controle de tamanho | Receitas exploratórias; não efeito causal isolado da proporção |
| Diferenças 3B/7B | Piloto 3B + três seeds 7B | Dispersão e IC condicionais; desenho desigual | Não afirmar superioridade geral de escala nem equivalência |
| Ordenação próxima da referência aleatória | Logs pareados | Integridade, empates e intervalos; pressuposto de simetria | Descrever valores/intervalos; não provar ausência de compreensão |
| P-C/P-V/P-B/P-R | Código 04/classificador e PrimeVul | Definição oficial, orientação e política de limiar | Não chamar ordenação ajustada de P-C ajustado; acaso 25% não é universal |
| FNR no limiar dev | Validação/teste, algoritmo e CSV | Limiar, operador e FPR efetivamente observado | Se FPR teste exceder 0,5%, declarar o excesso |
| VD-S do tamanho com teto 2.048 | CSV baseline + script 08 | Conferir clipping, limiar no teto e decisões resultantes | Resultado da configuração truncada, não incapacidade universal do tamanho |
| NF4 versus BF16 | Seis logs/linhas 7B + código 07 | Correspondência de checkpoint e construção; diferenças e IC | Comparação de implantação, não isolamento puro da quantização |
| Memória/tempo/custo | CSVs e janela de medição no código | Alocado versus pico; amortizado versus latência; preço histórico | Sem energia ou fatura efetiva inventadas; separar prompting/classificação |
| Truncamento e empates | Campos dos logs + dados/tokenizer | Contagens, métricas sem truncamento e, se alegado, igualdade de entradas | Scores iguais não provam entradas idênticas |
| AUC por faixas, quartis, acertos comuns | NOTAS e logs | Script reproduzível ou retirada | Não transportar automaticamente números das notas |
| P-valores e IC históricos | NOTAS etapa3 | Evento, dados e algoritmo exatos ou retirada | Novo teste de outro evento não valida p-valor antigo |
| Ausência de contaminação | Protocolo antigo + fontes de dataset/modelos | Limites de split/deduplicação e dados de pré-treinamento | Não afirmar garantia de descontaminação |
| Novidade/contribuição | Protocolo antigo + literatura | Leitura primária, sobreposições e busca focalizada datada | Posicionar como caracterização/replicação quando apropriado |

## 2. Núcleo primário de leitura

Os nomes/anos abaixo identificam os arquivos locais; ano de publicação, versão, DOI e veículo devem ser conferidos na fonte primária antes de montar a bibliografia. A inspeção de um título/trecho em OCR não equivale a leitura integral do PDF.

| Fonte local | PDF em `02_referencias/pdfs das referencias/` | Uso planejado |
|---|---|---|
| Ding — PrimeVul | `Datasets e benchmarks/Ding, Y - 2024.pdf` | Dataset, splits/releases, P-* e VD-S; conferir definição contra implementação própria |
| Risse & Böhme | `Ref Adicionadas/Niklas Risse - 2024.pdf` | Limites de avaliação e interpretação dos detectores |
| Huang — Semantic Trap | `Deteccao de vulnerabilidade métodos e modelos/Feiyang Huang - 2026.pdf` | Prioridade alta: investigar sobreposição com conclusões sobre ajuste e avaliação pareada |
| Dettmers — QLoRA | `Eficiência quantizacao PEFT e destilacao/Dettmers, T - 2023.pdf` | NF4, adaptação e distinção entre treino quantizado e implantação |
| Hu — LoRA | `Eficiência quantizacao PEFT e destilacao/Hu, E - 2021.pdf` | Método de adaptação usado no pipeline |
| Hui — Qwen2.5-Coder | `Modelos de código/Hui, B - 2024.pdf` | Modelos, variantes e configuração compatível com revisões usadas |

Leitura focalizada das seis fontes é necessária mesmo no percurso essencial; priorizar método/resultados/limitações relevantes, conferidos no PDF. No percurso completo, aprofundar e adicionar apenas fontes que expliquem diferenças concretas: Steenhoek, Vul-RAG/PairVul e outros estudos locais pertinentes. Não assumir que todas as referências da biblioteca precisam entrar no artigo.

Fontes de bootstrap, McNemar exato e Holm: localizar documentação/papers primários adequados e registrar definição e referência. Não foram validadas bibliograficamente nesta etapa. Se McNemar/Holm forem retirados do percurso essencial, não manter essas técnicas no método do texto.

## 3. Procedimento de leitura e verificação

Para cada fonte usada, registrar título, autoria, ano/versão, DOI ou página oficial, caminho local, páginas relevantes, afirmação sustentada e limites de comparação. Usar os markdowns de `02_referencias/pdf_to_markdown/markdown_output/` para localizar conteúdo; conferir no PDF toda afirmação/citação que será incorporada.

Comparar estudos por dataset/release, tarefa, tipo de modelo, contexto, treinamento, seeds, métrica, limiar e hardware/motor. Números de artigos diferentes não são uma comparação controlada com os resultados locais.

## 4. Verificação de posicionamento

- Ler Huang, PrimeVul e Risse antes de fechar as contribuições da introdução.
- Registrar o que é reprodução, diferença de configuração, controle adicional, caracterização de recursos e ponto ainda sem evidência.
- Fazer busca focalizada em fontes primárias para verificar trabalhos próximos e metadados; registrar data e consultas, sem prometer revisão sistemática.
- Não reutilizar as alegações amplas do protocolo antigo sobre quantização inédita ou curva completa para este recorte.
- Caso a sobreposição seja grande, posicionar o artigo como replicação/caracterização exploratória; não aumentar experimentos automaticamente para fabricar novidade.

## 5. Registro de decisões a preencher

| ID da alegação | Fonte exata e versão | Resultado/conferência | Decisão: manter, limitar ou retirar | Responsável/data |
|---|---|---|---|---|
| A preencher durante a consolidação | — | — | — | — |

A redação final deve seguir este registro. Notas históricas permanecem preservadas; correções de interpretação serão registradas aqui e nos relatórios de consolidação, sem reescrever o histórico como se as decisões sempre tivessem sido as atuais.
