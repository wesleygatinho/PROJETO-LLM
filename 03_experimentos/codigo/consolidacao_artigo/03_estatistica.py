from comum import *
from collections import defaultdict
a=args();out=a.destino
m=json.loads((out/'manifesto.json').read_text(encoding='utf-8'))
rows=read_csv(out/'metricas_por_execucao.csv');pairs=read_csv(out/'pares_auditados.csv')
runs=[r for r in m['execucoes'] if r['tipo']!='prompting']
values=np.column_stack([np.load(out/(r['id']+'.npz'))['pair_value'] for r in runs])
groups=defaultdict(list)
for i,p in enumerate(pairs):groups[(p['project'],p['commit_id'])].append(i)
cluster_indices=list(groups.values());G=len(cluster_indices)
aggregate=np.vstack([values[index].sum(axis=0) for index in cluster_indices]);sizes=np.array([len(index) for index in cluster_indices])
reps=10000;seed=20261008
rng=np.random.default_rng(seed);replicates=np.empty((reps,values.shape[1]));pair_replicates=np.empty_like(replicates)
for start in range(0,reps,250):
    n=min(250,reps-start);indices=rng.integers(0,G,size=(n,G))
    replicates[start:start+n]=aggregate[indices].sum(axis=1)/sizes[indices].sum(axis=1)[:,None]
    pi=rng.integers(0,len(pairs),size=(n,len(pairs)))
    pair_replicates[start:start+n]=values[pi].mean(axis=1)
def interval(v):return [float(x) for x in np.quantile(v,[.025,.975])]
records=[]
for i,r in enumerate(runs):
    ci=interval(replicates[:,i]);ci_pair=interval(pair_replicates[:,i]);half=interval(replicates[:5000,i])
    records.append({'id':r['id'],'rotulo':next(x['rotulo'] for x in rows if x['id']==r['id']),'ordenacao':float(values[:,i].mean()),'ic95_inferior_commit':ci[0],'ic95_superior_commit':ci[1],'ic95_inferior_par':ci_pair[0],'ic95_superior_par':ci_pair[1],'variacao_endpoint_5000_10000':max(abs(ci[j]-half[j]) for j in (0,1))})
indices={r['id']:i for i,r in enumerate(runs)}
seven={v:sorted([r for r in runs if r['tipo']=='classificador' and '7B' in r['historico']['modelo'] and r['historico']['variante']==v],key=lambda r:int(r['historico']['seed'])) for v in ('nf4','bf16')}
summaries=[];comparisons=[]
for variant,rs in seven.items():
    ix=[indices[r['id']] for r in rs];means=values[:,ix].mean(axis=0);boot=replicates[:,ix].mean(axis=1)
    ci=interval(boot);ci_pair=interval(pair_replicates[:,ix].mean(axis=1))
    summaries.append({'variante':variant,'seeds':[int(r['historico']['seed']) for r in rs],'media':float(means.mean()),'desvio_padrao_seeds':float(means.std(ddof=1)),'minimo':float(means.min()),'maximo':float(means.max()),'ic95_media_inferior_commit':ci[0],'ic95_media_superior_commit':ci[1],'ic95_media_inferior_par':ci_pair[0],'ic95_media_superior_par':ci_pair[1]})
for rn,rb in zip(seven['nf4'],seven['bf16']):
    ni,bi=indices[rn['id']],indices[rb['id']]
    assert rn['historico']['rodada']==rb['historico']['rodada'] and rn['historico']['epoca']==rb['historico']['epoca']
    delta=values[:,ni]-values[:,bi];ci=interval(replicates[:,ni]-replicates[:,bi])
    comparisons.append({'comparacao':'NF4 - BF16','seed':int(rn['historico']['seed']),'diferenca':float(delta.mean()),'ic95_inferior_commit':ci[0],'ic95_superior_commit':ci[1]})
ni=[indices[r['id']] for r in seven['nf4']];bi=[indices[r['id']] for r in seven['bf16']]
delta=(values[:,ni]-values[:,bi]).mean(axis=1);ci=interval((replicates[:,ni]-replicates[:,bi]).mean(axis=1))
comparisons.append({'comparacao':'NF4 - BF16 média das três seeds','seed':None,'diferenca':float(delta.mean()),'ic95_inferior_commit':ci[0],'ic95_superior_commit':ci[1]})
inspection=json.loads((out/'inspecao_correspondencia_commits.json').read_text(encoding='utf-8'))
excluded={r['par_id'] for r in inspection};mask=np.array([p['par_id'] not in excluded for p in pairs]);assert int(mask.sum())==559
restricted=[]
for i,r in enumerate(runs):
    restricted.append({'id':r['id'],'rotulo':records[i]['rotulo'],'n_pares':int(mask.sum()),'ordenacao_sem_cinco':float(values[mask,i].mean()),'variacao_pp':float((values[mask,i].mean()-values[:,i].mean())*100),'ordenacao_sem_cinco_sem_truncamento':float(values[mask&np.load(out/(r['id']+'.npz'))['pair_mask'],i].mean()),'n_sem_cinco_sem_truncamento':int((mask&np.load(out/(r['id']+'.npz'))['pair_mask']).sum())})
metadata={'replicas':reps,'seed':seed,'metodo':'Bootstrap percentil, quantis 0.025 e 0.975; primário por project+commit, sensibilidade por par','grupos_commit':G,'n_pares':len(pairs),'n_projetos':len({p['project'] for p in pairs}),'grupo_maximo_pares':max(sizes.tolist()),'hipotese':'Grupos de commit intercambiáveis/independentes; possível dependência entre commits do mesmo projeto não eliminada','condicional':'Modelos já treinados, três seeds observadas, limiares fixos. Não representa variabilidade de futuros treinos.','pareado_e_global_nao_independentes':True,'p_valores':'Não calculados nem usados; p-valores históricos não transportados','estabilidade_endpoint_max':max(r['variacao_endpoint_5000_10000'] for r in records)}
write_json(out/'estatistica.json',{'parametros':metadata,'por_execucao':records,'seeds_7b':summaries,'comparacoes':comparisons,'sensibilidade_cinco':restricted})
write_csv(out/'intervalos.csv',records);write_csv(out/'comparacoes.csv',comparisons);write_csv(out/'sensibilidade_correspondencia.csv',restricted)
print(json.dumps({'parametros':metadata,'seeds_7b':summaries,'comparacoes':comparisons,'sensibilidade_cinco':restricted},ensure_ascii=False,indent=2))
