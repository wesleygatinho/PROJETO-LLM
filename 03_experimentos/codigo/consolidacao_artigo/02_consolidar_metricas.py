from comum import *
import re,datetime,difflib
from tokenizers import Tokenizer
a=args();root=a.raiz;out=a.destino
manifest=json.loads((out/'manifesto.json').read_text(encoding='utf-8'))
data_dir=root/'03_experimentos/dados/artigo_seminarios_2026/release_original'
data={s:read_jsonl(data_dir/f'primevul_{f}.jsonl') for s,f in [('teste','test'),('validacao','valid'),('pareado','test_paired'),('validacao_pareada','valid_paired')]}
assert [(len(data[s]),sum(d['target'] for d in data[s])) for s in data]==[(25911,695),(25430,699),(1128,564),(1124,562)]
pairs=official_pairs(data['pareado'],allow_official_repeated_corrected=True);devpairs=official_pairs(data['validacao_pareada'],allow_official_repeated_corrected=True)
assert len({d['idx'] for d in data['teste']})==25911
assert len({d['idx'] for d in data['validacao']})==25430
recovery=json.loads((data_dir/'recuperacao_dados.json').read_text(encoding='utf-8'))
hashes={r['arquivo']:r['sha256'] for r in recovery['arquivos'] if r['estado']=='recuperado'}
for run in manifest['execucoes']:
    h=run['historico'];key='dados_sha256_teste' if run['tipo']!='prompting' else 'dados_sha256'
    file='primevul_test_paired.jsonl' if run['tipo']=='prompting' and 'pareado' in run['logs'] else 'primevul_test.jsonl'
    assert hashes[file].startswith(h[key]),(run['id'],'hash histórico incompatível')
for row in manifest['treinos_oficiais']:assert hashes['primevul_train.jsonl'].startswith(row['dados_sha256'])
audits=[];pairrows=[];ambiguities=[]
from collections import defaultdict
reused={}
for split in ('pareado','validacao_pareada'):
    by=defaultdict(list)
    for pos,row in enumerate(data[split]):by[row['idx']].append(pos)
    reused[split]=[{'idx':idx,'posicoes':positions,'target':data[split][positions[0]]['target'],'project':data[split][positions[0]]['project'],'commit_id':data[split][positions[0]]['commit_id'],'mesmo_codigo':len({data[split][i]['func'] for i in positions})==1} for idx,positions in by.items() if len(positions)>1]
write_json(out/'reutilizacoes_release_oficial.json',reused)
for index,(v,b) in enumerate(pairs):
    x,y=data['pareado'][v],data['pareado'][b]
    def header(row):return re.sub(r'\s+',' ',row['func'].split('{',1)[0]).strip()
    hx,hy=header(x),header(y)
    identical=x['func']==y['func']
    row={'par_id':f'primevul_original_test_{x["idx"]}_{y["idx"]}','pos_vulneravel':int(v),'pos_corrigida':int(b),'idx_vulneravel':x['idx'],'idx_corrigida':y['idx'],'project':x['project'],'commit_id':x['commit_id'],'cabecalho_igual':hx==hy,'codigo_identico':identical,'sha256_func_vulneravel':hashlib.sha256(x['func'].encode()).hexdigest(),'sha256_func_corrigida':hashlib.sha256(y['func'].encode()).hexdigest()}
    pairrows.append(row)
    if hx!=hy or identical:ambiguities.append({**row,'cabecalho_vulneravel':hx[:500],'cabecalho_corrigida':hy[:500],'diff':'\n'.join(difflib.unified_diff(x['func'].splitlines(),y['func'].splitlines(),n=2))})
write_csv(out/'pares_auditados.csv',pairrows)
write_json(out/'pares_inspecao.json',ambiguities)

tokenizer=Tokenizer.from_file(str(root/'03_experimentos/dados/artigo_seminarios_2026/tokenizer_3b/tokenizer.json'))
tokenizer.no_truncation();tokenizer.no_padding()
lengths={};truncated={};tokens_pair=None
for split in ('validacao','teste','pareado'):
    cache=out/f'tokenizacao_{split}.npz'
    if cache.exists():
        loaded=np.load(cache);lengths[split]=loaded['n_tokens'];truncated[split]=loaded['truncada']
    else:
        raw=[];tok_pairs=[]
        for start in range(0,len(data[split]),500):
            encoded=tokenizer.encode_batch([d['func'] for d in data[split][start:start+500]],add_special_tokens=False)
            raw.extend(len(e.ids) for e in encoded)
            if split=='pareado':tok_pairs.extend(e.ids[:2048] for e in encoded)
        raw=np.asarray(raw);lengths[split]=np.minimum(raw,2048);truncated[split]=raw>2048
        np.savez_compressed(cache,n_tokens=lengths[split],truncada=truncated[split])
        if split=='pareado':tokens_pair=tok_pairs
    print('Tokens reconstruídos:',split,flush=True)
if tokens_pair is None:tokens_pair=[e.ids[:2048] for e in tokenizer.encode_batch([d['func'] for d in data['pareado']],add_special_tokens=False)]
identical_tokens=np.array([tokens_pair[v]==tokens_pair[b] for v,b in pairs])
write_json(out/'tokenizacao_proveniencia.json',{'tokenizers':__import__('tokenizers').__version__,'revisao_modelo_recuperada':json.loads((root/'03_experimentos/dados/artigo_seminarios_2026/tokenizer_3b/revisao_modelo.json').read_text())['sha'],'historico':'Baseline não registra revisão própria do tokenizer. Artefato do modelo 3B histórico foi usado e todos os comprimentos de teste e pareado são confrontados abaixo.','pares_tokens_identicos_2048':int(identical_tokens.sum()),'pares_ambos_nao_truncados':int((~truncated['pareado'][pairs].any(axis=1)).sum())})

global_rows=[];paired_rows=[];sensitivity=[];divergences=[];epoch_rows=[]
for run in manifest['execucoes']:
    rid=run['id'];h=run['historico'];logs={s:verify_alignment(read_jsonl(root/p),data[s]) for s,p in run['logs'].items()}
    audits.append({'execucao':rid,'splits':{s:{'n':len(rows),'pos_idx_project_commit_target':'iguais à fonte oficial','pos_unicas':True} for s,rows in logs.items()}})
    if run['tipo']=='prompting':
        split=next(iter(logs));rows=logs[split];y=np.array([d['target'] for d in rows]);s=np.array([d['pred'] for d in rows]);m=metrics(y,s,.5)
        global_rows.append({'id':rid,'rotulo':'Prompt '+('3B' if '3B' in h['modelo'] else '7B'),'tipo':'prompting','split':split,'politica':'parser histórico YES/NO','limiar':None,'auc':None,**m,'n':len(rows),'indefinidos':sum(d['status']!='ok' for d in rows),'truncadas':sum(d['truncada'] for d in rows)})
        for k in ('tp','fp','fn','tn'):assert m[k]==int(h[k]),(rid,k)
        if split=='pareado':paired_rows.append({'id':rid,'rotulo':'Prompt '+('3B' if '3B' in h['modelo'] else '7B'),'politica':'parser histórico YES/NO',**paired(s,pairs,.5),'ordenacao':None,'ordenados':None,'empatados':None})
        continue
    scores={s:np.array([d['nota'] for d in rows]) for s,rows in logs.items()};labels={s:np.array([d['target'] for d in rows]) for s,rows in logs.items()}
    baseline=run['tipo']=='tamanho'
    if baseline:
        for split in ('teste','pareado'):assert np.array_equal(scores[split],lengths[split]),('Tokenizer diverge baseline',split)
        scores['validacao']=lengths['validacao'].astype(float);labels['validacao']=np.array([d['target'] for d in data['validacao']])
        tag='Tamanho';seed=None;variant='tamanho'
    else:
        for split in logs:
            assert np.array_equal(np.array([d['n_tokens'] for d in logs[split]]),lengths[split]),('comprimentos divergentes',rid,split)
            assert np.array_equal(np.array([d['truncada'] for d in logs[split]]),truncated[split]),('truncamento divergente',rid,split)
        tag=('7B' if '7B' in h['modelo'] else '3B')+' '+({'real':'real','1':'1:1'}[h['benignas_por_vul']])+(' tamanho' if 'ben1tam' in h['rodada'] else '')+' '+h['variante']+' s'+h['seed']
        seed=int(h['seed']);variant=h['variante']
        recipe=json.loads((root/run['receita']).read_text(encoding='utf-8'))
        entries=[]
        for e in recipe['epocas']:
            tie=e.get('pareado_empatados');adjusted=e['pareado_ordenados_pct']+100*tie/(2*e['pareado_pares']) if tie is not None else None
            entries.append({'epoca':e['epoca'],'estrita_pct':e['pareado_ordenados_pct'],'empates':tie,'ajustada_reconstruida_pct':adjusted,'auc':e['auc_validacao']})
        historical=max(entries,key=lambda e:(e['estrita_pct'],e['auc']))['epoca']
        corrected=max(entries,key=lambda e:(e['ajustada_reconstruida_pct'],e['auc']))['epoca'] if all(e['ajustada_reconstruida_pct'] is not None for e in entries) else None
        epoch_rows.append({'rodada':h['rodada'],'receita_melhor_epoca':recipe['melhor_epoca'],'historica_estrita':historical,'ajustada_reconstruida':corrected,'mesma':corrected==historical if corrected is not None else None,'limite':'Percentuais por época arredondados, não previsões por época' if corrected is not None else 'Empates por época não registrados; não afirmar manutenção pelo critério ajustado','epocas':entries})
        assert int(h['epoca'])==int(recipe['melhor_epoca'])==historical
    t,fdev=best_f1(labels['validacao'],scores['validacao']);tv=fpr_threshold(labels['validacao'],scores['validacao'])
    m=metrics(labels['teste'],scores['teste'],t);mz=metrics(labels['teste'],scores['teste'],0);mv=metrics(labels['teste'],scores['teste'],tv)
    key={'id':rid,'rotulo':tag,'tipo':run['tipo'],'split':'teste','seed':seed,'variante':variant,'epoca':h['epoca'],'n':len(labels['teste']),'politica':'maior F1 no dev reconstruído','limiar':t,'limiar_historico_arredondado':float(h['limiar_decisao']),'f1_dev':fdev,'auc':auc(labels['teste'],scores['teste']),'limiar_fpr_dev':tv,'fnr_limiar_fpr_dev':mv['fnr'],'fpr_teste_limiar_fpr_dev':mv['fpr'],'fpr_dev':metrics(labels['validacao'],scores['validacao'],tv)['fpr'],'truncadas':int(truncated['teste'].sum()),**m}
    global_rows.append(key)
    for name,value in [('auc',key['auc']),('f1_limiar_validacao',m['f1']),('precisao_limiar_validacao',m['precisao']),('revocacao_limiar_validacao',m['revocacao']),('fpr_limiar_validacao',m['fpr']),('vds',mv['fnr']),('fpr_teste_no_limiar_vds',mv['fpr']),('f1_validacao_no_limiar',fdev)]:
        reported=float(h[name]);rounded=round(value,4)
        if rounded!=reported:divergences.append({'id':rid,'campo':name,'historico':reported,'reconstruido':value,'arredondado4':rounded,'delta':value-reported,'causa':'Reconstrução a partir dos scores arredondados; investigar fronteira/precisão. Histórico preservado.'})
    historical_dec=metrics(labels['teste'],np.array([d['pred'] for d in logs['teste']]),.5)
    if not baseline:
        for k in ('tp','fp','fn','tn'):assert historical_dec[k]==int(h[k]),(rid,k)
        assert np.array_equal(np.array([d['pred'] for d in logs['teste']]),(scores['teste']>0).astype(int))
    else:
        # Reconstrução do corte abaixo do inteiro deve reproduzir a decisão original.
        for k in ('tp','fp','fn','tn'):assert m[k]==int(h[k]),(rid,k,m[k],h[k])
    for policy,threshold in [('dev_f1',t),('historico',float(h['limiar_decisao']) if baseline else 0)]:
        pr=paired(scores['pareado'],pairs,threshold)
        paired_rows.append({'id':rid,'rotulo':tag,'politica':policy,'limiar':threshold,**pr})
        if policy=='historico':
            for k in ('P_C','P_V','P_B','P_R'):assert pr[k]==int(h[k]),(rid,k,pr[k],h[k])
            assert pr['empatados']==int(h['pares_empatados'])
            assert round(pr['ordenacao']*100,2)==float(h['pares_ordenados_ajust_pct'])
    mask=~truncated['pareado'][pairs].any(axis=1)
    sensitivity.append({'id':rid,'rotulo':tag,'recorte':'ambas não truncadas',**paired(scores['pareado'],pairs,t,mask)})
    pairval=np.where(scores['pareado'][pairs[:,0]]>scores['pareado'][pairs[:,1]],1,np.where(scores['pareado'][pairs[:,0]]==scores['pareado'][pairs[:,1]],.5,0))
    np.savez_compressed(out/(rid+'.npz'),pair_value=pairval,pair_mask=mask,identical_tokens=identical_tokens,global_scores=scores['teste'],global_labels=labels['teste'],threshold=t)
    print('Reconstruída:',tag,'F1',round(m['f1'],4),'ord',round(pairval.mean()*100,2),flush=True)
write_csv(out/'metricas_por_execucao.csv',global_rows);write_csv(out/'metricas_pareadas.csv',paired_rows);write_csv(out/'sensibilidade_truncamento.csv',sensitivity)
write_json(out/'divergencias.json',divergences);write_json(out/'selecao_epocas.json',epoch_rows)
write_json(out/'auditoria_integridade.json',{'data_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release':'original oficial; hashes completos atuais coincidem com prefixos históricos disponíveis','pareado_teste':len(pairs),'pareado_validacao':len(devpairs),'sem_exclusoes':True,'func_hash_nulo_nao_usado':True,'identidade':audits,'cabecalhos_a_inspecionar':len(ambiguities),'reutilizacoes_oficiais_documentadas':reused,'limites':['A identidade foi conferida contra a release oficial; isso não é uma nova auditoria humana dos rótulos/vulnerabilidades.','A release oficial reutiliza membros corrigidos; posições são únicas, idx de corrigidas não é sempre único. Dependência considerada por agrupamento de commit.','Revisão própria do tokenizer e hashes completos históricos não registrados.','Scores foram gravados com 5 casas; reconstrução não recupera precisão interna ausente.'],'divergencias_numericas':len(divergences)})
print('Concluído. Divergências:',len(divergences),'pares para inspeção:',len(ambiguities))
