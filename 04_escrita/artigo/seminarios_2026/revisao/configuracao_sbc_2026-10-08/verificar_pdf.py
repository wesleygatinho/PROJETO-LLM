"""Inspeção somente de leitura do PDF gerado do documento existente."""
import json,hashlib,subprocess,re,sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from pypdf import PdfReader
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
ARTICLE=HERE.parents[1]
DOC=ARTICLE/'revisao/introducao_2026-10-07/previa_rascunho_sbc.tex'
PDF=DOC.with_suffix('.pdf')
reader=PdfReader(PDF)
pages=[p.extract_text() for p in reader.pages]
dest=HERE/'paginas';dest.mkdir(exist_ok=True)
poppler=Path('C:/Users/santo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
subprocess.run([str(poppler),'-r','65','-png',str(PDF),str(dest/'pagina')],check=True,capture_output=True)
files=sorted(dest.glob('pagina-*.png'))[:len(pages)]
for k in range(0,len(files),8):
    images=[Image.open(p).convert('RGB') for p in files[k:k+8]]
    w,h=images[0].size;contact=Image.new('RGB',(4*w,2*(h+25)),(225,225,225))
    draw=ImageDraw.Draw(contact)
    for j,img in enumerate(images):
        x=(j%4)*w;y=(j//4)*(h+25)
        draw.text((x+10,y+5),f'Pagina {k+j+1}',fill=(0,0,0))
        contact.paste(img,(x,y+25))
    contact.save(dest/f'contato_{k//8+1}.png')
subprocess.run([str(poppler),'-f','1','-singlefile','-r','130','-png',str(PDF),str(dest/'primeira_pagina')],check=True,capture_output=True)
log=DOC.with_suffix('.log').read_text(encoding='utf-8',errors='replace')
record={'arquivo_tex':str(DOC),'sha256_tex':hashlib.sha256(DOC.read_bytes()).hexdigest(),
    'arquivo_pdf':str(PDF),'sha256_pdf':hashlib.sha256(PDF.read_bytes()).hexdigest(),
    'paginas':len(pages),'dimensoes_pt':[float(x) for x in reader.pages[0].mediabox],
    'avisos_relevantes':[x for x in log.splitlines() if any(t in x for t in ['Warning','Overfull','Underfull','undefined','Error'])],
    'referencias_sem_interrogacao':not any('??' in p for p in pages),
    'marcadores':[{'pagina':i+1,'tabelas':re.findall(r'Tabela\s+\d+',p),'inicio':p[:130]} for i,p in enumerate(pages)],
    'limite':'Extração de texto e renderização não substituem inspeção visual; conferência das imagens realizada separadamente.'}
(HERE/'verificacao_pdf.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'pdf_extraido.txt').write_text('\n\n'.join(f'--- PAGINA {i+1} ---\n{p}' for i,p in enumerate(pages)),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
