"""Transposição determinística da redação Claude: citações, tabelas e SBC no .tex aberto."""
import json,re,hashlib,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent; ARTICLE=HERE.parents[1]
TARGET=ARTICLE/'revisao/introducao_2026-10-07/previa_rascunho_sbc.tex'
CAT=json.loads((HERE/'catalogo_verificado.json').read_text(encoding='utf-8'))
SEPARATOR='<!-- INICIO_SUPLEMENTO -->'
CITE=re.compile(r'\[([@!][\w; @!-]+)\]')
def cite_keys(token):return [k.strip().lstrip('@!') for k in token.split(';')]
def tex(text):
    saved=[]
    def keep(s):saved.append(s);return f'ZZSAFE{len(saved)-1}ZZ'
    text=re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]',lambda m:keep(m[0]),text,flags=re.S)
    def citation(m):
        keys=cite_keys(m[1]);assert all(k in CAT for k in keys),keys
        return keep(('\\citet' if m[1].startswith('!') else '\\citep')+'{'+','.join(keys)+'}')
    text=CITE.sub(citation,text)
    text=re.sub(r'\bTabela (\d+)\b',lambda m:keep('Tabela~\\ref{tab:'+m[1]+'}'),text)
    text=re.sub(r'\bSeç(?:ão|ões) (\d+)\b',lambda m:keep('Seção~\\ref{sec:'+m[1]+'}'),text)
    text=re.sub(r'`([^`]+)`',lambda m:keep('\\texttt{'+tex(m[1])+'}'),text)
    text=re.sub(r'\*\*([^*]+)\*\*',lambda m:keep('\\textbf{'+tex(m[1])+'}'),text)
    text=re.sub(r'(?<![\w*])\*([^*\n]+)\*(?!\w)',lambda m:keep('\\textit{'+tex(m[1])+'}'),text)
    for old,new in {'≤':r'\(\leq\)','≥':r'\(\geq\)','α':r'\(\alpha\)','Δ':r'\(\Delta\)','Σ':r'\(\Sigma\)','×':r'\(\times\)','≈':r'\(\approx\)','₀':r'\(_0\)','−':'-','—':'---','–':'--'}.items():text=text.replace(old,keep(new))
    text=re.sub(r'[\\{}%&#_$~^]',lambda m:{'\\':r'\textbackslash{}','{':r'\{','}':r'\}','%':r'\%','&':r'\&','#':r'\#','_':r'\_','$':r'\$','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}[m[0]],text)
    for i,v in reversed(list(enumerate(saved))):text=text.replace(f'ZZSAFE{i}ZZ',v)
    assert 'ZZSAFE' not in text
    return text
def body(content):
    lines=content.strip().splitlines();out=[];i=0;caption=None;tn=None
    while i<len(lines):
        line=lines[i].strip()
        if not line or line.startswith('<!--'):i+=1;continue
        if line.startswith('\\['):
            eq=[line];i+=1
            while not eq[-1].endswith('\\]'):
                assert i<len(lines);eq.append(lines[i]);i+=1
            out.append('\n'.join(eq));continue
        cap=re.match(r'^Tabela (\d+)\.\s*(.*)',line)
        if cap:tn=cap[1];caption=cap[2];i+=1;continue
        if line.startswith('|'):
            assert caption is not None,'Tabela sem legenda'
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c) for c in row):rows.append(row)
                i+=1
            n=len(rows[0]);assert all(len(r)==n for r in rows)
            out += [r'\begin{table}[htbp]',r'\centering',r'\caption{'+tex(caption)+'}',r'\label{tab:'+tn+'}',r'\footnotesize\setlength{\tabcolsep}{3pt}',r'\resizebox{\textwidth}{!}{%',r'\begin{tabular}{l'+'r'*(n-1)+'}',r'\toprule']
            for j,row in enumerate(rows):
                out.append(' & '.join(tex(c) for c in row)+r' \\')
                if j==0:out.append(r'\midrule')
            out += [r'\bottomrule',r'\end{tabular}}',r'\end{table}','']
            caption=None;continue
        h=re.match(r'^(##|###)\s+(\d+(?:\.\d+)*)\.?\s+(.*)$',line)
        if h:out.append(('\\section' if h[1]=='##' else '\\subsection')+'{'+tex(h[3])+'}\\label{sec:'+h[2]+'}')
        else:out.append(tex(line)+'\n')
        i+=1
    return '\n'.join(out)
def readable(md):
    def citation(m):
        keys=cite_keys(m[1]);refs=[CAT[k] for k in keys]
        if m[1].startswith('!'):return refs[0]['autores_citacao']+' ('+refs[0]['year']+')'
        return '['+'; '.join(x['autores_citacao']+' '+x['year'] for x in refs)+']'
    return CITE.sub(citation,md)
def main():
    source=Path(sys.argv[1]);stage=sys.argv[2]
    raw=source.read_text(encoding='utf-8');md,supp=raw.split(SEPARATOR,1)
    md=md.strip()+'\n';supp=supp.strip()+'\n'
    keys=sorted({k for m in CITE.finditer(md) for k in cite_keys(m[1])},key=lambda k:(CAT[k]['author'],CAT[k]['year']))
    assert keys and 'http' not in md.lower() and 'github' not in md.lower()
    assert not re.search(r'(?m)^## Referências',md)
    title=md.splitlines()[0].lstrip('# ')
    resumo=re.search(r'## Resumo\s+(.*?)\s+## Abstract',md,re.S)[1]
    abstract=re.search(r'## Abstract\s+(.*?)\s+## 1\.',md,re.S)[1]
    maintext=md[md.index('## 1.'):]
    original=(HERE/'antes/documento_aberto.tex').read_text(encoding='utf-8')
    preamble=original[original.index(r'\documentclass'):original.index(r'\title{')].strip()
    preamble+='\n\\usepackage{amssymb}\n\\usepackage[authoryear,square]{natbib}\n\\setcitestyle{authoryear,square,aysep={},citesep={,}}\n'
    bib=[]
    for key in keys:
        ref=CAT[key]
        bib.append('\\bibitem['+tex(ref['autores_citacao'])+'('+ref['year']+')]{'+key+'}\n'+tex(ref['referencia']))
    result=('% Redação e correções: Claude Opus 5.5 xhigh. Transposição: Codex.\n'+preamble+'\n\\title{'+tex(title)+'}\n\\author{Autoria a confirmar}\n\\address{Programa de Pós-Graduação em Ciência da Computação\\\\\nUniversidade Federal do Maranhão}\n\\begin{document}\n\\maketitle\n\\begin{abstract}\n'+tex(abstract)+'\n\\end{abstract}\n\\begin{resumo}\n'+tex(resumo)+'\n\\end{resumo}\n'+body(maintext)+'\n\\clearpage\n\\begin{thebibliography}{99}\n'+'\n\n'.join(bib)+'\n\\end{thebibliography}\n\\end{document}\n')
    defined=set(re.findall(r'\\label\{([^}]+)\}',result));called=set(re.findall(r'\\ref\{([^}]+)\}',result))
    assert called<=defined,{'referencias_internas_ausentes':list(called-defined)}
    used_tex={k for args in re.findall(r'\\cite[pt]\{([^}]+)\}',result) for k in args.split(',')}
    assert used_tex==set(keys)
    out=HERE/stage;out.mkdir(exist_ok=True)
    (out/'artigo_com_citacoes.md').write_text(md,encoding='utf-8')
    (out/'artigo_legivel.md').write_text(readable(md)+'\n## Referências\n\n'+'\n\n'.join(CAT[k]['referencia'] for k in keys)+'\n',encoding='utf-8')
    (out/'SUPLEMENTO.md').write_text(readable(supp),encoding='utf-8')
    bibsrc=(HERE/'bibliografia_verificada.bib').read_text(encoding='utf-8')
    chunks=[m[0].strip() for m in re.finditer(r'@\w+\{([^,]+),.*?(?=\n@|\Z)',bibsrc,re.S) if m[1] in keys]
    (out/'artigo.bib').write_text('% Somente publicações efetivamente citadas na redação Claude.\n'+'\n\n'.join(chunks)+'\n',encoding='utf-8')
    TARGET.write_text(result,encoding='utf-8',newline='\n')
    report={'fonte':str(source.resolve()),'sha256_fonte':hashlib.sha256(source.read_bytes()).hexdigest(),'tex_aberto':str(TARGET),'sha256_tex':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'referencias':keys,'numero_citacoes':len(list(CITE.finditer(md))),'labels_verificados':len(defined),'comentario':'Somente transposição e vínculos de citações. Não certifica compilação ou layout. Texto e fontes científicas não alterados.'}
    (out/'transposicao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
