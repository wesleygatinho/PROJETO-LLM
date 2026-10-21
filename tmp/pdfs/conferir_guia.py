from pathlib import Path
import json, re
from PIL import Image, ImageOps, ImageDraw, ImageFont
from pypdf import PdfReader
import pdfplumber

root=Path(__file__).resolve().parents[2]
path=root/'output/pdf/Guia_Completo_do_Projeto_Mestrado_09-10-2026.pdf'
dest=root/'tmp/pdfs/render'
files=sorted(dest.glob('guia-*.png'))
font=ImageFont.truetype('C:/Windows/Fonts/calibrib.ttf',18)
sheets=[]
for i in range(0,len(files),4):
    sheet=Image.new('RGB',(940,1372),'#dce5e9')
    draw=ImageDraw.Draw(sheet)
    for j,f in enumerate(files[i:i+4]):
        im=Image.open(f).convert('RGB')
        im.thumbnail((447,632),Image.Resampling.LANCZOS)
        x=15+(j%2)*470; y=32+(j//2)*686
        sheet.paste(im,(x,y));draw.text((x,y-24),f'Página {i+j+1:02d}',fill='#142d42',font=font)
    target=dest/f'contato-{i//4+1:02d}.jpg';sheet.save(target,quality=94);sheets.append(str(target))
reader=PdfReader(path)
texts=[p.extract_text() for p in reader.pages]
assert len(texts)==34
assert all(len(t)>400 for t in texts)
assert not any('\ufffd' in t or '\u25a0' in t for t in texts)
bad=[]
with pdfplumber.open(path) as pdf:
    for n,p in enumerate(pdf.pages,1):
        for ch in p.chars:
            if ch['x0'] < 3 or ch['x1'] > p.width-3 or ch['top'] < 0 or ch['bottom'] > p.height:
                bad.append((n,ch['text'],round(ch['x0'],1),round(ch['x1'],1)))
assert not bad,bad[:20]
body='\n'.join(texts)
checks=['235.768','184.427','25.911','25.430','695','564','435','21,10%','50,62%','49,97%','47,92%','53,33%','4,63 GB','14,15 GB','12,49 GB','20,76 GB']
for v in checks:assert v in body,v
report={'pdf':str(path),'pages':len(texts),'word_count':len(body.split()),'size_bytes':path.stat().st_size,'contact_sheets':sheets,'page_characters':[len(t) for t in texts],'text_bounds':'ok','numeric_anchors':'ok'}
(root/'tmp/pdfs/verificacao_guia.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
