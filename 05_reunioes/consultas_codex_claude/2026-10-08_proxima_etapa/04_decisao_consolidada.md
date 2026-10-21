# Próxima etapa do artigo — decisão após análise Codex–Claude

Data: 08/10/2026. Escopo: analisar a prioridade atual a pedido do pesquisador; não executar a etapa técnica nem redigir a próxima seção nesta consulta.

## Conclusão

A resposta anterior do Codex era **parcialmente correta**: inventário e recuperação da release são prioritários na consolidação, mas P0–P2 não são condição para começar a redação. O plano já permite escrever fundamentação e método enquanto a validação avança. Não é necessário mudar o plano; é necessário corrigir sua interpretação.

**Próxima etapa recomendada: inventário documental inicial de P0, articulado à primeira versão do Método.** A prioridade técnica é localizar e mapear as fontes existentes. A próxima seção a redigir é o Método, aproveitando essa mesma leitura. Não esperar P0 completo, recuperação dos dados ou aceites de P1–P2 para escrever os componentes sustentados.

## Entrega concreta da próxima etapa

1. **Inventário documental inicial:** relacionar as execuções candidatas aos CSVs, logs, receitas e código; distinguir rodadas oficiais, depuração, `v01/` e `descartados/`; registrar fontes ausentes, vias candidatas de recuperação da release e impressões digitais históricas disponíveis. Separar hashes atuais completos de hashes históricos abreviados e de revisões ausentes. Isso inicia P0 e não representa seu aceite integral.
2. **Método, primeira versão:** redigir configurações, prompting/classificação, políticas de calibração, métricas global/pareada e cronologia exploratória a partir das fontes efetivamente conferidas. Registrar, em material de revisão, a correspondência de cada decisão com sua fonte e as lacunas. Não afirmar que a manutenção das melhores épocas já foi reproduzida. Não apresentar procedimentos estatísticos planejados como executados.
3. **Mapa de pendências:** cobrir os oito itens metodológicos do plano de escrita, identificando fonte disponível, limitação e etapa de validação aplicável. Release, identidades, denominadores, revisões, calibração, análises e recursos só podem ser certificados com a evidência pertinente.

Critério de aceite desta entrega inicial: decisões relatadas são rastreáveis; lacunas não são preenchidas por suposição; não há números copiados das notas sem conferência; o texto distingue execução histórica e consolidação futura; fontes históricas permanecem preservadas. Não exigir auditoria completa de pares ou reconstrução integral das métricas para aceitar essa primeira versão documental.

Depois disso, a frente técnica avança na recuperação da mesma release e em P1–P2. Fundamentação e trabalhos relacionados podem ser redigidos com o núcleo primário já verificado, particularmente durante esperas externas, mas não substituem a resolução do caminho crítico técnico.

## Distinções necessárias

| Decisão | Evidência e limite |
|---|---|
| Começar o Método agora | `PLANO_EXECUCAO.md`, §4/P5, e `PLANO_ESCRITA.md`, §6. A redação parte de receitas/código conferidos e declara lacunas |
| Priorizar P0 na frente técnica | Plano técnico §4/P0–P1; cronograma §§2 e 4. Dados estão ausentes no diretório reservado e a recuperação pode demorar |
| Fechar o Método | Contrato do plano de escrita §3: P0–P3 e código; recursos (§4/item 7) também exigem verificação de P4, conforme os procedimentos efetivamente usados |
| Fechar Resultados e Discussão | Aceites de P1–P4 para as análises incluídas. Diagnóstico preliminar não é resultado certificado |
| Fechar contribuições, conclusão, título e resumos | Achados consolidados e reavaliação do posicionamento. Aprovação da introdução não resolve essas dependências |

As análises opcionais não viram obrigatórias por constarem na especificação. Se não forem executadas, não podem sustentar alegações. A data de 13/10 é um ponto de replanejamento, não uma proibição de diagnósticos úteis antes dela. As horas estimadas e a disponibilidade semanal ainda não permitem garantir prazo ou impor uma sequência rígida de redação.

## Pareceres e divergências resolvidas

O Codex registrou a análise independente em `02_analise_codex_previa.md`, antes de ler o primeiro parecer. Claude Opus 5.5 analisou os seis documentos em `01_parecer_claude.md`; a identidade do modelo é confirmada pelo retorno da CLI, não apenas por sua declaração textual.

O primeiro parecer confirmou a prioridade técnica de P0, mas criou condições adicionais não sustentadas. O Codex contestou esses pontos numa segunda consulta, preservada em `03_solicitacao_conferencia.txt` e `03_parecer_conferencia_claude.md`. A conferência:

- retirou a exigência de concluir P0 antes de qualquer prosa;
- retirou a exclusividade do pesquisador para localizar a origem da release e uma autorização humana obrigatória não expressa no plano;
- corrigiu o fechamento do Método para considerar P3, código e P4 no bloco de recursos;
- reconheceu que limitar diagnósticos preliminares à contingência de 13/10 era preferência operacional, não regra documental;
- substituiu a recomendação de apenas um mapa pelo Método parcial acompanhado de lacunas, mantendo P0 como prioridade técnica.

A recomendação consolidada é do Codex, após confronto com os pareceres e com os documentos. Concordância dos agentes não certifica resultados científicos.

## Estado e limites

A consulta usou seis documentos internos autorizados especificamente pelo pesquisador. Claude declarou que analisou o conteúdo anexado e não conferiu PDFs, código, logs, CSVs ou disco. O Codex conferiu os planos, o fechamento e os diretórios pertinentes. `03_experimentos/dados/` contém apenas `.gitkeep`; a consolidação contém somente a especificação; o destino de resultados derivados contém somente README. Isso não prova que inexista uma cópia histórica em outro local.

A introdução v003 segue aprovada como seção, com reavaliação posterior das contribuições. A compilação SBC permanece pendente por falha do ambiente registrada no fechamento; esta análise não tentou corrigir o compilador ou alterar o LaTeX aberto.

P0–P4 e os scripts futuros continuam pendentes. Origem/disponibilidade da release, regras da disciplina e dedicação real permanecem questões a resolver, sem bloquear os trechos metodológicos já documentados. Os planos congelados não foram reescritos. Nenhuma implementação de consolidação, recuperação de dados, treinamento, inferência, uso de RunPod ou alteração de resultados históricos foi executada.
