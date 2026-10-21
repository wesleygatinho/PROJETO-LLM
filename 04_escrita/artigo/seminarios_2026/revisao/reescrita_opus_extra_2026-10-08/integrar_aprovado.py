"""Integra somente versão Claude aprovada; preserva o arquivo bibliográfico histórico congelado."""
import json,sys,hashlib,shutil,re,importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];ARTICLE=HERE.parents[1]
spec=importlib.util.spec_from_file_location('flow',ARTICLE/'revisao/fluxo_editorial/gerenciar.py')
flow=importlib.util.module_from_spec(spec);spec.loader.exec_module(flow)
NAME='artigo_opus_extra_01'
def main():
    stage=HERE/sys.argv[1]
    directory,manifest=flow.load(NAME);v=flow.current(manifest)
    review=flow.latest_review(directory,v)
    assert v['estado']=='apto_integrar' and review['decisao']=='aprovar' and review['itens']==[]
    text=flow.read_artifact(directory,v['texto']).decode('utf-8')
    audit=json.loads((stage/'conferencia_tabelas_preservacao.json').read_text(encoding='utf-8'))
    assert audit['versao_sha256']==v['texto']['sha256'] and audit['alteracoes_experimentais']==[]
    checks=[]
    for phrase,source,locator,verification in [
      ('F1', 'tabelas_artigo.md','Tabelas congeladas 1–6 e tabela suplementar','Conferência determinística de todas as células reproduzidas nas seis tabelas experimentais, com mapeamento declarado de rótulos. Nova tabela de dados confere contagens da release.'),
      ('A época', 'selecao_epocas.json','historica_estrita, ajustada_reconstruida e mesma das seis receitas únicas','Épocas históricas 1,1,3,3,2,3, com mesma seleção reconstruída nos quatro treinos de controle de tamanho. Não há reconstituição de empates por época nos outros dois; nenhuma escolha por F1 de época foi inventada.'),
      ('10.000', 'estatistica.json','parametros, seeds_7b e comparacoes','Bootstrap percentil por 550 grupos projeto/commit, 10.000 réplicas, mesmas amostras entre configurações, média de três modelos e intervalos condicionais. A dispersão das seeds não triplica o teste nem identifica equivalência.'),
      ('32 pares', 'tokenizacao_proveniencia.json','pares_tokens_identicos_2048 e pares_ambos_nao_truncados','32 entradas pareadas idênticas após o corte e 465 pares sem truncamento. Conferência adicional somente de leitura dos artefatos e funções originais: os 32 têm código original diferente e não pertencem ao subconjunto sem truncamento.'),
      ('cinco', 'inspecao_correspondencia_commits.json','cinco casos de correspondência inspecionada','Inspeção focalizada e fontes de patch confirmam cinco correspondências com outra função. Não se certificou todo o restante; a sensibilidade não altera a amostra oficial nem cria previsões ausentes.')]:
        paragraph=next(p for p in text.split('\n\n') if phrase in p)
        checks.append({'alegacao':paragraph,'fonte':'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08/'+source,'localizador':locator,'verificacao':verification})
    paragraph=next(p for p in text.split('\n\n') if 'limiar' in p and '0,5%' in p and 'calibr' in p)
    checks.append({'alegacao':paragraph,'fonte':'03_experimentos/codigo/consolidacao_artigo/comum.py','localizador':'metrics, best_f1 e fpr_threshold, linhas 35–46','verificacao':'Desigualdade estrita, limiar de maior F1 e limiar dado pelo escore negativo de posição floor(0,005*Nneg) em ordem decrescente. Não é o maior limiar matematicamente admissível nem garantia de FPR no teste. Conferir a redação aprovada, sem inferir uma otimização que o código não executa.'})
    verification={'versao':v['numero'],'sha256':v['texto']['sha256'],'verificador':'Codex — orientação, conferência de fontes, cópia de células e integração; redação/correções a cargo do Claude Opus 5.5 xhigh','pendencias':[],'escopo':'Conferências locais materiais, somadas à revisão científico/editorial integral do Claude em sessão nova. Não certifica autoria definitiva, compilação, número de páginas ou layout.','checagens':checks}
    path=HERE/'verificacao_integracao.json';assert not path.exists()
    path.write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    target=flow.integrate(NAME,path)
    shutil.copyfile(stage/'artigo_legivel.md',ARTICLE/'texto/artigo_completo.md')
    # artigo.bib é fonte congelada de rodadas históricas: manter, salvar a bibliografia atual com nome explícito.
    bib=ARTICLE/'referencias/artigo_opus_extra.bib';assert not bib.exists()
    shutil.copyfile(stage/'artigo.bib',bib)
    sections=ARTICLE/'texto/secoes/artigo_opus_extra';sections.mkdir(exist_ok=False)
    content=(stage/'artigo_legivel.md').read_text(encoding='utf-8')
    matches=list(re.finditer(r'^## (?!Referências)(.*)$',content,re.M))
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else content.index('## Referências')
        (sections/f'{i:02d}_secao.md').write_text(content[m.start():end].strip()+'\n',encoding='utf-8')
    log={'rodada':NAME,'versao_integrada':v['numero'],'sha256_integral':v['texto']['sha256'],'fonte_aprovada':str(target),'manuscrito_canonico':str(ARTICLE/'texto/artigo_completo.md'),'sha256_canonico':hashlib.sha256((ARTICLE/'texto/artigo_completo.md').read_bytes()).hexdigest(),'bibliografia_atual':str(bib),'bibliografia_anterior_preservada':str(ARTICLE/'referencias/artigo.bib'),'transposicao':json.loads((stage/'transposicao.json').read_text(encoding='utf-8')),'fontes_preservadas':audit['fontes_experimentais_preservadas'],'modificacoes_experimentais':[]}
    (HERE/'integracao.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(log,ensure_ascii=False))
if __name__=='__main__':main()
