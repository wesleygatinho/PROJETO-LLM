"""Transpõe o manuscrito para o documento SBC já aberto, sem compilar PDF externo."""
import re
import sys
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTICLE = HERE.parents[1]
TARGET = ARTICLE / 'revisao/introducao_2026-10-07/previa_rascunho_sbc.tex'

def tex(text):
    saved = []
    def keep(fragment):
        saved.append(fragment)
        return f'ZZPROTECTED{len(saved)-1}ZZ'
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',
                  lambda m: keep(tex(m[1]) + ': ' + r'\url{' + m[2] + '}'), text)
    text = re.sub(r'https?://[^\s]+', lambda m: keep(r'\url{' + m[0].rstrip('.') + '}') + ('.' if m[0].endswith('.') else ''), text)
    text = re.sub(r'`([^`]+)`', lambda m: keep(r'\texttt{' + tex(m[1]) + '}'), text)
    text = re.sub(r'\*\*([^*]+)\*\*', lambda m: keep(r'\textbf{' + tex(m[1]) + '}'), text)
    text = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?!\w)', lambda m: keep(r'\textit{' + tex(m[1]) + '}'), text)
    text = text.replace('A_par = [Σ 1(s_v > s_c) + 0,5 Σ 1(s_v = s_c)]/N',
                        keep(r'\(A_{\mathrm{par}}=[\sum_i \mathbf{1}(s_{v,i}>s_{c,i})+0{,}5\sum_i \mathbf{1}(s_{v,i}=s_{c,i})]/N\)'))
    text = text.replace('s > t', keep(r'\(s>t\)'))
    text = text.replace('ΔW = BA', keep(r'\(\Delta W=BA\)'))
    text = text.replace('d × k', keep(r'\(d\times k\)'))
    text = text.replace('W₀', keep(r'\(W_0\)'))
    for old, new in {'≤':r'\(\leq\)', '≥':r'\(\geq\)', 'α':r'\(\alpha\)', 'Σ':r'\(\Sigma\)', '−':'-', '—':'---', '–':'--', '₀':r'\(_0\)'}.items():
        text = text.replace(old, keep(new))
    text = re.sub(r'[\\{}%&#_$~^]', lambda m: {'\\':r'\textbackslash{}','{':r'\{','}':r'\}','%':r'\%','&':r'\&','#':r'\#','_':r'\_','$':r'\$','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}[m[0]], text)
    for i, fragment in enumerate(saved):
        text = text.replace(f'ZZPROTECTED{i}ZZ', fragment)
    return text

def body(content):
    out, lines, i = [], content.strip().splitlines(), 0
    caption = None
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('<!--'):
            i += 1
            continue
        if line.startswith('Tabela '):
            caption = re.sub(r'^Tabela \d+\.\s*', '', line)
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in row):
                    rows.append(row)
                i += 1
            n = len(rows[0])
            assert all(len(row)==n for row in rows), 'Tabela irregular'
            out += [r'\begin{table}[htbp]', r'\centering', r'\caption{' + tex(caption or '') + '}', r'\footnotesize\setlength{\tabcolsep}{3pt}', r'\resizebox{\textwidth}{!}{%', r'\begin{tabular}{l' + 'r'*(n-1) + '}', r'\toprule']
            for ri, row in enumerate(rows):
                out.append(' & '.join(tex(c) for c in row) + r' \\')
                if ri == 0: out.append(r'\midrule')
            out += [r'\bottomrule', r'\end{tabular}}', r'\end{table}', '']
            caption = None
            continue
        m = re.match(r'^(##|###)\s+(?:\d+(?:\.\d+)*\.\s*)?(.*)$', line)
        if m:
            out.append(('\\section' if m[1]=='##' else '\\subsection') + '{' + tex(m[2]) + '}')
        else:
            out.append(tex(line) + '\n')
        i += 1
    return '\n'.join(out)

def main():
    source = Path(sys.argv[1]).resolve()
    md = source.read_text(encoding='utf-8')
    original = (HERE/'previa_original_preservada.tex').read_text(encoding='utf-8')
    preamble = original.split(r'\begin{document}')[0]
    preamble = preamble[preamble.index(r'\documentclass'):]
    preamble += '\n' + r'\usepackage{booktabs,array,graphicx,amsmath,url}' + '\n'
    title = md.splitlines()[0].lstrip('# ')
    resumo = re.search(r'## Resumo\s+(.*?)\s+## Abstract', md, re.S)[1]
    abstract = re.search(r'## Abstract\s+(.*?)\s+## 1\.', md, re.S)[1]
    maintext = md[md.index('## 1.'):md.index('## Referências')]
    references = md.split('## Referências',1)[1].strip().split('\n\n')
    oldbib = original.split(r'\begin{thebibliography}{99}',1)[1].split(r'\end{thebibliography}',1)[0]
    fullhui = re.search(r'\\bibitem\[Hui.*?\n(.*?)\nQwen2', oldbib,re.S)[1]
    bib = []
    for i, ref in enumerate(references):
        if ref.startswith('Hui,'):
            ref = re.sub(r'^Hui, B\. et al\. \(2024\)\.', lambda _:fullhui, ref)
            ref = ref.replace('Lista completa de autores na bibliografia BibTeX. ', '')
        label = re.match(r'(.*?)\((\d{4})\)',ref)
        bib.append(r'\bibitem[' + tex(label[1].strip().split(',')[0]+' '+label[2]) + ']{ref'+str(i+1)+'}\n'+tex(ref))
    result = ('% Artigo completo; fonte e hash registrados em exportacao_latex.json.\n'+preamble+
              '\n\\title{'+tex(title)+'}\n\\author{Autoria a confirmar}\n'+
              '\\address{Programa de Pós-Graduação em Ciência da Computação\\\\\nUniversidade Federal do Maranhão}\n'+
              '\\begin{document}\n\\maketitle\n'+
              '\\begin{abstract}\n'+tex(abstract)+'\n\\end{abstract}\n'+
              '\\begin{resumo}\n'+tex(resumo)+'\n\\end{resumo}\n'+body(maintext)+
              '\n\\clearpage\n\\begin{thebibliography}{99}\n'+ '\n\n'.join(bib)+
              '\n\\end{thebibliography}\n\\end{document}\n')
    TARGET.write_text(result, encoding='utf-8', newline='\n')
    log = {'manuscrito':str(source),'sha256_manuscrito':hashlib.sha256(source.read_bytes()).hexdigest(),
           'documento_aberto':str(TARGET),'sha256_tex':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
           'observacao':'Transposição para o mesmo arquivo aberto. Identificação pendente; nenhuma compilação ou inspeção de PDF é declarada por este script.'}
    (HERE/'exportacao_latex.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(log,ensure_ascii=False))

if __name__=='__main__': main()
