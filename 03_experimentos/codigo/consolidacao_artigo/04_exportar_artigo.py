from comum import *
import os
os.environ['MPLCONFIGDIR']=str(ROOT/'.runtime_artigo_2026/matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
a=args();out=a.destino
tables=out/'tabelas';tables.mkdir(exist_ok=True)
g=read_csv(out/'metricas_por_execucao.csv');p=read_csv(out/'metricas_pareadas.csv');sens=read_csv(out/'sensibilidade_truncamento.csv');corr=read_csv(out/'sensibilidade_correspondencia.csv')
m=json.loads((out/'manifesto.json').read_text(encoding='utf-8'));stats=json.loads((out/'estatistica.json').read_text(encoding='utf-8'))
def fmt(v,d=3):return f'{float(v):.{d}f}'.replace('.',',') if v not in ('',None) else '—'
def pct(v):return fmt(float(v)*100,2)
def md(path,title,headers,rows):
    text=title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
    text+='\n'.join('| '+' | '.join(str(v) for v in r)+' |' for r in rows)+'\n'
    path.write_text(text,encoding='utf-8');return text
short={r['id']:(('3B real' if r['historico']['benignas_por_vul']=='real' else '3B 1:1 tamanho' if 'ben1tam' in r['historico']['rodada'] else '3B 1:1') if '3B' in r['historico']['modelo'] else f'7B {r["historico"]["variante"].upper()} s{r["historico"]["seed"]}') if r['tipo']=='classificador' else 'Tamanho' for r in m['execucoes'] if r['tipo']!='prompting'}
configs=[]
for r in m['treinos_oficiais']:
    label=('3B real' if r['benignas_por_vul']=='real' else '3B 1:1 tamanho' if 'ben1tam' in r['rodada'] else '3B 1:1') if '3B' in r['modelo'] else '7B 1:1 tamanho s'+r['seed']
    configs.append([label,r['n_vul'],r['n_ben'],r['epocas'],r['melhor_epoca'],fmt(float(r['tempo_treino_s'])/3600,2),fmt(r['custo_total_usd'],2)])
pieces={}
pieces['T1']=md(tables/'T1_configuracoes.md','Tabela 1. Configurações de ajuste. Tempo corresponde ao treino registrado; custo inclui o tempo total registrado da rodada, ao preço histórico de US$ 0,50/h. As horas não representam orçamento igual entre receitas.',['Configuração','Vulneráveis','Benignas','Épocas','Selecionada','Treino (h)','Custo total (US$)'],configs)
prompts=[r for r in g if r['tipo']=='prompting' and r['split']=='teste']
pieces['T2']=md(tables/'T2_prompting.md','Tabela 2. Prompting no teste global (25.911 funções) e categorias no teste pareado (564 pares), pela regra YES/NO. Contexto do código: 8.192 tokens.',['Modelo','F1','Precisão','Revocação','FPR (%)','P-C','P-V','P-B','P-R'],[[r['rotulo'],fmt(r['f1']),fmt(r['precisao']),fmt(r['revocacao']),pct(r['fpr'])]+[next(q for q in p if q['rotulo']==r['rotulo'])[k] for k in ('P_C','P_V','P_B','P_R')] for r in prompts])
main=[r for r in g if r['tipo']!='prompting']
pieces['T3']=md(tables/'T3_global.md','Tabela 3. Teste global, 25.911 funções. F1/precisão/revocação/FPR usam o limiar de maior F1 no dev; FNR* e FPR* usam outro limiar, calibrado para FPR ≤ 0,5% no dev. FPR* é o valor efetivamente observado no teste. AUC usa os scores disponíveis.',['Configuração','F1','Precisão','Revocação','FPR (%)','AUC','FNR* (%)','FPR* (%)'],[[short[r['id']],fmt(r['f1']),fmt(r['precisao']),fmt(r['revocacao']),pct(r['fpr']),fmt(r['auc']),pct(r['fnr_limiar_fpr_dev']),pct(r['fpr_teste_limiar_fpr_dev'])] for r in main])
pieces['T4']=md(tables/'T4_pareado.md','Tabela 4. Teste pareado oficial, 564 pares. Categorias P-* usam o limiar F1 do dev; ordenação usa meio crédito para empates e independe de limiar. A coluna 465 considera apenas pares com ambas as versões não truncadas.',['Configuração','P-C','P-V','P-B','P-R','Empates','Ord. 564 (%)','Ord. 465 (%)'],[[short[r['id']]]+[r[k] for k in ('P_C','P_V','P_B','P_R','empatados')]+[pct(r['ordenacao']),pct(next(s for s in sens if s['id']==r['id'])['ordenacao'])] for r in p if r['politica']=='dev_f1'])
resources=[]
for r in m['execucoes']:
    h=r['historico']
    if r['tipo']=='classificador' and '7B' in h['modelo']:resources.append([short[r['id']],fmt(h['memoria_modelo_gb'],2),fmt(h['memoria_pico_gb'],2),fmt(float(h['tempo_por_funcao_s'])*1000,1),fmt(h['custo_teste_usd'],4)])
pieces['T5']=md(tables/'T5_recursos.md','Tabela 5. Recursos históricos do 7B na NVIDIA A40, Transformers, 32.768 tokens por lote e contexto de 2.048. GB decimais de memória alocada após carga e pico na janela que abrange dev/teste/pareado. Tempo amortizado do teste em lotes; custo computacional estimado ao preço histórico US$ 0,50/h. As seeds não são repetições independentes de desempenho.',['Configuração','Após carga (GB)','Pico (GB)','Tempo/função (ms)','Custo teste (US$)'],resources)
pieces['T6']=md(tables/'T6_incerteza.md','Tabela 6. Ordenação pareada do 7B: média das três seeds, dispersão descritiva entre seeds e IC percentil de 95% por bootstrap de 550 grupos projeto/commit (10.000 réplicas), condicional aos três modelos observados. O intervalo da diferença mantém alinhamento entre variantes.',['Medida','Estimativa (%) ou p.p.','DP seeds (p.p.)','IC95% inferior','IC95% superior'],[[s['variante'].upper(),pct(s['media']),fmt(s['desvio_padrao_seeds']*100,2),pct(s['ic95_media_inferior_commit']),pct(s['ic95_media_superior_commit'])] for s in stats['seeds_7b']]+[['NF4 − BF16 (p.p.)',fmt(stats['comparacoes'][-1]['diferenca']*100,2),'—',fmt(stats['comparacoes'][-1]['ic95_inferior_commit']*100,2),fmt(stats['comparacoes'][-1]['ic95_superior_commit']*100,2)]])
pieces['T7']=md(tables/'T7_sensibilidade_correspondencia.md','Tabela 7 suplementar. Ordenação no conjunto oficial (564), sem cinco correspondências incompatíveis com os patches (559) e, entre esses, sem truncamento (460). Recortes retrospectivos; não certificam a correção de todos os pares restantes.',['Configuração','Ord. 564 (%)','Ord. 559 (%)','Ord. 460 (%)'],[[short[r['id']],pct(next(q for q in p if q['id']==r['id'] and q['politica']=='dev_f1')['ordenacao']),pct(r['ordenacao_sem_cinco']),pct(r['ordenacao_sem_cinco_sem_truncamento'])] for r in corr])
(out/'tabelas_artigo.md').write_text('\n\n'.join(pieces.values()),encoding='utf-8')
figdir=ROOT/'04_escrita/artigo/seminarios_2026/figuras';figdir.mkdir(exist_ok=True)
fig,ax=plt.subplots(figsize=(6.7,3.3),layout='constrained')
for variant,color,offset in [('nf4','#155e75',-.08),('bf16','#a74622',.08)]:
    entries=sorted([r for r in main if r['variante']==variant and r['rotulo'].startswith('7B')],key=lambda r:int(r['seed']))
    point=[next(z for z in stats['por_execucao'] if z['id']==r['id']) for r in entries]
    y=np.array([r['ordenacao']*100 for r in point]);low=np.array([r['ic95_inferior_commit']*100 for r in point]);high=np.array([r['ic95_superior_commit']*100 for r in point])
    ax.errorbar(np.arange(1,4)+offset,y,yerr=[y-low,high-y],fmt='o',capsize=4,color=color,label=variant.upper())
ax.axhline(50,color='#666666',ls='--',lw=1);ax.set_xticks([1,2,3]);ax.set_xlabel('Seed');ax.set_ylabel('Ordenação com meio crédito (%)');ax.set_ylim(37,62);ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,ncol=2);ax.grid(axis='y',alpha=.2)
fig.savefig(figdir/'ordenacao_7b.png',dpi=220);fig.savefig(figdir/'ordenacao_7b.svg');plt.close(fig)
provenance={str(p.relative_to(ROOT)):sha(p) for p in list(out.glob('*.csv'))+list(out.glob('*.json'))+list(tables.glob('*.md'))+list(figdir.glob('ordenacao_7b.*'))}
write_json(out/'proveniencia_exports.json',{'fontes':provenance,'codigo':{p.relative_to(ROOT).as_posix():sha(p) for p in Path(__file__).parent.glob('*.py')},'numpy':np.__version__,'matplotlib':matplotlib.__version__,'legendas':'Unidades e denominadores explícitos; figura mostra intervalo amostral condicional, não IC de treino.'})
print('Exportadas 7 tabelas e figura de ordenação.')
