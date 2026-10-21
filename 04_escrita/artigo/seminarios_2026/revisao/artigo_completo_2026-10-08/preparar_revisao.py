from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[5];BASE=ROOT/'04_escrita/artigo/seminarios_2026';OUT=Path(__file__).resolve().parent
FLOW=BASE/'revisao/fluxo_editorial';sys.path.insert(0,str(FLOW));import gerenciar as flow
DER=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08'
spec=[('libjpeg','libjpeg','2022'),('php-src','PHP','2011'),('rizin','rizin','2022'),('linux-2.6','Linux','2008'),('drogon','drogon','2022')]
metadata=json.loads((ROOT/'03_experimentos/dados/artigo_seminarios_2026/commits_inspecao/proveniencia.json').read_text())['fontes']
bib=(BASE/'referencias/introducao.bib').read_text(encoding='utf-8');refs=[]
for key,label,year in spec:
    source=next(r for r in metadata if r['projeto']==key)
    info=json.loads((ROOT/f'03_experimentos/dados/artigo_seminarios_2026/commits_inspecao/{key}.json').read_text())
    title=info['commit']['message'].splitlines()[0];assert info['commit']['author']['date'].startswith(year)
    url='https://github.com/'+source['repo']+'/commit/'+source['commit']
    safe_title=title.replace('#',r'\#')
    bib+=f'\n@misc{{commit_{key.replace("-","_")},\n  author = {{{{{label}}}}},\n  title = {{{safe_title}}},\n  year = {{{year}}},\n  howpublished = {{Commit {source["commit"]}}},\n  url = {{{url}}},\n  note = {{Arquivos do commit e do pai conferidos em 8 de outubro de 2026}}\n}}\n'
    refs.append(f'{label} ({year}). {title}. Commit `{source["commit"]}`. [Fonte primária]({url}).')
(BASE/'referencias/artigo.bib').write_text(bib,encoding='utf-8')
text=(OUT/'v001_artigo_codex.md').read_text(encoding='utf-8')
text=text.replace('libjpeg, PHP, rizin, Linux e drogon.','libjpeg (2022), PHP (2011), rizin (2022), Linux (2008) e drogon (2022).')
old='Fontes primárias adicionais da auditoria de correspondência: commits e arquivos dos projetos libjpeg, PHP, rizin, Linux e drogon, identificados por SHA completo e URL no suplemento auditável e em referencias/artigo.bib. Não são usados para generalizar a qualidade de todo o dataset.'
text=text.replace(old,'\n\n'.join(refs))
version=OUT/'v001_submissao.md';version.write_text(text,encoding='utf-8')
briefing='''# Revisão do artigo completo — 08/10/2026

O pesquisador pediu finalizar o artigo inteiro junto com o Claude, em uma execução contínua. Escopo científico/editorial do texto integral: objetivo, fontes, método, resultados, estatística, comparabilidade, discussão, limitações, conclusão, resumos e referências. Codex redige/corrige; Claude Opus 5.5 revisa; nova sessão confere os IDs. Não editar fontes, não executar comandos, não treinar/inferir, não usar RunPod, MCPs ou agentes. Use somente fontes listadas; nenhuma credencial faz parte do pacote. Responda pelo contrato do controlador.

## Evidência concluída

A release original oficial foi recuperada. Hashes completos atuais coincidem com prefixos históricos disponíveis de treino/teste/pareado; validação não tinha hash registrado. Todas as 14 avaliações incluídas possuem junção por pos/idx/project/commit/target sem divergências e cobertura integral. Baseline foi recontado em CPU; tokenizers 0.23.2 e tokenizer recuperado do 3B. Os tokenizers das revisões 3B/7B recuperadas são idênticos, e os comprimentos correspondem aos logs. Métricas principais reproduzem os CSVs na precisão publicada; não se recupera precisão interna ausente. Não se fez nova inferência/treino ou medição de GPU.

Release oficial reutiliza duas identidades corrigidas no teste e uma em cinco pares dev; isso é registrado, sem fallback/exclusão silenciosa. Quinze pares apresentam cabeçalhos diferentes. Diferença de nome não prova erro: inspeção dos diffs e dos cinco commits suspeitos confirmou que, nesses cinco, a função dita corrigida já existia no pai e é diferente da realmente alterada pelo patch. Fontes públicas antes/depois e normalização só de espaço comprovam as ocorrências (inspecao_correspondencia_commits.json). Os 564 oficiais são referência descritiva; sensibilidade sem cinco mantém 559, cruzada sem truncamento 460. Não se substituem membros sem previsões nem se certificam os demais pares. Avalie a força da alegação e a adequação do tratamento; concordância de agentes não substitui ciência.

Bootstrap primário por 550 grupos project/commit, 10.000 réplicas, vetores de três seeds e variantes alinhados. Sensibilidade por par. Intervalos condicionais aos modelos; dispersão de seeds é separada. Sem p-valores, sem McNemar opcional. Janela de pico alocado após carga/merge abrange dev/teste/pareado. Tempos do teste são amortizados em lotes, não latência. Comparação NF4/BF16 inclui merge e representação. Limiares maior F1/dev e FPR/dev são diferentes.

## Exigências da revisão

Confira os números em tabelas/estatística e reconstrução; não presuma aceites apenas pela execução dos scripts. Verifique em especial atribuição causal, equivalência, leitura de chance 50%, validade dos pares e unidade do bootstrap. Os seis PDFs primários foram lidos focalizadamente pelo Codex; você pode ler as extrações determinísticas listadas. Declare ausência de leitura visual/diagramação e quais fontes efetivamente conferiu. Não imponha novas inferências/GPU para remover afirmações que excedam evidência. Trate protocolo próprio VD-S como distinto do oficial. Verifique referências e limitações completas; não invente apontamentos para exercitar o fluxo.

A identificação de autores/afiliação completa e o limite de páginas foram perguntados ao pesquisador, ainda sem resposta; são pendências externas de entrega, não alegações empíricas a inventar. Texto completo não equivale a arquivo pronto para submissão. Compilador nativo falhou anteriormente por ambiente; este pacote revisa o texto e a ciência, sem prometer PDF verificado. Não aprovar diagramação ou regras de páginas não informadas.
'''
bp=OUT/'briefing.md';bp.write_text(briefing,encoding='utf-8')
paths=[BASE/'referencias/artigo.bib',BASE/'referencias/MATRIZ_INTRODUCAO.md',ROOT/'01_planejamento/artigo_seminarios_2026/PLANO_EXECUCAO.md']
paths += [DER/n for n in ('manifesto.json','auditoria_integridade.json','metricas_por_execucao.csv','metricas_pareadas.csv','selecao_epocas.json','sensibilidade_truncamento.csv','estatistica.json','inspecao_correspondencia_commits.json','pares_inspecao.json','tokenizacao_proveniencia.json','divergencias.json','tabelas_artigo.md','proveniencia_exports.json')]
paths += list((ROOT/'03_experimentos/codigo/consolidacao_artigo').glob('*.py'))
paths += [ROOT/'03_experimentos/codigo'/n for n in ('classificador.py','03_inferencia_etapa1.py','06_treinar_qlora.py','07_avaliar_classificador.py','08_baseline_tamanho.py')]
paths += [ROOT/'02_referencias/verificacao_introducao_seminarios_2026'/n for n in ('primevul_pdf.txt','risse_pdf.txt','huang_pdf.txt','qwen_pdf.txt','lora_pdf.txt','qlora_pdf.txt','LEITURA_FONTES.md')]
paths += [ROOT/'03_experimentos/dados/artigo_seminarios_2026/fontes_publicas'/n for n in ('calc_vd_score_oficial.py','primevul_readme_oficial.md')]
paths += [ROOT/'03_experimentos/dados/artigo_seminarios_2026/commits_inspecao'/n for n in ('drogon_pai.cc','drogon_commit.cc','libjpeg_pai.cpp','libjpeg_commit.cpp','php-src_pai.c','php-src_commit.c','rizin_pai.c','rizin_commit.c','linux-2.6_pai.c','linux-2.6_commit.c')]
name='artigo_completo_01'
flow.start(name,str(bp.relative_to(ROOT)),'artigo',[str(p.relative_to(ROOT)) for p in paths])
flow.draft(name,str(version.relative_to(ROOT)),'Codex — redator do manuscrito completo')
print('Rodada registrada:',name,'fontes específicas:',len(paths))
