import json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ARTICLE=HERE.parents[1]
for name in ['FECHAMENTO.md','DIAGNOSTICO_LATEX.md']:
    p=HERE/name
    text=p.read_text(encoding='utf-8')
    text=text.replace('falhou duas vezes','falhou quatro vezes')
    text=text.replace('Foram feitas duas chamadas','Foram feitas quatro chamadas')
    text=text.replace('depois de salvar a versão inicial e depois de salvar a versão corrigida. Ambas retornaram:',
                      'após salvar versões sucessivas do manuscrito e a correção da transposição dos asteriscos FNR*/FPR*. Todas retornaram:')
    text=text.replace('confirmação do título pelo pesquisador, ','')
    text=text.replace('título definitivo confirmado pelo pesquisador, ','')
    text=re.sub(r'(\d)(arquivos|avaliações|pares|seeds|grupos)',r'\1 \2',text)
    text=text.replace('pilot o','piloto')
    text=text.replace('piloto3Breal','piloto 3B real').replace('médias7B','médias 7B')
    text=text.replace('0,22p.p.','0,22 p.p.').replace('0,10p.p.','0,10 p.p.')
    text=text.replace('NF4comadaptador/BF16mesclada','NF4 com adaptador/BF16 mesclada')
    text=text.replace('global/pareado','global/pareado').replace('limiarF1/restriçãoFPR','limiar F1/restrição FPR')
    p.write_text(text,encoding='utf-8')
p=HERE/'SUPLEMENTO.md'
text=p.read_text(encoding='utf-8')
text=text.replace('com os argumentos `--raiz` e `--destino`','na mesma raiz do projeto com `--destino`')
text=text.replace('em `revisao/fluxo_editorial/rodadas/artigo_completo_01`.',
                  'em `revisao/fluxo_editorial/rodadas/artigo_completo_01` e `artigo_completo_02`. A conferência primária adicional e a resposta P1 ficam neste diretório de revisão.')
p.write_text(text,encoding='utf-8')
p=ARTICLE/'README.md'
text=p.read_text(encoding='utf-8').replace('título definitivo e regras de extensão','regras de extensão')
text=text.replace('Opus5.5','Opus 5.5').replace('em07/10','em 07/10').replace('de08/10','de 08/10')
p.write_text(text,encoding='utf-8')
export=json.loads((HERE/'exportacao_latex.json').read_text(encoding='utf-8'))
source=Path(export['documento_aberto'])
assert 'ZZPROTECTED' not in source.read_text(encoding='utf-8')
assert 'FNR* e FPR*' in source.read_text(encoding='utf-8')
meta={'documento':export['documento_aberto'],'sha256_tex':export['sha256_tex'],'tentativas_compilador_interno':4,'todas_resultado':'compile-failed; falha na preparação Windows; helper_unknown_error: setup refresh had errors','compilacao_validada':False,'pdf_inspecionado':False,'pendencias_entrega':['autoria/afiliação completa','limite de páginas/regras específicas','compilação e inspeção de diagramação/PDF']}
(HERE/'estado_entrega.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2))
