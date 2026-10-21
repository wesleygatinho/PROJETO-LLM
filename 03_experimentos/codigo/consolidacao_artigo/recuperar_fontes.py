"""Recuperação de fontes públicas; não executa código baixado nem acessa pesos/RunPod."""
from pathlib import Path
import urllib.request, json, re, hashlib, datetime

ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'03_experimentos/dados/artigo_seminarios_2026/fontes_publicas'
DEST.mkdir(parents=True,exist_ok=True)
URL='https://drive.google.com/drive/folders/19iLaNDS0z99N8kB_jBRTmDLehwZBolMY'
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read()
records=[]
for name,url in [('primevul_readme_oficial.md','https://raw.githubusercontent.com/DLVulDet/PrimeVul/main/README.md'),('calc_vd_score_oficial.py','https://raw.githubusercontent.com/DLVulDet/PrimeVul/main/calc_vd_score.py'),('drive_original.html',URL)]:
    try:
        data=get(url); (DEST/name).write_bytes(data)
        records.append({'arquivo':name,'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'estado':'recuperado'})
        if name.endswith('.html'):
            text=data.decode('utf-8','replace')
            for m in re.finditer('primevul_[a-z_]+\\.jsonl',text):
                print(text[max(0,m.start()-220):m.end()+120])
    except Exception as e:records.append({'arquivo':name,'url':url,'estado':'falhou','erro':str(e)})
(DEST/'recuperacao_fontes.json').write_text(json.dumps({'data_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fontes':records},indent=2),encoding='utf-8')
print(json.dumps(records,indent=2))
