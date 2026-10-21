from pathlib import Path
import urllib.request,json,hashlib
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'03_experimentos/dados/artigo_seminarios_2026/tokenizer_3b'
DEST.mkdir(parents=True,exist_ok=True)
records=[]
for name,url in [('revisao_modelo.json','https://huggingface.co/api/models/Qwen/Qwen2.5-Coder-3B/revision/09d9bc5d376b'),('tokenizer.json','https://huggingface.co/Qwen/Qwen2.5-Coder-3B/resolve/09d9bc5d376b/tokenizer.json'),('tokenizer_config.json','https://huggingface.co/Qwen/Qwen2.5-Coder-3B/resolve/09d9bc5d376b/tokenizer_config.json'),('run_ft_oficial.py','https://raw.githubusercontent.com/DLVulDet/PrimeVul/main/os_expr/run_ft.py'),('revisao_modelo_7b.json','https://huggingface.co/api/models/Qwen/Qwen2.5-Coder-7B/revision/0396a76181e1'),('tokenizer_7b.json','https://huggingface.co/Qwen/Qwen2.5-Coder-7B/resolve/0396a76181e1/tokenizer.json')]:
    if (DEST/name).exists():data=(DEST/name).read_bytes()
    else:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=90) as r:data=r.read()
        (DEST/name).write_bytes(data)
    records.append({'arquivo':name,'url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
(DEST/'proveniencia.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(json.dumps(records,indent=2))
assert (DEST/'tokenizer.json').read_bytes()==(DEST/'tokenizer_7b.json').read_bytes(),'Tokenizers diferentes; não extrapolar a igualdade de entradas ao 7B.'
