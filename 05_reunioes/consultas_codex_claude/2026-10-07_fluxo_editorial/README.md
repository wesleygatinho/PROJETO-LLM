# Mecanismo de redação, revisão e correção

Solicitação do pesquisador: criar com Claude um mecanismo/projeto em que haja quem escreva, quem revise e quem corrija. Data local: 07/10/2026; timestamps UTC dos retornos são de 08/10/2026.

## Trabalho realizado

O Codex consultou Claude Opus sobre o desenho, implementou um controlador Python local, prompts dos três papéis, ponte dentro do projeto, documentação e testes. A distribuição padrão adotada é Codex redator/corretor em etapas separadas, Claude revisor em sessão nova por versão, com conferência de fontes pelo Codex e responsabilidade editorial do pesquisador. Claude pode redigir/corrigir como alternativa explícita pelo mesmo contrato. Os papéis não representam três modelos independentes.

O artigo continua sem manuscrito iniciado. A demonstração usou os três parágrafos da amostra já existente, com uma preferência de concisão explicitamente adicionada ao briefing. Resultados experimentais não foram consolidados, nenhum treinamento/inferência foi executado e não houve uso de GPU/RunPod.

## Consultas efetivas

| Consulta | Modelo confirmado | Verificação |
|---|---|---|
| Desenho do mecanismo, `20261008T015444642006Z` | claude-opus-5-5 | Claude leu README, padrão, matriz e plano técnico; não revisou o código implementado depois |
| Revisão da amostra v1, `20261008T020109021765Z` | claude-opus-5-5 | Dois itens editoriais: concisão do objetivo e referente das receitas/volumes |
| Revisão da amostra v2 pela ponte interna | claude-opus-5-5 | Confirmou os dois IDs resolvidos e aprovou somente o escopo editorial |

Nenhuma negação de ferramenta foi registrada nas consultas bem-sucedidas. Não houve override de esforço. O Claude leu a amostra e o briefing nas revisões; os guias e a matriz foram examinados pelo conteúdo incluído nos pacotes. Não leu PDFs, código científico ou logs nessas revisões. O modelo efetivo é extraído de `modelUsage`, não da sua declaração textual.

## Ajustes após a discussão

- Registro de versão exata por SHA256 em bytes; contexto inclui fontes, briefing, guias e prompts com hashes.
- Apontamentos citam trecho literal existente; o corretor responde exatamente aos IDs e nova revisão verifica cada resolução.
- Correção científica exige fonte, localizador e registro da conferência, ou retirada explícita da alegação sujeita à revisão.
- A aprovação editorial não libera integração. Uma demonstração nunca pode ser integrada.
- Fonte/guia alterado invalida a continuidade da rodada. Aprovação de trechos não aprova a montagem completa do artigo.
- Evitou-se Claude corretor como padrão para que a correção não fosse sempre julgada pelo mesmo modelo. Isso não garante independência absoluta entre os dois modelos ou entre papéis do Codex.

Sugestões do parecer que não viraram requisitos automáticos: aprovar apenas após nova autorização do pesquisador em cada trecho; bloquear qualquer número por uma busca lexical; tornar a matriz inteira legível por máquina antes de iniciar redação; hard cap de três chamadas. O pesquisador já autorizou criar o mecanismo e correções rotineiras não exigem nova aprovação. Números como nomes de modelos, épocas e datas não equivalem a achados de desempenho; uma regra lexical não validaria suas afirmações. Os vínculos usam fontes com hash/localizador e a matriz existente, sem fingir seu preenchimento. Recomenda-se reavaliar divergências após três ciclos, sem implementar chamadas contínuas.

## Demonstração e limite científico

A versão v2 explicita que as duas receitas 1:1 mencionadas são do 3B e que o volume comparado é o da proporção original versus receitas 1:1. O Codex consultou `03_experimentos/resultados/treinos_etapa3.csv`, onde os dois pilotos 1:1 registram iguais contagens por classe e o piloto real registra quantidade maior de benignas. Isso evita a sugestão alternativa do revisor de dizer volumes distintos entre os dois braços 1:1. Essa conferência pontual de contagens não é auditoria dos treinos, recuperação da release ou consolidação P2–P4.

Claude ressaltou corretamente que a amostra por si só não sustentava a comparação de volumes e que isso deve ser verificado antes de uso no manuscrito. O status final da demonstração é **apto_editorial**; não há aprovação científica ou integração. A amostra original não foi alterada.

## Verificação de implementação

Dezesseis testes offline passaram: ciclo completo com dados fictícios, vínculo de versão/contexto, citações literais, IDs duplicados/faltantes, exigência de evidência, verificação dos IDs anteriores, rejeição de integração editorial/demo, persistência do bloqueio por pendências do redator, detecção de alterações, confinamento de caminhos, metadados CLI e retorno/timeout sem importação ou repetição automática.

A primeira tentativa dos testes encontrou restrição de gravação no diretório temporário padrão do sandbox. Os testes passaram a usar pastas temporárias curtas dentro do projeto, removidas ao final, e então foram executados com sucesso. Claude não auditou o código do controlador: suas contribuições foram ao desenho e à redação demonstrativa. Testes não certificam segurança absoluta, validade acadêmica ou correção científica das fontes.

O controlador opera sequencialmente, sem trava entre processos. Manifesto e hashes são mecanismos de rastreabilidade/detecção de alteração acidental, não log inviolável. Não houve commit ou alteração de configurações globais.

## Arquivos

- [Fluxo, comandos e limites](../../../04_escrita/artigo/seminarios_2026/revisao/fluxo_editorial/README.md).
- [Manifesto da demonstração](../../../04_escrita/artigo/seminarios_2026/revisao/fluxo_editorial/rodadas/demo_editorial_01/manifesto.json).
- [Parecer v1](../../../04_escrita/artigo/seminarios_2026/revisao/fluxo_editorial/rodadas/demo_editorial_01/pareceres/v001.json).
- [Parecer v2](../../../04_escrita/artigo/seminarios_2026/revisao/fluxo_editorial/rodadas/demo_editorial_01/pareceres/v002.json).

`01_solicitacao.txt`, `01_resposta.json` e `01_parecer_claude.md` preservam a discussão de desenho. Os retornos brutos da demonstração ficam dentro da própria rodada, em entradas/consultas. As estimativas de custo da CLI não comprovam cobrança extra no plano por assinatura.
