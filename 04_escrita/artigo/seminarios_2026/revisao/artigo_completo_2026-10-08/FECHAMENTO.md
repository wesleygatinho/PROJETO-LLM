# Fechamento do artigo completo

## Resultado

Manuscrito completo redigido, corrigido e integrado: `texto/artigo_completo.md`. Título: **Avaliação exploratória de classificadores Qwen2.5-Coder no PrimeVul: desempenho global, pareado e recursos de implantação**. Inclui Resumo/Abstract, Introdução, Fundamentação e trabalhos relacionados, Método, Resultados, Discussão, Ameaças à validade, Conclusão e onze referências primárias. Seis tabelas no corpo e uma tabela suplementar; figura científica suplementar em `figuras/ordenacao_7b.png`/`.svg`.

O arquivo LaTeX já aberto foi atualizado em seu próprio caminho: `revisao/introducao_2026-10-07/previa_rascunho_sbc.tex`. Não foi criado documento LaTeX substituto nem aberta nova aba. A versão anterior está preservada neste diretório.

Versão global incorporada: v003, versão 1 da rodada artigo_completo_02; SHA-256 do Markdown: `8ee65a8fd09cb16c1e525863fcecf79136caa38940fba79e85e3693b7f6683b6`. A integração foi explícita pelo controlador após conferência local de 39 conjuntos de alegações/tabelas e verificação das fontes congeladas. Essa integração não publica nem submete o artigo.

## Ciclo Codex–Claude

Codex redigiu v001. Claude Opus 5.5 revisou o texto integral e apontou oito itens. Codex corrigiu em v002 e respondeu individualmente a todos. Uma sessão nova do Claude Opus 5.5 conferiu a versão integral, declarou todos os oito IDs resolvidos e aprovou nas conferências realizadas. Uma terceira sessão focalizada confrontou as seis fontes primárias de literatura e os arquivos pai/commit dos cinco pares documentados, confirmando os cinco casos e levantando P1: distinção entre atualização LoRA e peso adaptado. Codex corrigiu P1 em v003. Uma quarta sessão revisou o manuscrito integral final na rodada artigo_completo_02, que foi iniciada explicitamente para preservar a aprovação anterior sem alterar silenciosamente seu texto. Pareceres e limites reais estão preservados; não se declara revisão visual integral dos PDFs nem reprodução independente pelo Claude.

As quatro chamadas reais utilizaram Claude Opus 5.5, confirmado pelo campo modelUsage da CLI, e as quatro sessões são distintas. Metadados, duração e custos estimados estão em `consultas_claude.json`; prompts e retornos brutos foram preservados. Cada chamada teve teto US$3; estimativa da CLI não comprova faturamento avulso. Não houve envio de credenciais.

## Ajustes realizados

Corrigidos dois arredondamentos (sensibilidade máxima0,22 p.p.; estabilidade bootstrap0,10 p.p.), restringida ao pareado a afirmação sobre o limiar zero do piloto 3B real, ajustada a numeração das tabelas pela ordem de aparição, padronizado seed/seeds, explicitado o referente das médias 7B nos resumos e removida nota interna da referência Hui. O método distingue14 avaliações de33 arquivos de previsão. A introdução explicita a necessidade de conferir a correspondência dos membros na release.

As análises mantêm separados global/pareado, ordenação/categorias, limiar F1/restrição FPR e intervalo condicional/dispersão de seeds. A comparação NF4 com adaptador/BF16 mesclada é de configurações completas, sem causalidade atribuída apenas a bits, equivalência ou diagnóstico de compreensão semântica. Os cinco casos de correspondência têm sensibilidade própria e não implicam validação dos demais559 pares.

## Preservação e rastreabilidade

Os110 arquivos registrados antes da consolidação permanecem byte a byte inalterados. Nenhum treinamento, inferência, recuperação de pesos ou acesso ao RunPod foi realizado. A etapa nova recuperou dados/tokenizers/fontes públicas, reconstruiu métricas em CPU, calculou bootstrap e exportou tabelas/figura. Oito testes passaram. Não foram encontradas divergências nas métricas reproduzidas à precisão histórica publicada. `auditoria_final.json`, `verificacao_integracao.json` e `SUPLEMENTO.md` documentam as condições e limites; duas alterações de scripts auxiliares após a exportação e antes do congelamento estão explicitadas, sem apagar sua cronologia.

## Pendências para entrega formal

O conteúdo completo está revisado no escopo descrito, mas **o artefato não está pronto para submissão**. Faltam nomes/autoria, afiliação completa, limite de páginas e regras específicas da disciplina. A fonte usa identificação explicitamente pendente, sem inventar nomes ou contato.

O compilador interno falhou quatro vezes na preparação do ambiente Windows: `helper_unknown_error: setup refresh had errors`. Não apresentou erros de linha da fonte. Portanto, compilação, diagramação integral, limite de dez linhas de Resumo/Abstract, legibilidade das tabelas no PDF e número de páginas não foram validados. `DIAGNOSTICO_LATEX.md` preserva os retornos. Não foi produzido PDF por ferramenta externa.

A aprovação dos agentes não substitui a responsabilidade acadêmica do pesquisador ou aceite docente. As limitações exploratórias e de generalização são explícitas no artigo, não pendências que justifiquem fabricar resultados ou executar novos treinos.
