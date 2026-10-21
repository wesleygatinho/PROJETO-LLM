"""Importa retornos reais do Claude no controlador existente, sem redigir prosa."""
import json,sys,importlib.util,hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]; ARTICLE=ROOT/'04_escrita/artigo/seminarios_2026'
spec=importlib.util.spec_from_file_location('flow',ARTICLE/'revisao/fluxo_editorial/gerenciar.py')
flow=importlib.util.module_from_spec(spec);spec.loader.exec_module(flow)
NAME='artigo_opus_extra_01'
SEPARATOR='<!-- INICIO_SUPLEMENTO -->'
def setup():
    primary=list((ROOT/'02_referencias/verificacao_introducao_seminarios_2026').glob('*_pdf.txt'))
    more=list((ROOT/'02_referencias/verificacao_reescrita_opus_2026-10-08').glob('*.txt'))
    more += list((ROOT/'02_referencias/verificacao_reescrita_opus_2026-10-08').glob('*.json'))
    more += [ROOT/'02_referencias/verificacao_reescrita_opus_2026-10-08/LEITURA_ADICIONAIS.md']
    results=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08'
    frozen=[p for p in results.iterdir() if p.suffix in ['.md','.json','.csv']]
    frozen+=list((ROOT/'03_experimentos/codigo/consolidacao_artigo').glob('*.py'))
    frozen+=[ROOT/('03_experimentos/codigo/'+n) for n in ['03_inferencia_etapa1.py','06_treinar_qlora.py','07_avaliar_classificador.py','08_baseline_tamanho.py','classificador.py']]
    corpus=[ROOT/f'02_referencias/padrao_escrita_anselmo_2026/textos_extraidos/{k}.txt' for k in ['A01','A06','A08']]
    sources=primary+more+frozen+corpus+[HERE/'01_analise/retorno.json',HERE/'catalogo_verificado.json',HERE/'bibliografia_verificada.bib',HERE/'antes/artigo_completo.md',HERE/'antes/documento_aberto.tex',HERE/'antes/artigo.bib',ARTICLE/'revisao/artigo_completo_2026-10-08/SUPLEMENTO.md',ARTICLE/'template_sbc/sbc.bst',ARTICLE/'template_sbc/sbc-template.sty']
    briefing=HERE/'02_orientacao_reescrita.txt'
    directory=flow.start(NAME,briefing,'artigo',[str(p) for p in sources])
    print(json.dumps({'rodada':str(directory),'fontes':len(sources)},ensure_ascii=False))
def redaction():
    p=HERE/'02_reescrita';r=json.loads((p/'retorno.json').read_text(encoding='utf-8'))
    raw=json.loads((p/'resposta_bruta.json').read_text(encoding='utf-8'))
    pending=r['pendencias_cientificas']
    assert len(pending)==1 and pending[0].startswith('Não impede finalizar: a orientação dizia que a época foi escolhida por F1'),pending
    selection=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08/selecao_epocas.json'
    entries=json.loads(selection.read_text(encoding='utf-8'))
    data=list({x['rodada']:x for x in entries}.values())
    assert [x['historica_estrita'] for x in data]==[1,1,3,3,2,3]
    assert all(x['mesma'] is True for x in data[2:])
    assert all(x['ajustada_reconstruida'] is None for x in data[:2])
    note={'verificador':'Codex, orientação e conferência de fontes','observacao_original_claude':pending,'fonte':selection.relative_to(ROOT).as_posix(),'sha256_fonte':hashlib.sha256(selection.read_bytes()).hexdigest(),'verificacao':'As épocas históricas são 1,1,3,3,2,3; critério histórico de ordenação estrita com AUC para desempate. Nos quatro treinos de controle de tamanho, a seleção reconstruída com meio crédito é igual à histórica; nos dois outros não há empates por época. O manuscrito Claude segue os registros e não a orientação equivocada que confundia época com limiar F1. A pendência de conferência foi resolvida sem editar nenhuma frase. Submeter ainda à revisão independente.'}
    (p/'conferencia_selecao_epocas.json').write_text(json.dumps(note,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    text=r['texto'].rstrip()+'\n\n'+SEPARATOR+'\n\n'+r['suplemento'].strip()+'\n'
    payload={**r,'texto':text,'autor':r['autor_redacao'],'pendencias':[],'conferencia_pendencia':note}
    normalized={**raw,'result':json.dumps(payload,ensure_ascii=False)}
    dest=p/'entrada_controlador.json'
    assert not dest.exists();dest.write_text(json.dumps(normalized,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (p/'normalizacao.json').write_text(json.dumps({'alteracao':'Mapeamento de campos autor_redacao/pendencias_cientificas para autor/pendencias e concatenação determinística artigo+suplemento. Nenhuma frase reescrita.','sha256_texto_artigo':hashlib.sha256(r['texto'].encode()).hexdigest(),'sha256_texto_integral_registrado':hashlib.sha256(text.encode()).hexdigest(),'modelo':list(raw['modelUsage']),'session_id':raw['session_id']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    flow.import_draft(NAME,dest)
    print(str(flow.request(NAME,'revisar')))
if __name__=='__main__':
    if sys.argv[1]=='iniciar':setup()
    elif sys.argv[1]=='redacao':redaction()
    elif sys.argv[1]=='parecer':flow.review(NAME,HERE/sys.argv[2]/'resposta_bruta.json');print(flow.status(NAME))
    elif sys.argv[1]=='correcao':
        path=HERE/sys.argv[2];entry=path/'entrada_controlador.json'
        flow.correction(NAME,entry if entry.exists() else path/'resposta_bruta.json');print(flow.status(NAME))
    elif sys.argv[1]=='pedido':print(str(flow.request(NAME,sys.argv[2])))
