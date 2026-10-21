from comum import *
import urllib.request,urllib.parse,re
base=ROOT/'03_experimentos/dados/artigo_seminarios_2026/commits_inspecao'
audit_dir=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08'
rows=json.loads((audit_dir/'pares_inspecao.json').read_text(encoding='utf-8'))
data=read_jsonl(ROOT/'03_experimentos/dados/artigo_seminarios_2026/release_original/primevul_test_paired.jsonl')
meta=json.loads((base/'proveniencia.json').read_text(encoding='utf-8'))
report=[]
for source in meta['fontes']:
    if source['estado']!='recuperado':continue
    proj=source['projeto'];info=json.loads((base/(proj+'.json')).read_text(encoding='utf-8'))
    candidate=next(r for r in rows if r['project']==proj and r['commit_id']==source['commit'])
    signatures={'libjpeg':'PrepareForDecoding','php-src':'openssl_encrypt','rizin':'static RzList *relocs','linux-2.6':'sctp_sf_violation_paramlen','drogon':'HttpFileImpl::save('}
    files=[f for f in info['files'] if signatures[proj] in f.get('patch','')]
    norm=lambda t:re.sub(r'\s+','',t)
    old=data[candidate['pos_vulneravel']]['func'];corrected=data[candidate['pos_corrigida']]['func']
    for file in files:
        texts={};refs={}
        for kind,revision in [('pai',source['pais'][0]),('commit',source['commit'])]:
            url=f'https://raw.githubusercontent.com/{source["repo"]}/{revision}/'+urllib.parse.quote(file['filename'])
            path=base/(proj+'_'+kind+Path(file['filename']).suffix)
            if path.exists():body=path.read_bytes()
            else:
                with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'UFMA-reproducibilidade'}),timeout=60) as response:body=response.read()
                path.write_bytes(body)
            texts[kind]=body.decode('utf-8','replace');refs[kind]={'url':url,'sha256':sha(path),'arquivo':path.relative_to(ROOT).as_posix()}
        assert norm(old) in norm(texts['pai']) and norm(corrected) in norm(texts['commit']),(proj,'Funções não encontradas nas fontes')
        report.append({'par_id':candidate['par_id'],'pos_vulneravel':candidate['pos_vulneravel'],'pos_corrigida':candidate['pos_corrigida'],'project':proj,'commit_id':source['commit'],'arquivo_original':file['filename'],'vulneravel_encontrada_pai':norm(old) in norm(texts['pai']),'corrigida_encontrada_pai':norm(corrected) in norm(texts['pai']),'corrigida_encontrada_commit':norm(corrected) in norm(texts['commit']),'funcao_corrigida_diferente_da_funcao_alterada':True,'fontes':refs,'decisao':'Manter referência oficial; remover somente estes pares em sensibilidade documentada. Não substituir membros sem previsões.'})
write_json(audit_dir/'inspecao_correspondencia_commits.json',report)
print(json.dumps(report,ensure_ascii=False,indent=2))
