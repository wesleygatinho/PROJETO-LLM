"""Remove somente uma introdução externa ao JSON; preserva o retorno bruto do Claude."""
import json,hashlib,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
p=HERE/sys.argv[1]
raw=(p/'resposta_bruta.json').read_bytes();envelope=json.loads(raw)
assert envelope['is_error'] is False and 'claude-opus-5-5' in envelope['modelUsage']
response=envelope['result']
start=response.index('{');prefix=response[:start].strip()
assert prefix=='Sigo as instruções do contrato e já fiz as leituras necessárias. Agora vou montar o texto corrigido e as respostas aos onze apontamentos.',prefix
payload,end=json.JSONDecoder().raw_decode(response[start:])
assert response[start+end:].strip()==''
assert isinstance(payload,dict) and payload['versao_base']==1 and len(payload['respostas'])==11
(p/'retorno.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(p/'entrada_controlador.json').write_text(json.dumps({**envelope,'result':json.dumps(payload,ensure_ascii=False)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(p/'normalizacao_formato.json').write_text(json.dumps({'origem_bruta_sha256':hashlib.sha256(raw).hexdigest(),'prefixo_fora_json_removido':prefix,'alteracao':'Somente supressão do prefácio externo para atender ao parser JSON do controlador. Todos os campos e todo o texto são os devolvidos pelo Claude, sem correção de prosa por Codex.','session_id':envelope['session_id'],'modelos_reais':list(envelope['modelUsage']),'custo_estimado_usd':envelope['total_cost_usd']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'normalizacao':'prefácio fora do JSON removido','respostas':len(payload['respostas']),'session_id':envelope['session_id'],'custo':envelope['total_cost_usd']},ensure_ascii=False))
