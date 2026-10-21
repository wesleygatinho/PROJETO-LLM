"""Conferência de células e preservação; nenhum recálculo de modelos/métricas."""
import json,re,hashlib,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
def tables(md):
    groups=[];rows=[]
    for line in md.splitlines()+['']:
        if line.strip().startswith('|'):
            row=[x.strip() for x in line.strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',x) for x in row):rows.append(row)
        elif rows:groups.append(rows);rows=[]
    return groups
def normalize(label):
    replacements=[('Heurística de comprimento','Tamanho'),('3B proporção original','3B real'),('3B 1:1 + tamanho','3B 1:1 tamanho'),('7B 1:1 + tamanho, semente ','7B 1:1 tamanho s'),('3B Instruct','Prompt 3B'),('7B Instruct','Prompt 7B')]
    for old,new in replacements:label=label.replace(old,new)
    return label
def main():
    source=Path(sys.argv[1]);out=HERE/sys.argv[2]
    text=source.read_text(encoding='utf-8');main,supp=text.split('<!-- INICIO_SUPLEMENTO -->',1)
    current=tables(main)
    frozenpath=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08/tabelas_artigo.md'
    frozen=tables(frozenpath.read_text(encoding='utf-8'))
    assert len(current)==7 and len(frozen)==7,(len(current),len(frozen))
    reports=[]
    for ci,fi in [(1,0),(2,1),(3,2),(4,3),(5,5),(6,4)]:
        new=current[ci][1:];old=frozen[fi][1:]
        if fi==0:old=[row[:-1] for row in old]
        assert len(new)==len(old)
        for n,o in zip(new,old):assert [normalize(n[0])]+n[1:]==o,(ci,n,o)
        reports.append({'tabela_artigo':ci+1,'tabela_congelada':fi+1,'celulas_conferidas':sum(len(r) for r in old),'diferencas':[]})
    assert current[0][1:]==[['Treino','184.427','5.574','4.354'],['Validação','25.430','699','562'],['Teste','25.911','695','564']]
    frozenhashes=json.loads((HERE/'preservacao.json').read_text(encoding='utf-8'))['fontes_experimentais_congeladas']
    changed=[name for name,digest in frozenhashes.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
    assert changed==[],changed
    report={'versao_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'arquivo':str(source.resolve()),'fontes_experimentais_preservadas':len(frozenhashes),'alteracoes_experimentais':changed,'tabelas':reports,'dados_tabela1':'Conferência das contagens registradas da release original','numero_tokens_citacao':len(re.findall(r'\[[@!][^\]]+\]',main)),'validacao':'Conferência de cópia, sem produzir novos resultados, testes estatísticos ou avaliações. Não valida a prosa por contagem de referências.'}
    (out/'conferencia_tabelas_preservacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
