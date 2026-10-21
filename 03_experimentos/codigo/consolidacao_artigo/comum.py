from pathlib import Path
import sys, csv, json, hashlib, argparse
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'.runtime_artigo_2026'))
import numpy as np

def args():
    p=argparse.ArgumentParser()
    p.add_argument('--raiz',type=Path,default=ROOT)
    p.add_argument('--destino',type=Path,default=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08')
    a=p.parse_args();a.destino.mkdir(parents=True,exist_ok=True);return a
def read_jsonl(path):
    with path.open(encoding='utf-8') as f:return [json.loads(l) for l in f if l.strip()]
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_json(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def write_csv(path,rows):
    if not rows:raise ValueError('Tabela vazia: '+str(path))
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
def auc(y,s):
    y=np.asarray(y);s=np.asarray(s);positive=int(y.sum());negative=len(y)-positive
    if not positive or not negative:return None
    order=np.argsort(s,kind='stable'); sorted_s=s[order]
    bounds=np.r_[0,np.flatnonzero(sorted_s[1:]!=sorted_s[:-1])+1,len(s)]
    ranks=np.empty(len(s),dtype=float)
    for start,end in zip(bounds[:-1],bounds[1:]):ranks[order[start:end]]=(start+1+end)/2
    return float((ranks[y==1].sum()-positive*(positive+1)/2)/(positive*negative))
def metrics(y,s,t):
    y=np.asarray(y);pred=np.asarray(s)>t
    tp=int((pred & (y==1)).sum());fp=int((pred & (y==0)).sum());fn=int(((~pred)&(y==1)).sum());tn=int(((~pred)&(y==0)).sum())
    return dict(tp=tp,fp=fp,fn=fn,tn=tn,f1=2*tp/max(1,2*tp+fp+fn),precisao=tp/max(1,tp+fp),revocacao=tp/max(1,tp+fn),fpr=fp/max(1,fp+tn),fnr=fn/max(1,fn+tp),acuracia=(tp+tn)/len(y))
def best_f1(y,s):
    y=np.asarray(y);s=np.asarray(s);order=np.argsort(-s);ys=y[order];ss=s[order]
    tp=np.cumsum(ys==1);fp=np.cumsum(ys==0);f=2*tp/np.maximum(1,tp+fp+y.sum())
    valid=np.r_[ss[:-1]!=ss[1:],True];f=np.where(valid,f,-1)
    k=int(np.argmax(f));return float(np.nextafter(ss[k],-np.inf)),float(f[k])
def fpr_threshold(y,s):
    negative=np.sort(np.asarray(s)[np.asarray(y)==0])[::-1]
    return float(negative[min(int(np.floor(.005*len(negative))),len(negative)-1)])
def verify_alignment(log,data):
    if len(log)!=len(data):raise ValueError(f'Cobertura {len(log)} != {len(data)}')
    mapped={}
    for row in log:
        pos=row['pos']
        if not isinstance(pos,int) or pos<0 or pos>=len(data) or pos in mapped:raise ValueError('Posição inválida/duplicada')
        ref=data[pos]
        for key in ('idx','project','commit_id','target'):
            if row.get(key)!=ref.get(key):raise ValueError(f'Identidade divergente: pos={pos}, {key}')
        mapped[pos]=row
    if set(mapped)!=set(range(len(data))):raise ValueError('Posições ausentes')
    return [mapped[i] for i in range(len(data))]
def official_pairs(data,allow_official_repeated_corrected=False):
    if len(data)%2:raise ValueError('Número ímpar de funções')
    ids={};pairs=[]
    for i in range(0,len(data),2):
        x,y=data[i:i+2]
        if {x['target'],y['target']}!={0,1} or x['project']!=y['project'] or x['commit_id']!=y['commit_id']:raise ValueError('Par incompatível com release: '+str(i))
        for row in (x,y):
            if row['idx'] in ids:
                old=ids[row['idx']]
                if not allow_official_repeated_corrected or row['target']!=0 or any(old[k]!=row[k] for k in ('target','project','commit_id','func')):
                    raise ValueError('Identidade reutilizada sem correspondência documental')
            ids[row['idx']]=row
        pairs.append((i,i+1) if x['target']==1 else (i+1,i))
    return np.asarray(pairs)
def paired(scores,pairs,t,mask=None):
    a=np.asarray(scores)[pairs[:,0]];b=np.asarray(scores)[pairs[:,1]]
    if mask is not None:a=a[mask];b=b[mask]
    if len(a)==0:raise ValueError('Nenhum par')
    pc=int(((a>t)&(b<=t)).sum());pv=int(((a>t)&(b>t)).sum());pb=int(((a<=t)&(b<=t)).sum());pr=int(((a<=t)&(b>t)).sum())
    strict=int((a>b).sum());ties=int((a==b).sum())
    return dict(n_pares=len(a),P_C=pc,P_V=pv,P_B=pb,P_R=pr,ordenados=strict,empatados=ties,ordenacao=(strict+.5*ties)/len(a),P_C_pct=pc/len(a)*100)
