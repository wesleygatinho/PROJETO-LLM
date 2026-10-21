# Configuração local do documento SBC já aberto.
# Bibliografia incorporada no .tex: não exige executar BibTeX.
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 %O %S';
$bibtex_use = 0;
$max_repeat = 5;
