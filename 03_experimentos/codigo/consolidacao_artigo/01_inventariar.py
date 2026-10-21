from comum import *
import platform,datetime
a=args();root=a.raiz;dest=a.destino
ev=read_csv(root/'03_experimentos/resultados/resultados_etapa3.csv')
prompt=read_csv(root/'03_experimentos/resultados/resultados_etapa1.csv')
tr=read_csv(root/'03_experimentos/resultados/treinos_etapa3.csv')
assert len(ev)==10 and all(r['depuracao']=='nao' for r in ev)
assert len(prompt)==4 and all(r['release_dados']=='original' for r in prompt)
train=[r for r in tr if r['depuracao']=='nao'];assert len(train)==6
logs=root/'03_experimentos/logs';runs=[];files=[]
for row in ev:
    baseline=row['variante']=='baseline_tamanho'
    run={'id':row['log_prefixo'],'tipo':'tamanho' if baseline else 'classificador','historico':row,
         'logs':{split:str((logs/(row['log_prefixo']+'_'+split+'.jsonl')).relative_to(root)).replace('\\','/') for split in (('teste','pareado') if baseline else ('validacao','teste','pareado'))}}
    if not baseline:run['receita']='03_experimentos/logs/'+row['rodada']+'.json'
    runs.append(run)
for row in prompt:runs.append({'id':Path(row['log']).stem,'tipo':'prompting','historico':row,'logs':{'pareado' if int(row['n_funcoes'])==1128 else 'teste':'03_experimentos/logs/'+row['log']}})
paths=set(p for r in runs for p in r['logs'].values())|set(r['receita'] for r in runs if 'receita'in r)
paths|={f'03_experimentos/resultados/{n}' for n in ('resultados_etapa1.csv','resultados_pareado.csv','resultados_etapa3.csv','treinos_etapa3.csv')}
paths|={p.relative_to(root).as_posix() for p in (root/'03_experimentos/dados/artigo_seminarios_2026/release_original').glob('*.jsonl')}
for path in sorted(paths):
    p=root/path
    if not p.exists():raise ValueError('Fonte essencial ausente: '+path)
    count=None;fields=None
    if p.suffix=='.jsonl':
        n=0;targets={0:0,1:0}
        with p.open(encoding='utf-8') as f:
            for line in f:
                if not line.strip():continue
                d=json.loads(line);n+=1;targets[int(d['target'])]+=1
                if fields is None:fields=list(d)
        count=n
    files.append({'arquivo':path,'sha256_atual_completo':sha(p),'bytes':p.stat().st_size,'n_linhas_jsonl':count,'schema_primeira_linha':fields})
manifest={'gerado_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':platform.python_version(),'numpy':np.__version__,'execucoes':runs,'treinos_oficiais':train,'fontes':files,'exclusoes':[{'rodada':r['rodada'],'motivo':'depuração'} for r in tr if r['depuracao']=='sim'],'limites':['Revisões históricas de código não registradas por execução.','Revisões de modelo e dados históricas são prefixos de 12 caracteres; hashes atuais completos não são metadados históricos completos.','Hash histórico da validação global não foi gravado nas avaliações.']}
write_json(dest/'manifesto.json',manifest)
write_csv(dest/'inventario.csv',[{k:v for k,v in f.items() if k!='schema_primeira_linha'} for f in files])
print('Fontes:',len(files),'execuções:',len(runs),'treinos oficiais:',len(train))
