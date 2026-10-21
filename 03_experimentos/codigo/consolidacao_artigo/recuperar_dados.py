from pathlib import Path
import urllib.request, urllib.parse, http.cookiejar, json, re, hashlib, datetime, html
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'03_experimentos/dados/artigo_seminarios_2026/release_original'
DEST.mkdir(parents=True,exist_ok=True)
folder=(DEST.parent/'fontes_publicas/drive_original.html').read_text(encoding='utf-8')
files=dict((name,id) for id,name in re.findall(r'data-id="([\w-]+)"[^>]+data-tooltip="(primevul_[a-z_]+\.jsonl) Binary"',folder))
assert len(files)==6,files
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
records=[]
for name in sorted(files,key=lambda n:(n=='primevul_train.jsonl',n)):
    path=DEST/name; url='https://drive.usercontent.google.com/download?'+urllib.parse.urlencode({'id':files[name],'export':'download','confirm':'t'})
    try:
        if not path.exists():
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
            with opener.open(req,timeout=180) as response:
                initial=response.read(8192)
                if b'<html' in initial.lower() or b'<!doctype' in initial.lower():
                    body=initial+response.read()
                    (DEST/(name+'.erro.html')).write_bytes(body)
                    raise RuntimeError('Resposta HTML em vez de dados; preservada para diagnóstico')
                with path.with_suffix('.part').open('wb') as f:
                    f.write(initial)
                    for block in iter(lambda:response.read(2**20),b''):f.write(block)
            path.with_suffix('.part').rename(path)
        h=hashlib.sha256(); counts={0:0,1:0}
        with path.open('rb') as f:
            for line in f:
                h.update(line)
                if line.strip():counts[int(json.loads(line)['target'])]+=1
        record={'arquivo':name,'drive_id':files[name],'url':url,'bytes':path.stat().st_size,'sha256':h.hexdigest(),'contagens':counts,'estado':'recuperado'}
        records.append(record); print(json.dumps(record),flush=True)
    except Exception as e:
        record={'arquivo':name,'drive_id':files[name],'url':url,'estado':'falhou','erro':str(e)}
        records.append(record);print(json.dumps(record),flush=True)
(DEST/'recuperacao_dados.json').write_text(json.dumps({'data_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pasta_oficial':'19iLaNDS0z99N8kB_jBRTmDLehwZBolMY','arquivos':records},indent=2),encoding='utf-8')
