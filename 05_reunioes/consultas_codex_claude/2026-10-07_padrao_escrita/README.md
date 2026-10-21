# Definição do padrão de escrita — Codex e Claude

Data local: 07/10/2026 (America/Sao_Paulo). Solicitação: adotar o padrão de redação dos artigos na pasta externa indicada pelo pesquisador e o template SBC do projeto PLN, considerando coesão, coerência, verbos e construção, além dos tópicos.

## Procedimento

O Codex inventariou 12 PDFs/133 páginas e extraiu todo o texto para `02_referencias/padrao_escrita_anselmo_2026/`. Conferiu visualmente as primeiras páginas dos 12, páginas internas selecionadas de A01/A08/A12 e a primeira página do template genérico; examinou as quatro páginas de instruções extraídas e o `.sty` local. O PDF de duas colunas recebeu extração auxiliar, sem substituir a fonte original.

Foram realizadas duas consultas ao Claude Code com `--model opus`, sem override de esforço. Ambas retornaram **`claude-opus-5-5`**, sucesso e nenhuma negação de ferramenta. Acesso do Claude permaneceu restrito a Read/Glob/Grep no projeto. As extrações permitiram discutir as fontes externas sem ampliar permissões do agente nem editar o projeto PLN.

| Rodada | Timestamp UTC original | Conteúdo |
|---|---|---|
| 1 | `20261008T013515040393Z` | Análise do corpus e proposta de padrão editorial |
| 2 | `20261008T014219049220Z` | Revisão do guia, análise, amostra e instruções de template |

O Claude informou leitura integral de A01–A12 na primeira rodada. Na segunda, leu os quatro documentos preparados e trechos de referências, sem abrir PDFs ou a extração auxiliar de A12. Suas sugestões foram revistas pelo Codex, com limites de leitura registrados. Não houve atribuição estilométrica de autoria.

## Decisões integradas

- Português acadêmico brasileiro, orientado pelos traços recorrentes e pela diversidade do corpus com coautoria.
- Template SBC local, Resumo em português e Abstract em inglês, referências autor–ano.
- Progressão clara, retomadas com referentes definidos, conectivos com função e procedimentos contextualizados.
- Predominância editorial de impessoalidade, preservando a possibilidade de sujeitos ativos e primeira pessoa plural deliberada.
- Tempos verbais segundo a função: definições/objetivo, execução, interpretação e continuidade.
- Hipóteses, comparação e força verbal limitadas pelo desenho e pelas evidências deste estudo.
- Limite de páginas, autoria/afiliação, título e regras da disciplina permanecem pendentes.

## Revisão mútua

O Codex corrigiu regras excessivamente rígidas propostas na primeira resposta: uma voz gramatical por seção, objetivo sempre na mesma fórmula, retomada demonstrativa obrigatória e futuro limitado exclusivamente a trabalho posterior. Também padronizou categorias pareadas, validação/dev e interpretação dos verbos de comparação. O Claude aceitou todos esses ajustes.

O Claude identificou ambiguidade na retomada da amostra, ausência da proporção 1:1 na receita com controle de tamanho, ressalva sobre escala colocada no contexto errado e necessidade de explicitar o orçamento distinto do braço de proporção real. Esses pontos foram corrigidos. Foram integradas ainda concordância de taxa/FPR, delimitação dos recursos e transparência da conferência visual parcial.

## Artefatos e preservação

- [Guia editorial](../../../04_escrita/artigo/seminarios_2026/PADRAO_ESCRITA.md).
- [Amostra original](../../../04_escrita/artigo/seminarios_2026/AMOSTRA_REDACAO.md).
- [Análise do corpus](../../../02_referencias/padrao_escrita_anselmo_2026/ANALISE_CORPUS.md).
- [Template e proveniência](../../../04_escrita/artigo/seminarios_2026/template_sbc/README.md).

`01_solicitacao.txt`, `01_resposta.json`, `01_parecer_claude.md` e correspondentes `02_*` preservam os retornos brutos. A segunda solicitação contém o parecer anterior como contexto. Pareceres brutos incluem sugestões superadas e não substituem os documentos integrados.

Os arquivos `.sty`/`.bst` foram copiados sem alteração, com hashes. O `.tex` externo já preenchido com o artigo PLN não foi copiado. Não houve criação do manuscrito final, compilação PDF, consolidação de resultados, treinamento, inferência ou acesso RunPod. Planos e índices foram atualizados para registrar a decisão editorial; fontes científicas históricas e arquivos externos permaneceram preservados.

Os valores `total_cost_usd` nos retornos são estimativas de uso do CLI e não comprovam cobrança extra no plano. Esta revisão define escrita e organização; não certifica cientificamente os resultados.
