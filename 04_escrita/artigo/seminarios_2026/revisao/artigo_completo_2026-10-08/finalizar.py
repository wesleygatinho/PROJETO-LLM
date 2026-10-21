"""Integra explicitamente a versão aprovada, depois de conferir o parecer primário."""
import json, sys, shutil, re, subprocess, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
ARTICLE=HERE.parents[1]
FLOW=ARTICLE/'revisao/fluxo_editorial'
sys.path.insert(0,str(FLOW))
import gerenciar as flow
directory,manifest=flow.load('artigo_completo_02')
version=flow.current(manifest)
assert version['estado']=='apto_integrar',version['estado']
primary=json.loads((HERE/'conferencia_primaria/parecer.json').read_text(encoding='utf-8'))
assert primary['decisao']=='corrigir' and [p['id'] for p in primary['itens']]==['P1'],primary
assert flow.latest_review(directory,version)['decisao']=='aprovar'
assert 'a atualização é representada por ΔW = BA' in flow.read_artifact(directory,version['texto']).decode('utf-8')
assert len(primary['pares'])==5 and all(p['decisao']=='sustentado' for p in primary['pares']),primary['pares']
verification=json.loads((HERE/'verificacao_integracao.json').read_text(encoding='utf-8'))
assert verification['sha256']==version['texto']['sha256']
target=flow.integrate('artigo_completo_02',HERE/'verificacao_integracao.json')
md=Path(target).read_bytes()
canonical=ARTICLE/'texto/artigo_completo.md'
assert not canonical.exists(),'Não sobrescrever manuscrito existente sem nova revisão.'
canonical.write_bytes(md)
sections=ARTICLE/'texto/secoes/artigo_completo'
sections.mkdir(exist_ok=True)
content=md.decode('utf-8')
chunks=re.split(r'(?m)(?=^## )',content)
names=['00_identificacao','00_resumo','00_abstract','01_introducao','02_fundamentacao_trabalhos_relacionados','03_metodo','04_resultados','05_discussao','06_ameacas_validade','07_conclusao','08_referencias']
assert len(chunks)==len(names)
for chunk,name in zip(chunks,names):(sections/(name+'.md')).write_text(chunk.strip()+'\n',encoding='utf-8')
tables=ARTICLE/'tabelas';tables.mkdir(exist_ok=True)
derived=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08/tabelas'
mapping=[('T1_configuracoes.md','01_configuracoes.md'),('T2_prompting.md','02_prompting.md'),('T3_global.md','03_global.md'),('T4_pareado.md','04_pareado.md'),('T6_incerteza.md','05_incerteza.md'),('T5_recursos.md','06_recursos.md'),('T7_sensibilidade_correspondencia.md','S1_sensibilidade_correspondencia.md')]
for i,(src,dest) in enumerate(mapping,1):
    tab=(derived/src).read_text(encoding='utf-8')
    tab=re.sub(r'^Tabela \d+\.',f'Tabela {i}.' if i<7 else 'Tabela suplementar S1.',tab)
    (tables/dest).write_text(tab,encoding='utf-8')
subprocess.run([sys.executable,str(HERE/'exportar_latex.py'),str(canonical)],check=True,cwd=ROOT)
calls=[]
old_directory=FLOW/'rodadas/artigo_completo_01'
for path in [old_directory/'consultas/001_revisar.json',old_directory/'consultas/003_revisar.json',HERE/'conferencia_primaria/resposta_bruta.json',directory/'consultas/001_revisar.json']:
    envelope=json.loads(path.read_text(encoding='utf-8'))
    assert 'claude-opus-5-5' in envelope.get('modelUsage',{}),envelope.get('modelUsage')
    assert not envelope.get('is_error')
    calls.append({'arquivo':path.relative_to(ROOT).as_posix(),'session_id':envelope.get('session_id'),'modelos':list(envelope.get('modelUsage',{})),'custo_estimado_usd':envelope.get('total_cost_usd'),'duration_ms':envelope.get('duration_ms')})
assert len({c['session_id'] for c in calls})==4,'Sessões precisam ser distintas.'
(HERE/'consultas_claude.json').write_text(json.dumps(calls,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
closure=f'''# Fechamento do artigo completo

## Resultado

Manuscrito completo redigido, corrigido e integrado: `texto/artigo_completo.md`. Título: **{content.splitlines()[0].lstrip('# ')}**. Inclui Resumo/Abstract, Introdução, Fundamentação e trabalhos relacionados, Método, Resultados, Discussão, Ameaças à validade, Conclusão e onze referências primárias. Seis tabelas no corpo e uma tabela suplementar; figura científica suplementar em `figuras/ordenacao_7b.png`/`.svg`.

O arquivo LaTeX já aberto foi atualizado em seu próprio caminho: `revisao/introducao_2026-10-07/previa_rascunho_sbc.tex`. Não foi criado documento LaTeX substituto nem aberta nova aba. A versão anterior está preservada neste diretório.

Versão global incorporada: v003, versão {version['numero']} da rodada artigo_completo_02; SHA-256 do Markdown: `{version['texto']['sha256']}`. A integração foi explícita pelo controlador após conferência local de 39 conjuntos de alegações/tabelas e verificação das fontes congeladas. Essa integração não publica nem submete o artigo.

## Ciclo Codex–Claude

Codex redigiu v001. Claude Opus 5.5 revisou o texto integral e apontou oito itens. Codex corrigiu em v002 e respondeu individualmente a todos. Uma sessão nova do Claude Opus 5.5 conferiu a versão integral, declarou todos os oito IDs resolvidos e aprovou nas conferências realizadas. Uma terceira sessão focalizada confrontou as seis fontes primárias de literatura e os arquivos pai/commit dos cinco pares documentados, confirmando os cinco casos e levantando P1: distinção entre atualização LoRA e peso adaptado. Codex corrigiu P1 em v003. Uma quarta sessão revisou o manuscrito integral final na rodada artigo_completo_02, que foi iniciada explicitamente para preservar a aprovação anterior sem alterar silenciosamente seu texto. Pareceres e limites reais estão preservados; não se declara revisão visual integral dos PDFs nem reprodução independente pelo Claude.

As quatro chamadas reais utilizaram Claude Opus 5.5, confirmado pelo campo modelUsage da CLI, e as quatro sessões são distintas. Metadados, duração e custos estimados estão em `consultas_claude.json`; prompts e retornos brutos foram preservados. Cada chamada teve teto US$3; estimativa da CLI não comprova faturamento avulso. Não houve envio de credenciais.

## Ajustes realizados

Corrigidos dois arredondamentos (sensibilidade máxima0,22p.p.; estabilidade bootstrap0,10p.p.), restringida ao pareado a afirmação sobre o limiar zero do piloto3Breal, ajustada a numeração das tabelas pela ordem de aparição, padronizado seed/seeds, explicitado o referente das médias7B nos resumos e removida nota interna da referência Hui. O método distingue14avaliações de33arquivos de previsão. A introdução explicita a necessidade de conferir a correspondência dos membros na release.

As análises mantêm separados global/pareado, ordenação/categorias, limiarF1/restriçãoFPR e intervalo condicional/dispersão de seeds. A comparação NF4comadaptador/BF16mesclada é de configurações completas, sem causalidade atribuída apenas a bits, equivalência ou diagnóstico de compreensão semântica. Os cinco casos de correspondência têm sensibilidade própria e não implicam validação dos demais559pares.

## Preservação e rastreabilidade

Os110arquivos registrados antes da consolidação permanecem byte a byte inalterados. Nenhum treinamento, inferência, recuperação de pesos ou acesso ao RunPod foi realizado. A etapa nova recuperou dados/tokenizers/fontes públicas, reconstruiu métricas em CPU, calculou bootstrap e exportou tabelas/figura. Oito testes passaram. Não foram encontradas divergências nas métricas reproduzidas à precisão histórica publicada. `auditoria_final.json`, `verificacao_integracao.json` e `SUPLEMENTO.md` documentam as condições e limites; duas alterações de scripts auxiliares após a exportação e antes do congelamento estão explicitadas, sem apagar sua cronologia.

## Pendências para entrega formal

O conteúdo completo está revisado no escopo descrito, mas **o artefato não está pronto para submissão**. Faltam nomes/autoria, afiliação completa, confirmação do título pelo pesquisador, limite de páginas e regras específicas da disciplina. A fonte usa identificação explicitamente pendente, sem inventar nomes ou contato.

O compilador interno falhou duas vezes na preparação do ambiente Windows: `helper_unknown_error: setup refresh had errors`. Não apresentou erros de linha da fonte. Portanto, compilação, diagramação integral, limite de dez linhas de Resumo/Abstract, legibilidade das tabelas no PDF e número de páginas não foram validados. `DIAGNOSTICO_LATEX.md` preserva os retornos. Não foi produzido PDF por ferramenta externa.

A aprovação dos agentes não substitui a responsabilidade acadêmica do pesquisador ou aceite docente. As limitações exploratórias e de generalização são explícitas no artigo, não pendências que justifiquem fabricar resultados ou executar novos treinos.
'''
(HERE/'FECHAMENTO.md').write_text(closure,encoding='utf-8')
readme=ARTICLE/'README.md'
shutil.copyfile(readme,HERE/'README_projeto_antes.md')
readme.write_text('''# Artigo de Seminários — PPGCC UFMA — 11/11/2026

**Estado em 08/10/2026: manuscrito completo consolidado, revisado e integrado.** Codex redigiu/corrigiu; Claude Opus5.5 realizou revisões integrais e conferência focalizada de fontes primárias em quatro sessões distintas. O texto continua condicionado aos registros e ao recorte exploratório descritos.

- [Artigo completo](texto/artigo_completo.md).
- [Fonte SBC no documento já aberto](revisao/introducao_2026-10-07/previa_rascunho_sbc.tex).
- [Referências utilizadas](referencias/artigo.bib).
- [Fechamento, ajustes e pendências](revisao/artigo_completo_2026-10-08/FECHAMENTO.md).
- [Suplemento e rastreabilidade](revisao/artigo_completo_2026-10-08/SUPLEMENTO.md).
- [Primeiro ciclo de versões, correções e pareceres](revisao/fluxo_editorial/rodadas/artigo_completo_01/manifesto.json).
- [Conferência integral final após P1](revisao/fluxo_editorial/rodadas/artigo_completo_02/manifesto.json).
- [Conferência primária complementar](revisao/artigo_completo_2026-10-08/conferencia_primaria/parecer.json).
- [Diagnóstico do compilador](revisao/artigo_completo_2026-10-08/DIAGNOSTICO_LATEX.md).

**Pendências para entrega:** autoria/afiliação completa, título definitivo e regras de extensão; compilação e diagramação não validadas, pois o compilador interno falhou ao preparar o ambiente Windows. O artigo não é apresentado como PDF pronto para submissão.

Os experimentos históricos foram preservados e nenhum treino, inferência ou uso do RunPod foi realizado. Os resultados derivados ficam em `03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08`. A implementação CPU nova e seus limites estão documentados em `03_experimentos/codigo/consolidacao_artigo/IMPLEMENTACAO_2026-10-08.md`.

As seis tabelas editoriais e a sensibilidade suplementar estão em `tabelas/`; a figura complementar em `figuras/`. `texto/secoes/artigo_completo/` contém as seções extraídas da versão integrada. A introdução aprovada em07/10 e seus pareceres permanecem como versões históricas, sem sobrescrita.

- [Plano de escrita](PLANO_ESCRITA.md).
- [Matriz histórica de evidências](MATRIZ_EVIDENCIAS.md).
- [Padrão de escrita](PADRAO_ESCRITA.md).
- [Template SBC e proveniência](template_sbc/README.md).
- [Mecanismo editorial](revisao/fluxo_editorial/README.md).
- [Plano técnico](../../../01_planejamento/artigo_seminarios_2026/PLANO_EXECUCAO.md).
- [Cronograma histórico](../../../01_planejamento/artigo_seminarios_2026/CRONOGRAMA_CHECKLIST.md).

Planos e matrizes anteriores representam seu estado datado; o fechamento de08/10 documenta as análises agora executadas. A pasta `entrega/` não contém PDF final validado. Apresentação e submissão não foram realizadas por esta tarefa.
''',encoding='utf-8')
print(json.dumps({'manuscrito':str(canonical),'sha256':hashlib.sha256(md).hexdigest(),'fechamento':str(HERE/'FECHAMENTO.md'),'consultas':calls},ensure_ascii=False,indent=2))
