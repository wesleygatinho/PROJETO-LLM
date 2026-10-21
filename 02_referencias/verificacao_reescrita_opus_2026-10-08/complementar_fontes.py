from pathlib import Path
import json,hashlib,urllib.request,sys
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
sources={
 'ullah':ROOT/'02_referencias/pdfs das referencias/Deteccao de vulnerabilidade métodos e modelos/Ullah, S - 2024.pdf',
 'saito':'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0118432&type=printable',
 'field':'https://bemlar.ism.ac.jp/zhuang/Refs/Refs/field2007jrssb.pdf'
}
record=[]
for key,src in sources.items():
    if isinstance(src,str):
        path=OUT/(key+'.pdf')
        assert not path.exists(),'Não sobrescrever fontes'
        req=urllib.request.Request(src,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=60) as r:blob=r.read()
        assert blob.startswith(b'%PDF'),src
        path.write_bytes(blob)
    else:path=src
    pdf=PdfReader(path)
    txt='\n\n'.join(f'=== PÁGINA FÍSICA {i} ===\n'+page.extract_text(extraction_mode='layout') for i,page in enumerate(pdf.pages,1))
    dest=OUT/(key+'_pdf.txt');dest.write_text(txt,encoding='utf-8')
    record.append({'chave':key,'pdf':path.relative_to(ROOT).as_posix(),'origem':str(src),'sha256_pdf':hashlib.sha256(path.read_bytes()).hexdigest(),'paginas':len(pdf.pages),'sha256_texto':hashlib.sha256(dest.read_bytes()).hexdigest(),'metadados':{str(k):str(v) for k,v in (pdf.metadata or {}).items()}})
    print(key,len(pdf.pages),txt[:1200])
(OUT/'inventario_complementar.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
