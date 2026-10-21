# Registro da elaboração do plano Codex–Claude

Data local: **07/10/2026**, America/Sao_Paulo. Projeto examinado: `D:\UFMA UNIVERSIDADE\MESTRADO - ESTUDO LLM`, HEAD `5b4b969d3643f30c80e2678f67efdce1e24d67dd`. Registros técnicos das chamadas usam UTC, portanto seus timestamps originais iniciam em 08/10.

## Solicitação e execução

O pesquisador solicitou um plano de implementação/consolidação e escrita do artigo de Seminários, entrega e apresentação em 11/11/2026, elaborado com o Claude e organizado no projeto. Autorizou usar Opus 5.5 com comportamento padrão. O padrão de escrita será definido depois deste plano.

Foram feitas duas chamadas reais pelo Claude Code local, com `--model opus` e sem override de esforço. Ambas reportaram **`claude-opus-5-5`**, sucesso e nenhuma negação de ferramenta. A ponte usou apenas Read/Glob/Grep, com acesso restrito ao projeto, sem comandos/edições pelo Claude. O Codex criou os documentos finais de planejamento. Não houve implementação dos scripts futuros, download de dataset, execução de treinamento/inferência ou alteração das fontes científicas históricas.

| Rodada | Registro UTC original | Objetivo |
|---|---|---|
| 1 | `20261008T011119598898Z` | Proposta independente baseada em protocolo, código, CSVs e formatos dos logs |
| 2 | `20261008T011944955152Z` | Crítica dos documentos preliminares e resolução de contrapontos do Codex |

## Decisão integrada

- Recorte no bloco Qwen existente; novos treinos não são requisito automático.
- Roteiro da pesquisa maior preservado; comparação PTQ completa permanece futura.
- Recuperação da release exata e auditoria de identidade precedem certificação do pareado.
- F1 usa calibração na validação; categorias P-* e ordenação são métricas distintas, com políticas explícitas.
- Estatística separa incerteza amostral e variação entre seeds; McNemar complementar possui evento definido.
- Teto do baseline, diferenças de implantação, acesso exploratório ao teste e troca retrospectiva do critério de empates serão descritos.
- Leitura de Huang/PrimeVul/Risse precede fechamento das contribuições; nenhuma novidade foi certificada.
- Duas trilhas estimadas: completa ~72h e essencial ~50h, com replanejamento em 13/10 e 27/10.

## Contrapontos e ajustes

O primeiro parecer do Claude contou o cabeçalho como execução da etapa 3 e certificou ausência de falhas pelo total dos CSVs. O Codex corrigiu para 10 linhas de dados e para evidência de cobertura ainda sujeita a auditoria. O Claude aceitou.

O Codex manteve recuperação da fonte oficial como requisito de certificação, rejeitou formulações causais sobre remoção de atalhos e evitou reexecutar o baseline histórico que acrescenta linhas à planilha. O Claude aceitou esses ajustes.

O Claude recomendou explicitar a diferença entre os dois limiares de validação, a calibração distinta NF4/BF16, a cronologia da correção de empates, a contingência de recuperação dos dados e a carga de trabalho maior. Esses pontos foram integrados aos documentos finais.

McNemar, se utilizado, será complementar sobre P-C no limiar de maior F1 da validação; a ordenação com meio empate usa bootstrap pareado. O evento sugerido no parecer inicial, ordenação estrita, não foi adotado como teste principal. P-valores históricos exigem reprodução do evento original, sem substituição silenciosa.

## Arquivos do registro

- `01_solicitacao.txt` / `02_solicitacao.txt`: entradas exatas das chamadas; a segunda inclui a resposta anterior como contexto.
- `01_resposta.json` / `02_resposta.json`: retornos originais do CLI, incluindo modelo efetivo e metadados.
- `01_parecer_claude.md` / `02_parecer_claude.md`: texto dos retornos, preservado sem revisão editorial.

Pareceres brutos contêm sugestões que não foram adotadas e constatações com limites. Os documentos finais em [planejamento](../../../01_planejamento/artigo_seminarios_2026/README.md) e [escrita](../../../04_escrita/artigo/seminarios_2026/README.md) são a decisão operacional integrada.

## Limites

O Claude não abriu integralmente os PDFs ou os grandes logs, não recalculou os resultados e não recuperou dados. Na segunda rodada, revisou quatro documentos preliminares, não o pacote final já integrado nem os dois documentos de escrita criados depois. O Codex conferiu a organização e as ligações locais do pacote final; isso não equivale a validação dos experimentos.

Os metadados `total_cost_usd` dos retornos são estimativas do CLI e não comprovam cobrança extra no plano usado. Esta elaboração não acionou RunPod. Concordância entre agentes não substitui a responsabilidade acadêmica e a verificação das fontes.
