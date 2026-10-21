from comum import *
import urllib.request,datetime
out=ROOT/'03_experimentos/dados/artigo_seminarios_2026/commits_inspecao';out.mkdir(parents=True,exist_ok=True)
sources=[('libjpeg','thorfdbg/libjpeg','187035b9726710b4fe11d565c7808975c930895d'),('php-src','php/php-src','095cbc48a8f0090f3b0abc6155f2b61943c9eafb'),('rizin','rizinorg/rizin','58926dffbe819fe9ebf5062f7130e026351cae01'),('linux-2.6','torvalds/linux','ba0166708ef4da7eeb61dd92bbba4d5a749d6561'),('drogon','drogonframework/drogon','3c785326c63a34aa1799a639ae185bc9453cb447')]
records=[]
for project,repo,commit in sources:
    url=f'https://api.github.com/repos/{repo}/commits/{commit}'
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'UFMA-reproducibilidade','Accept':'application/vnd.github+json'}),timeout=60) as r:body=r.read()
        p=out/(project+'.json');p.write_bytes(body);info=json.loads(body)
        records.append({'projeto':project,'repo':repo,'commit':commit,'url':url,'sha256':sha(p),'pais':[p['sha'] for p in info['parents']],'arquivos':[f['filename'] for f in info['files']],'estado':'recuperado'})
        print(project,info['commit']['message'][:250]);print('\n'.join(f.get('patch','')[:7500] for f in info['files'] if any(t in f.get('patch','') for t in ('PrepareForDecoding','openssl_encrypt','relocs','sctp_sf_violation','HttpFileImpl::save'))))
    except Exception as e:records.append({'projeto':project,'url':url,'estado':'falhou','erro':str(e)})
write_json(out/'proveniencia.json',{'data_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fontes':records})
