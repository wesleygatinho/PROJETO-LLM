from pathlib import Path
import hashlib, json, datetime

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''): h.update(b)
    return h.hexdigest()
dest=OUT/'preservacao_antes.json'
if not dest.exists():
    files={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'03_experimentos').rglob('*') if p.is_file()}
    dest.write_text(json.dumps({'data_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'arquivos':files},indent=2),encoding='utf-8')
    source=ROOT/'04_escrita/artigo/seminarios_2026/revisao/introducao_2026-10-07/previa_rascunho_sbc.tex'
    (OUT/'previa_original_preservada.tex').write_bytes(source.read_bytes())
    print('Históricos preservados:',len(files))
else: print('Manifesto inicial já preservado.')
