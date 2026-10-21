"""Preserva a versão rejeitada e organiza metadados de fontes primárias; não redige o artigo."""
import json,hashlib,re,shutil,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
ARTICLE=ROOT/'04_escrita/artigo/seminarios_2026'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=HERE/'antes'
before.mkdir(exist_ok=True)
initial={}
for rel,name in [('texto/artigo_completo.md','artigo_completo.md'),('revisao/introducao_2026-10-07/previa_rascunho_sbc.tex','documento_aberto.tex'),('referencias/artigo.bib','artigo.bib')]:
    p=ARTICLE/rel;dest=before/name
    assert not dest.exists(),'Preservação já realizada'
    shutil.copyfile(p,dest);initial[str(p.relative_to(ROOT))]=sha(p)
frozen={}
for folder in ['03_experimentos/codigo','03_experimentos/logs','03_experimentos/resultados']:
    for p in (ROOT/folder).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:frozen[str(p.relative_to(ROOT))]=sha(p)
(HERE/'preservacao.json').write_text(json.dumps({'versao_anterior':initial,'fontes_experimentais_congeladas':frozen},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=(before/'artigo.bib').read_text(encoding='utf-8')
papers=old.split('@misc{commit_',1)[0].strip()
addition=r'''
@inproceedings{chen2023diversevul,
  author = {Chen, Yizheng and Ding, Zhoujie and Alowain, Lamya and Chen, Xinyun and Wagner, David},
  title = {DiverseVul: A New Vulnerable Source Code Dataset for Deep Learning Based Vulnerability Detection},
  booktitle = {26th International Symposium on Research in Attacks, Intrusions and Defenses (RAID 2023)},
  year = {2023},
  doi = {10.1145/3607199.3607242},
  note = {PDF primário local, arXiv:2304.00409v2, 9 de agosto de 2023}
}
@inproceedings{fu2022linevul,
  author = {Fu, Michael and Tantithamthavorn, Chakkrit},
  title = {LineVul: A Transformer-based Line-Level Vulnerability Prediction},
  booktitle = {19th International Conference on Mining Software Repositories (MSR 2022)},
  year = {2022},
  pages = {608--620},
  doi = {10.1145/3524842.3528452}
}
@misc{chakraborty2020reveal,
  author = {Chakraborty, Saikat and Krishna, Rahul and Ding, Yangruibo and Ray, Baishakhi},
  title = {Deep Learning based Vulnerability Detection: Are We There Yet?},
  year = {2020},
  howpublished = {arXiv:2009.07235},
  doi = {10.48550/arXiv.2009.07235},
  note = {Preprint de 2020 correspondente à fonte lida; não identificado como edição TSE de 2022}
}
@inproceedings{zhou2019devign,
  author = {Zhou, Yaqin and Liu, Shangqing and Siow, Jingkai and Du, Xiaoning and Liu, Yang},
  title = {Devign: Effective Vulnerability Identification by Learning Comprehensive Program Semantics via Graph Neural Networks},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {32},
  year = {2019},
  note = {Metadados conferidos no registro primário NeurIPS 2019; texto local em versão preprint}
}
'''
new=papers+'\n'+addition
(HERE/'bibliografia_candidata.bib').write_text(new,encoding='utf-8')
def untex(s):
    return s.replace(r'{\"o}','ö').replace(r'\#','#').replace('{','').replace('}','')
catalog={}
for match in re.finditer(r'@(\w+)\{([^,]+),\s*(.*?)(?=\n@|\Z)',new,re.S):
    kind,key,raw=match.groups()
    fields={m[1]:untex(m[2]) for m in re.finditer(r'^\s*(\w+)\s*=\s*\{(.*?)\}\s*,?\s*$',raw,re.M)}
    authors=fields['author'].split(' and ')
    names=[a.split(',',1)[0] for a in authors]
    short=names[0]+(' et al.' if len(names)>2 else ' e '+names[1] if len(names)==2 else '')
    full='; '.join(a for a in authors)+' ('+fields['year']+'). '+fields['title']+'. '
    if kind=='inproceedings':
        full+=fields['booktitle']+'. '
        if 'volume' in fields:full+='v. '+fields['volume']+'. '
        if 'pages' in fields:full+='p. '+fields['pages'].replace('--','–')+'. '
    else:full+=fields['howpublished']+'. '
    if 'doi' in fields:full+='DOI: '+fields['doi']+'.'
    catalog[key]={'tipo':kind,**fields,'autores_citacao':short,'referencia':full.strip()}
(HERE/'catalogo_referencias.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'fontes_congeladas':len(frozen),'catalogo':list(catalog)},ensure_ascii=False))
