from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
import pdfplumber, re, json, shutil

root=Path(__file__).resolve().parents[2]
build=root/'tmp/apresentacao_orientador'
out=root/'output/apresentacao_orientador'
src=build/'apresentacao_orientador_com_roteiro.pdf'
reader=PdfReader(src)
assert len(reader.pages)==45,len(reader.pages)
texts=[p.extract_text() for p in reader.pages]
assert all(len(t)>90 for t in texts)
assert 'Roteiro de fala' in texts[22]
for n in range(1,23):
    assert re.search(r'Roteiro\s*0?'+str(n)+r'\s*:',texts[22+n]),(n,texts[22+n][:70])
assert 'Roteiro' not in '\n'.join(texts[:22])
with pdfplumber.open(src) as pdf:
    bounds=[]
    for n,p in enumerate(pdf.pages,1):
        for ch in p.chars:
            if ch['x0']<10 or ch['x1']>p.width-10 or ch['top']<0 or ch['bottom']>p.height:
                bounds.append((n,ch['text'],ch['x0'],ch['x1'],ch['top'],ch['bottom']))
assert not bounds,bounds[:20]
log=(build/'apresentacao_orientador_com_roteiro.log').read_text(encoding='utf-8',errors='replace')
assert not re.search(r'Overfull \\[hv]box|^! ',log,re.M)
source=(out/'apresentacao_orientador.tex').read_text(encoding='utf-8')
assert len(re.findall(r'\\fala\{\d\d\}',source))==22
assert not re.search(r'—|–|\bLorem\b|\[Seu nome\]',source)
checks={3:['184.427','25.430','25.911','695','564'],8:['0,119','0,062','3,49%','11,00%'],10:['0,262','0,851','37,50%','49,20%','50,62%'],11:['55,23%','45,04%','51,60%','49,97%'],12:['4,63','14,15','12,49','20,76','59,6','47,1'],13:['88,06%','96,26%','98,71%'],14:['564','465','559','460','32','0,22']}
for p,anchors in checks.items():
    for a in anchors:assert a in texts[p],(p+1,a)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
files=sorted((build/'render').glob('slide-*.png'))
assert len(files)==45
contacts=[]
for start in range(0,len(files),6):
    sheet=Image.new('RGB',(1560,960),'#e0e6e9')
    draw=ImageDraw.Draw(sheet)
    for j,path in enumerate(files[start:start+6]):
        im=Image.open(path).convert('RGB');im.thumbnail((500,282),Image.Resampling.LANCZOS)
        x=10+(j%3)*520;y=27+(j//3)*320
        draw.text((x,y-22),f'Página {start+j+1:02d}',font=font,fill='#183349')
        sheet.paste(im,(x,y))
    path=build/'render'/f'contato-{start//6+1:02d}.jpg';sheet.save(path,quality=95);contacts.append(str(path))
shutil.copy2(src,out/src.name)
writer=PdfWriter()
for p in reader.pages[:22]:writer.add_page(p)
writer.add_metadata({'/Title':'Detecção de vulnerabilidades no PrimeVul - slides para apresentação','/Author':'PPGCC UFMA'})
with (out/'apresentacao_orientador_slides.pdf').open('wb') as stream:writer.write(stream)
report={'pages_full':45,'slides_main':18,'slides_backup':4,'speech_pages':22,'source_self_contained':True,'text_bounds':'ok','overfull_boxes':0,'numeric_anchors':'ok','contacts':contacts,'words_main_speech':sum(len(t.split()) for t in texts[23:41]),'outputs':[str(out/src.name),str(out/'apresentacao_orientador_slides.pdf'),str(out/'apresentacao_orientador.tex')]}
(build/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
