import json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
old=(HERE/'bibliografia_candidata.bib').read_text(encoding='utf-8')
extra='''
@misc{ullah2024sec,
  author = {Ullah, Saad and Han, Mingji and Pujar, Saurabh and Pearce, Hammond and Coskun, Ayse and Stringhini, Gianluca},
  title = {LLMs Cannot Reliably Identify and Reason About Security Vulnerabilities (Yet?): A Comprehensive Evaluation, Framework, and Benchmarks},
  year = {2024},
  howpublished = {arXiv:2312.12575v3},
  doi = {10.48550/arXiv.2312.12575},
  note = {Versão 3, 24 de julho de 2024, conferida visualmente no PDF local}
}
@article{saito2015metrics,
  author = {Saito, Takaya and Rehmsmeier, Marc},
  title = {The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets},
  journal = {PLOS ONE},
  volume = {10},
  number = {3},
  pages = {e0118432},
  year = {2015},
  doi = {10.1371/journal.pone.0118432}
}
@article{field2007bootstrap,
  author = {Field, C. A. and Welsh, A. H.},
  title = {Bootstrapping clustered data},
  journal = {Journal of the Royal Statistical Society: Series B (Statistical Methodology)},
  volume = {69},
  number = {3},
  pages = {369--390},
  year = {2007},
  doi = {10.1111/j.1467-9868.2007.00593.x}
}
'''
new=re.sub(r'^\s*url\s*=.*\n','',old,flags=re.M)+extra
(HERE/'bibliografia_verificada.bib').write_text(new,encoding='utf-8')
catalog={}
for match in re.finditer(r'@(\w+)\{([^,]+),\s*(.*?)(?=\n@|\Z)',new,re.S):
    kind,key,raw=match.groups()
    fields={m[1]:m[2].replace(r'{\"o}','ö').replace(r'\#','#').replace('{','').replace('}','') for m in re.finditer(r'^\s*(\w+)\s*=\s*\{(.*?)\}\s*,?\s*$',raw,re.M)}
    authors=fields['author'].split(' and ');names=[a.split(',',1)[0] for a in authors]
    short=names[0]+(' et al.' if len(names)>2 else ' e '+names[1] if len(names)==2 else '')
    abbreviated=[]
    for author in authors:
        surname,given=author.split(',',1)
        initials=' '.join(part[0]+'.' for part in given.strip().split())
        abbreviated.append(surname+', '+initials)
    full='; '.join(abbreviated)+' ('+fields['year']+'). '+fields['title'].rstrip('.')+'. '
    if kind in ['inproceedings','article']:
        full+=fields['booktitle'] if kind=='inproceedings' else fields['journal']
        if 'volume' in fields:full+=', '+fields['volume']
        if 'number' in fields:full+='('+fields['number']+')'
        if 'pages' in fields:full+=', '+fields['pages'].replace('--','–')
        full+='. '
    else:full+=fields['howpublished']+'. '
    if 'doi' in fields:full+='DOI: '+fields['doi']+'.'
    catalog[key]={'tipo':kind,**fields,'autores_citacao':short,'referencia':full.strip()}
(HERE/'catalogo_verificado.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'referencias_candidatas_verificadas':len(catalog),'chaves':list(catalog)},ensure_ascii=False))
