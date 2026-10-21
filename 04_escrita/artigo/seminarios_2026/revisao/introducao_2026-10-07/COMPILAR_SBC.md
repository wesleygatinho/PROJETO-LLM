# Compilação do documento SBC

O arquivo principal é `previa_rascunho_sbc.tex`, o mesmo documento já aberto. Ele incorpora o estilo SBC adotado pelo projeto e a bibliografia do artigo, sem depender de arquivos adicionais de estilo ou de uma rodada de BibTeX. O pacote `natbib`, necessário às citações autor–ano, foi instalado no MiKTeX deste computador.

Para compilar, execute `compilar_sbc.cmd` nesta pasta. Também funciona, no terminal aberto nesta pasta:

```powershell
latexmk -pdf previa_rascunho_sbc.tex
```

O PDF atualizado fica ao lado do `.tex`, com o nome `previa_rascunho_sbc.pdf`. O comando usa a configuração `.latexmkrc`, que executa pdfLaTeX, resolve as referências com as passagens necessárias, interrompe em erros reais e gera SyncTeX. As diretivas do arquivo identificam pdfLaTeX e UTF-8 para os editores que as reconhecem.

A compilação local foi validada com MiKTeX e latexmk: 15 páginas, sem erros, citações indefinidas ou caixas excedendo as margens. As páginas renderizadas foram inspecionadas. Restam avisos de espaçamento `Underfull`, sem cortes observados. A chamada de compilação interna do Codex continua falhando na preparação do ambiente Windows, antes do TeX; isso não impede a compilação local nem a leitura do PDF produzido.

O texto e os números não foram reescritos. Autoria completa, limite de páginas e adequação do comprimento dos resumos para entrega continuam sendo questões editoriais. Não foi reduzida a fonte dos resumos para forçar seu tamanho. O PDF permite visualizar a versão atual, sem declarar conformidade final de submissão.

O histórico e as verificações estão em `../configuracao_sbc_2026-10-08/`. A documentação oficial do gerenciador de dependências usado é [MiKTeX Packages](https://docs.miktex.org/manual/miktex-packages.html).
