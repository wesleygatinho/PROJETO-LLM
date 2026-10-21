from pathlib import Path
from pypdf import PdfReader
from hashlib import sha256
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sources={'diversevul':'Datasets e benchmarks/Chen, Y - 2023.pdf','linevul':'Ref Adicionadas/LineVul - 2022.pdf','reveal':'Ref Adicionadas/Saikat Chakraborty - 2020.pdf','devign':'Deteccao de vulnerabilidade métodos e modelos/Zhou, Y - 2019.pdf'}
records=[]
for key,relative in sources.items():
    path=ROOT/'02_referencias/pdfs das referencias'/relative
    pdf=PdfReader(path)
    text='\n\n'.join(f'=== PÁGINA FÍSICA {i} ===\n'+page.extract_text(extraction_mode='layout') for i,page in enumerate(pdf.pages,1))
    dest=OUT/(key+'_pdf.txt')
    dest.write_text(text,encoding='utf-8')
    records.append({'chave':key,'pdf':path.relative_to(ROOT).as_posix(),'sha256_pdf':sha256(path.read_bytes()).hexdigest(),'paginas':len(pdf.pages),'extracao':dest.relative_to(ROOT).as_posix(),'sha256_extracao':sha256(dest.read_bytes()).hexdigest(),'metadados':{str(k):str(v) for k,v in (pdf.metadata or {}).items()}})
    print(key,len(pdf.pages),text[:2100])
(OUT/'inventario.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
