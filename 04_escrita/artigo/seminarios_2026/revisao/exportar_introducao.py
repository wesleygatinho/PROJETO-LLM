"""Exporta a seção integrada para LaTeX e uma prévia SBC autocontida, sem resultados."""
from pathlib import Path
import re, hashlib, json, sys

ARTICLE = Path(__file__).resolve().parents[1]
is_draft = "--rascunho" in sys.argv
SOURCE = ARTICLE / ("revisao/introducao_2026-10-07/rascunho_codex.md" if is_draft else "texto/secoes/introducao_01.md")
text = SOURCE.read_text(encoding="utf-8")
body = text.split("\n", 1)[1].strip()
citations = {
    "Ding et al., 2024": "ding2024primevul",
    "Hui et al., 2024": "hui2024qwen",
    "Hu et al., 2021": "hu2021lora",
    "Dettmers et al., 2023": "dettmers2023qlora",
    "Ding et al. 2024": "ding2024primevul",
    "Hui et al. 2024": "hui2024qwen",
    "Hu et al. 2021": "hu2021lora",
    "Dettmers et al. 2023": "dettmers2023qlora",
}
for label,key in citations.items():
    body = body.replace("("+label+")", "\\cite{"+key+"}").replace("["+label+"]", "\\cite{"+key+"}")
body = re.sub(r"\*([^*\n]+)\*",r"\\textit{\1}",body)
section = "\\section{Introdução}\n\\label{sec:introducao}\n\n" + body + "\n"
section += "\n% Citações narrativas no texto também constam na bibliografia.\n"
section += "\\nocite{ding2024primevul,risse2024limits,huang2026trap,hui2024qwen,hu2021lora,dettmers2023qlora}\n"
section_target = ARTICLE / ("revisao/introducao_2026-10-07/rascunho_introducao_sbc.tex" if is_draft else "texto/secoes/introducao_01.tex")
section_target.parent.mkdir(parents=True, exist_ok=True)
section_target.write_text(section,encoding="utf-8")

sty = (ARTICLE/"template_sbc/sbc-template.sty").read_bytes()
style = sty.decode("latin-1")
# A fonte autocontida embute as definições do asset fornecido; preserva o arquivo original.
style = "\n".join(line for line in style.splitlines() if not line.startswith(("\\NeedsTeXFormat", "\\ProvidesPackage")))
bibliography = r"""\begin{thebibliography}{99}
\bibitem[Dettmers et~al. 2023]{dettmers2023qlora}
Dettmers, T., Pagnoni, A., Holtzman, A. e Zettlemoyer, L. (2023).
QLoRA: Efficient Finetuning of Quantized LLMs. arXiv:2305.14314v1. Preprint, versão 1.

\bibitem[Ding et~al. 2024]{ding2024primevul}
Ding, Y., Fu, Y., Ibrahim, O., Sitawarin, C., Chen, X., Alomair, B., Wagner, D., Ray, B. e Chen, Y. (2024).
Vulnerability Detection with Code Language Models: How Far Are We? arXiv:2403.18624v2. Preprint, versão 2.

\bibitem[Hu et~al. 2021]{hu2021lora}
Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L. e Chen, W. (2021).
LoRA: Low-Rank Adaptation of Large Language Models. arXiv:2106.09685v2. Preprint, versão 2.

\bibitem[Huang et~al. 2026]{huang2026trap}
Huang, F., Sun, Y., Zhang, F., Yang, Z., Liu, H. e Liu, Y. (2026).
Do Fine-Tuned LLMs Understand Vulnerabilities? An Investigation into the Semantic Trap. arXiv:2601.22655v3. Preprint, versão 3.

\bibitem[Hui et~al. 2024]{hui2024qwen}
Hui, B., Yang, J., Cui, Z., Yang, J., Liu, D., Zhang, L., Liu, T., Zhang, J., Yu, B., Lu, K., Dang, K., Fan, Y., Zhang, Y., Yang, A., Men, R., Huang, F., Zheng, B., Miao, Y., Quan, S., Feng, Y., Ren, X., Ren, X., Zhou, J. e Lin, J. (2024).
Qwen2.5-Coder Technical Report. arXiv:2409.12186v3. Relatório técnico, versão 3.

\bibitem[Risse and B{\"o}hme 2024]{risse2024limits}
Risse, N. e Böhme, M. (2024).
Uncovering the Limits of Machine Learning for Automatic Vulnerability Detection.
In \textit{33rd USENIX Security Symposium (USENIX Security 24)}, páginas 4247--4264. USENIX Association.
\end{thebibliography}
"""
preview = r"""% Prévia isolada da introdução, sem título/autoria/resumos do artigo completo.
% Bibliografia da prévia é explícita; manuscrito montado usará referencias/introducao.bib e sbc.bst.
\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\makeatletter
"""+"% Asset SBC embutido, SHA256: "+hashlib.sha256(sty).hexdigest()+"\n"+style+r"""
\makeatother
\begin{document}
"""+section+"\n"+bibliography+"\\end{document}\n"
preview_target = ARTICLE / ("revisao/introducao_2026-10-07/previa_rascunho_sbc.tex" if is_draft else "texto/introducao_sbc.tex")
preview_target.write_text(preview,encoding="utf-8")
metadata_target = ARTICLE / ("revisao/introducao_2026-10-07/exportacao_rascunho_sbc.json" if is_draft else "revisao/introducao_2026-10-07/exportacao_sbc.json")
metadata_target.write_text(json.dumps({
    "estado":"rascunho não revisado por Claude" if is_draft else "exportação da versão integrada",
    "fonte_md":SOURCE.as_posix(),"sha256_md":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "asset_sty_sha256":hashlib.sha256(sty).hexdigest(),
    "modo":"prévia de seção autocontida com definições SBC embutidas; bibliografia explícita autor–ano; fragmento e BibTeX para montagem via sbc.bst",
    "alteracoes_textuais":"somente markup, citações parentéticas SBC e nocite para citações narrativas; sem mudança científica",
},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Seção LaTeX e prévia SBC exportadas:", preview_target)
