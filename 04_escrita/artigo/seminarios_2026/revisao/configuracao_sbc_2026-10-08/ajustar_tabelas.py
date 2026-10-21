"""Corrige só as caixas das tabelas, sem alterar seu conteúdo."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
DOC=HERE.parents[1]/'revisao/introducao_2026-10-07/previa_rascunho_sbc.tex'
text=DOC.read_text(encoding='utf-8')
opening='\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}'
closing='\\end{tabular}}\n\\end{table}'
assert text.count(opening)==7 and text.count(closing)==7
text=text.replace(opening,'\\begin{sbcfitwidth}\n\\begin{tabular}')
text=text.replace(closing,'\\end{tabular}\n\\end{sbcfitwidth}\n\\end{table}')
DOC.write_text(text,encoding='utf-8')
