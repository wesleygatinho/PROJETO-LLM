import sys, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
FLOW=ROOT/'04_escrita/artigo/seminarios_2026/revisao/fluxo_editorial'
sys.path.insert(0,str(FLOW))
import gerenciar as flow
directory, manifest=flow.load('artigo_completo_01')
version=flow.current(manifest)
review=flow.latest_review(directory,version)
assert version['numero']==1
text=flow.read_artifact(directory,version['texto']).decode('utf-8')

def change(old,new):
    global text
    assert old in text, old
    text=text.replace(old,new)

change('A maior alteração absoluta nos seis resultados 7B foi 0,23 ponto percentual.',
       'A maior alteração absoluta nos seis resultados 7B foi 0,22 ponto percentual, arredondada a duas casas.')
change('O piloto 3B real classificava todas as funções como não vulneráveis no limiar histórico zero, mas seu F1 foi 0,262 no limiar reconstruído da validação.',
       'No limiar histórico zero, as 564 decisões pareadas do piloto 3B real foram P-B. No teste global, seu F1 foi 0,262 no limiar reconstruído da validação.')
change('Tabela 6','Tabela TEMP')
change('Tabela 5','Tabela 6')
change('Tabela TEMP','Tabela 5')
change('variou no máximo 0,11 ponto percentual por modelo.',
       'variou no máximo 0,10 ponto percentual por modelo, arredondada a duas casas.')
text=text.replace('sementes','seeds')
change('As médias de ordenação pareada foram 50,62% e 49,97%, respectivamente, com variação entre seeds.',
       'No 7B, as médias de ordenação pareada das três seeds foram 50,62% em NF4 e 49,97% em BF16. A referência de tamanho apresentou AUC global de 0,810 e ordenação pareada de 21,10%.')
change('Mean paired ordering was 50.62% and 49.97%, respectively, with variation across seeds.',
       'For the 7B model, mean paired ordering across the three seeds was 50.62% (NF4) and 49.97% (BF16). The size baseline obtained a global AUC of 0.810 and paired ordering of 21.10%.')
change('Lista completa de autores na bibliografia BibTeX. ','')
change('Foram incluídas quatro avaliações Instruct, três pilotos 3B e seis avaliações de três adaptadores 7B, cada um implantado em NF4 e BF16, além da referência de tamanho.',
       'Foram incluídas quatro avaliações por prompting (3B e 7B Instruct, cada um no teste global e no pareado), três pilotos 3B e seis avaliações de três adaptadores 7B, cada um implantado em NF4 e BF16, além da referência de tamanho. Para os classificadores e a referência de tamanho, cada avaliação reúne seus respectivos splits.')
change('A junção dos 14 logs de avaliação selecionados com os splits oficiais',
       'A junção dos 33 arquivos de previsão das 14 avaliações selecionadas com os splits oficiais')
change('a avaliação de pares formados por uma função vulnerável e sua versão corrigida',
       'a avaliação de pares rotulados como uma função vulnerável e sua versão corrigida')
change('A avaliação pareada é relevante porque reúne versões de código semelhantes que diferem pela correção da vulnerabilidade e examina as decisões sobre ambas, tornando visíveis erros que uma avaliação agregada não descreve diretamente.',
       'A avaliação pareada é relevante porque pretende reunir versões de código semelhantes que diferem pela correção da vulnerabilidade e examina as decisões sobre ambas, tornando visíveis erros que uma avaliação agregada não descreve diretamente. A correspondência entre os membros requer conferência na release utilizada, como examinado neste estudo.')
head,refs=text.split('## Referências\n\n',1)
text=head+'## Referências\n\n'+'\n\n'.join(sorted(refs.strip().split('\n\n'),key=str.casefold))+'\n'

DER='03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08/'
def evidence(file,loc,check):return {'fonte':DER+file,'localizador':loc,'verificacao':check}
responses=[
 {'id':'V1-R1','situacao':'corrigido','justificativa':'Aplicado arredondamento usual a duas casas: 0,22393 p.p. torna-se 0,22 p.p. Não foi usado arredondamento por excesso.',
  'evidencias':[evidence('estatistica.json','sensibilidade_cinco; id etapa3_aval_nf4_20261005_135446, campo variacao_pp; máximo absoluto das seis linhas 7B','Conferida a maior alteração de aproximadamente 0,22393 p.p.; nenhuma métrica subjacente foi alterada.')]},
 {'id':'V1-R2','situacao':'corrigido','justificativa':'A afirmação no limiar zero foi restringida às 564 decisões pareadas P-B; o resultado global aparece separadamente com o limiar reconstruído do dev.',
  'evidencias':[evidence('metricas_pareadas.csv','id etapa3_aval_nf4_20260929_072628; politica historico; limiar 0; P_B=564 e P_C=P_V=P_R=0','A evidência abrange 1.128 membros do teste pareado, não todas as funções de todos os splits.'),evidence('metricas_por_execucao.csv','id etapa3_aval_nf4_20260929_072628; f1','O F1 global no limiar do dev é aproximadamente 0,262, e é outra política de decisão.')]},
 {'id':'V1-R3','situacao':'corrigido','justificativa':'A tabela de incerteza passou a 5 e a de recursos a 6, incluindo chamadas; a numeração agora segue a aparição no artigo. Os identificadores T5/T6 dos arquivos derivados históricos foram preservados.','evidencias':[]},
 {'id':'V1-R4','situacao':'corrigido','justificativa':'A estabilidade máxima foi expressa como 0,10 p.p. com arredondamento a duas casas.',
  'evidencias':[evidence('estatistica.json','parametros.estabilidade_endpoint_max=0.0010448182744481338','Multiplicação por 100 resulta em 0,1044818 p.p.; duas casas resultam em 0,10. Não é alegação de precisão de treino.')]},
 {'id':'V1-R5','situacao':'corrigido','justificativa':'Mantida a definição semente de aleatoriedade (seed); as demais ocorrências e tabelas utilizam seed/seeds, inclusive no Resumo e na Introdução.','evidencias':[]},
 {'id':'V1-R6','situacao':'corrigido','justificativa':'Resumo e Abstract identificam explicitamente o modelo 7B, as três seeds e as duas variantes. Também incluído o contraste da referência de tamanho já sustentado nas tabelas.','evidencias':[evidence('estatistica.json','seeds_7b; variantes nf4 e bf16; campo media','Médias das três seeds: 0,5062056738 e 0,4997044917, sem ensemble ou triplicação da amostra.'),evidence('metricas_por_execucao.csv','id baseline_tamanho_tokens_20260924_012407; auc','AUC global arredondada 0,810.'),evidence('metricas_pareadas.csv','id baseline_tamanho_tokens_20260924_012407; politica dev_f1; ordenacao','Ordenação com meio crédito 21,10%; o contraste não demonstra um mecanismo semântico.')]},
 {'id':'V1-R7','situacao':'corrigido','justificativa':'Removida a nota de trabalho da referência Hui; a bibliografia foi ordenada alfabeticamente. A entrada completa permanece no BibTeX e na transposição LaTeX.','evidencias':[]},
 {'id':'V1-R8','situacao':'corrigido','justificativa':'Explicitados os dois modelos Instruct e seus dois splits. A expressão 14 logs foi corrigida para 14 avaliações/33 arquivos: 4 de prompting, 27 de classificadores e 2 da referência de tamanho.','evidencias':[evidence('manifesto.json','execucoes; tipo prompting/classificador/tamanho; lista de fontes por execução','Conferida a contagem de 14 avaliações e dos arquivos correspondentes; avaliações de classificadores reúnem dev, teste e pareado.')]},
]
payload={'versao_base':version['numero'],'sha256_base':version['texto']['sha256'],'contexto_sha256':flow.context_hash(manifest),'parecer_sha256':version['pareceres'][-1]['sha256'],'corretor':'Codex — papel corretor','texto':text,'respostas':responses}
(HERE/'v002_artigo_codex.md').write_text(text,encoding='utf-8')
(HERE/'correcao_v002.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(HERE/'correcao_v002.json')
