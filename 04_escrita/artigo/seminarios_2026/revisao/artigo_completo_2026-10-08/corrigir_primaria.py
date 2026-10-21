import sys,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
FLOW=ROOT/'04_escrita/artigo/seminarios_2026/revisao/fluxo_editorial'
sys.path.insert(0,str(FLOW))
import gerenciar as flow
envelope=json.loads((HERE/'conferencia_primaria/resposta_bruta.json').read_text(encoding='utf-8'))
raw=envelope['result'].strip()
assert raw.startswith('```json') and raw.endswith('```')
payload=json.loads(raw[len('```json'):].rsplit('```',1)[0].strip())
(HERE/'conferencia_primaria/parecer.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'conferencia_primaria/normalizacao.json').write_text(json.dumps({'operacao':'Remoção exclusiva da cerca Markdown externa para decodificar o JSON. Conteúdo do parecer não alterado; resposta bruta preservada.','modelos':list(envelope.get('modelUsage',{})),'is_error':envelope.get('is_error')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
directory,manifest=flow.load('artigo_completo_01')
v=flow.current(manifest)
assert v['numero']==2 and payload['manuscrito_sha256']==v['texto']['sha256']
text=flow.read_artifact(directory,v['texto']).decode('utf-8')
old='Para uma matriz pré-treinada W₀, a atualização assume a forma W₀ + BA, com posto r menor que as dimensões da matriz; os pesos originais permanecem congelados e os parâmetros adicionais são ajustados à tarefa (Hu et al., 2021).'
new='Para uma matriz pré-treinada W₀ de dimensões d × k, a atualização é representada por ΔW = BA, de modo que o peso adaptado é W₀ + BA, com posto r muito menor que o mínimo entre d e k; os pesos originais permanecem congelados e os parâmetros adicionais são ajustados à tarefa (Hu et al., 2021).'
assert old in text
text=text.replace(old,new)
(HERE/'v003_artigo_codex.md').write_text(text,encoding='utf-8')
response={'id':'P1','situacao':'corrigido','justificativa':'Distinguida a atualização ΔW=BA do peso adaptado W0+BA, com condição de baixo posto explicitada. Não alteradas receitas, números, conclusão ou referências.','evidencias':[{'fonte':'02_referencias/verificacao_introducao_seminarios_2026/lora_pdf.txt','localizador':'Página física4, linhas211–215; equação3 e definições de B∈R^(d×r), A∈R^(r×k), r≪min(d,k)','verificacao':'A fonte define W0+ΔW=W0+BA; W0 é congelado, A/B são treináveis. A versão anterior chamava indevidamente W0+BA de atualização.'}]}
(HERE/'resposta_P1.json').write_text(json.dumps(response,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
briefing=HERE/'briefing_fechamento.md'
briefing.write_text('''# Conferência integral após correção científica primária

Escopo: artigo completo de Seminários PPGCC/UFMA, mesma pergunta exploratória, mesmas análises CPU e mesmos registros históricos. O manuscrito integral passou pelo ciclo artigo_completo_01: oito itens levantados, corrigidos por Codex e resolvidos por outra sessão Claude. A auditoria focalizada seguinte confirmou diretamente os seis textos primários e as correspondências nos arquivos pai/commit dos cinco casos, mas levantou P1: confusão entre atualização LoRA e peso adaptado.

Codex corrigiu P1 no manuscrito v003: ΔW=BA é atualização; W0+BA é peso resultante. Leia o parecer primário e resposta_P1.json, confronte a formulação final diretamente em lora_pdf.txt p.física4, e confira o TEXTO INTEGRAL para regressões. O parecer primário não é prova de verdade: confronta fontes e explicita limites. Não considere aprovado antes desta chamada. Só P1 mudou de v002 para v003; os oito ajustes anteriores devem permanecer resolvidos. O controlador inicia nova rodada porque uma versão já aprovada não pode ser alterada silenciosamente.

Fontes já lidas: seis extrações primárias, publicações versionadas e referências; dados originais recuperados, logs/receitas históricas; fontes publicadas dos cinco commits e seus pais. Consolidação reproduziu métricas na precisão histórica, com scores arredondados e intervalos condicionais às três seeds. Referência oficial564pareados, sensibilidade559e460, sem certificar todos os rótulos. Preserve alcance, limites e diagnóstico de implantação NF4comadaptador/BF16mesclada não causal. Não transforme 50%em teste semântico/equivalência, nem a amostra exploratória em confirmação independente.

Autoria/afiliação completa, título definitivo confirmado pelo pesquisador, limite de páginas e regras do professor ainda não informados. Duas tentativas de compilação falharam na preparação do ambiente Windows, sem erros de linha da fonte. Nenhuma diagramação/PDF foi validada. Essas são pendências da entrega, não fundamento para inventar dados ou para aprovação de PDF. Sua revisão tem escopo científico/editorial do texto, com todas as limitações declaradas. Não execute comandos, modelos, treinamento ou RunPod, não leia credenciais.
''',encoding='utf-8')
sourcepaths=[r['arquivo'] for r in manifest['fontes']]
sourcepaths += [(HERE/'conferencia_primaria/parecer.json').relative_to(ROOT).as_posix(),(HERE/'resposta_P1.json').relative_to(ROOT).as_posix(),(directory/'pareceres/v002.json').relative_to(ROOT).as_posix(),(directory/'versoes/v002.md').relative_to(ROOT).as_posix()]
flow.start('artigo_completo_02',briefing.relative_to(ROOT),'artigo',sourcepaths)
flow.draft('artigo_completo_02',(HERE/'v003_artigo_codex.md'),'Codex — correção científica P1 após conferência primária')
print('Nova rodada artigo_completo_02 registrada com manuscrito v003 e correção P1 fundamentada.')
