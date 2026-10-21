# Fechamento da introdução — 07/10/2026

**Resultado:** introdução completa v003 aprovada no escopo científico/editorial e integrada. Zero apontamentos abertos no parecer final. Codex redigiu e corrigiu; Claude Opus 5.5 revisou em sessões novas. Aprovação é restrita à introdução e ao escopo do briefing; não garante ausência de erros, validade dos resultados não auditados ou aceite acadêmico.

## Arquivos canônicos

- Texto aprovado: [introducao_01.md](../../texto/secoes/introducao_01.md).
- Seção para montagem LaTeX: [introducao_01.tex](../../texto/secoes/introducao_01.tex).
- Prévia isolada SBC: [introducao_sbc.tex](../../texto/introducao_sbc.tex), autocontida com definições do asset preservado e bibliografia autor–ano explícita. A montagem final utilizará `.bib`/`sbc.bst`.
- Referências: [introducao.bib](../../referencias/introducao.bib) e [matriz da introdução](../../referencias/MATRIZ_INTRODUCAO.md).
- Fontes primárias conferidas, páginas e hashes: [LEITURA_FONTES.md](../../../../../02_referencias/verificacao_introducao_seminarios_2026/LEITURA_FONTES.md).
- Todas as versões, pareceres, respostas e retornos CLI: [manifesto](../fluxo_editorial/rodadas/introducao_01/manifesto.json).

## Ciclo realizado

| Versão | Executor / sessão | Decisão |
|---|---|---|
| v001 | Codex redator; Claude consulta 002 | Corrigir V1-R1 científico maior (posicionamento), V1-R2/V1-R3 editoriais menores (definição e coesão) |
| v002 | Codex corretor; Claude consulta 004 | Três IDs anteriores resolvidos; corrigir V2-R1 editorial menor (contraste explícito) |
| v003 | Codex corretor; Claude consulta 006 | V2-R1 resolvido; aprovar, itens=[] |

O modelo efetivo `claude-opus-5-5` está confirmado nos três retornos `modelUsage`. Os identificadores de sessão distintos e os custos estimados informados pela CLI constam em `auditoria_sessoes.json`. Essa estimativa não é declaração de cobrança. A consulta 001 falhou por DNS e não produziu parecer; negativas de permissão e autorização específica posterior estão no registro operacional.

As correções explicitaram o contraste entre teste PrimeVul/cabeça de classificação com escores e TrapEval/V2P-V2N multifuente/geração com ou sem raciocínio; definiram decisões pareadas e ordenação, restringindo esta aos braços com escores; corrigiram o referente avaliações global/pareada e a descrição da formação dos pares. Nenhum número, achado, superioridade, causalidade ou novidade foi acrescentado.

## Conferências e pendências

A conferência final do Codex contém 25 alegações literais, fontes e localizadores em `verificacao_integracao.json`. Os 109 arquivos históricos de `03_experimentos/` mantiveram seus hashes, conforme `preservacao_antes.json` e `preservacao_depois.json`. Os experimentos e suas notas não foram reescritos. Não houve treinamento, inferência ou uso de RunPod.

**Texto:** não restam apontamentos obrigatórios desta revisão. As fontes primárias e metadados foram verificados pelo Codex. Claude declarou uso focalizado das extrações/código e ausência de conferência visual dos PDFs e de acesso às páginas oficiais; seus pareceres não substituem a leitura primária do Codex. Sugestões opcionais de concisão e tempo verbal foram preservadas nos limites dos pareceres e não impedem aprovação.

**Diagramação:** a tentativa de compilação nativa tanto do rascunho quanto da versão final falhou com `Unable to find standard directories for platform`. O arquivo foi solicitado para abertura no editor (retorno queued) e preservado; não se declara PDF compilado nem layout verificado. Não foi instalado compilador/plugin.

**Artigo completo:** P0–P4 seguem pendentes (release local, identidade/pareamento, reconstrução de métricas/limiares, análises/recursos); dependências não foram resolvidas por revisão de texto. O texto evita anunciar seus resultados. A formulação das contribuições deverá ser reavaliada quando a consolidação produzir os achados. Título, autoria, afiliação completa, limite de páginas/regras da disciplina e demais seções também não foram fechados. A introdução é uma seção aprovada nesta etapa, não a versão final do artigo para entrega.
