# Registro operacional — introdução — 07/10/2026

O Codex redigiu `rascunho_codex.md` e o registrou como v001 na rodada `introducao_01`. Os registros do controlador em `../fluxo_editorial/rodadas/introducao_01/` são a fonte canônica das versões, hashes, pedidos, respostas brutas e pareceres importados. A seção não é integrada antes da revisão científico/editorial e da conferência de afirmações.

## Acesso ao Claude

1. A chamada inicial no sandbox produziu apenas erro `ENOTFOUND` (“Can't reach the API server”), preservado em `consultas/001_revisar.json`; não existe parecer dessa tentativa e não foi importado como revisão.
2. A primeira solicitação de execução com rede recebeu timeout da revisão automática de permissão. Não executou a consulta. O mecanismo informou que uma repetição era permitida.
3. A repetição foi recusada pela revisão automática por risco de envio de fontes/código/registros potencialmente privados do projeto à API externa sem autorização específica do payload. Não se contornou a recusa.
4. Foi apresentada ao pesquisador a consulta de autorização, com escopo exato: introdução, plano, guia, seis fontes primárias, bibliografia, receitas JSON, código de avaliação e CSVs históricos; exclusão de credenciais; modo somente leitura; limite CLI US$ 3 por chamada; finalidade revisão/conferência. O pesquisador respondeu explicitamente **“Autorizar o pacote de revisão”** nesta conversa em 07/10/2026. Essa autorização cobre as chamadas deste ciclo.
5. A consulta foi retomada com o pacote autorizado e `--modelo claude-opus-5-5`. A identidade efetiva e as sessões deverão ser registradas a partir de `modelUsage` e `session_id` dos retornos, não da autodeclaração do modelo.

Nenhuma das tentativas de aprovação recusadas gerou um parecer. Os erros não são evidência de revisão científica. A ponte usa sessão nova, `Read,Glob,Grep`, modo safe/restricted, sem persistência, sem MCP, sem edição ou shell do agente; as respostas são importadas explicitamente pelo controlador.

## Prévia SBC

Uma prévia autocontida do rascunho foi criada em `previa_rascunho_sbc.tex`, com as definições do estilo SBC fornecido embutidas, para respeitar o compilador de documentos únicos. O estilo original e `sbc.bst` permanecem preservados. A prévia usa bibliografia autor–ano explícita; a versão modular e o BibTeX serão empregados na montagem posterior com `sbc.bst`.

`open_in_codex` retornou `queued` para o arquivo. `compile_latex_document` retornou `compile-failed`, mensagem “Could not compile the document”, log **“Unable to find standard directories for platform”**. Trata-se de falha de ambiente reportada pelo compilador, não de diagnóstico de erro no conteúdo TeX; não se declara compilação ou diagramação verificada. Nenhuma instalação foi realizada. A fonte fica preservada no editor.

## Preservação

O trabalho desta etapa consiste em escrita, leitura documental, extração/renderização local de PDFs e revisão textual. Não foram executados scripts de experimento, treino, inferência ou RunPod. `preservacao_antes.json` registra hashes dos 109 arquivos preexistentes de `03_experimentos/`; a comparação final deverá registrar qualquer diferença antes do encerramento.
