"""Conferência local de preservação, tabelas e vínculos; não aprova texto automaticamente."""
import sys, json, re, hashlib, csv
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
FLOW=ROOT/'04_escrita/artigo/seminarios_2026/revisao/fluxo_editorial'
DER=ROOT/'03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08'
sys.path.insert(0,str(FLOW))
import gerenciar as flow
directory,manifest=flow.load('artigo_completo_02')
v=flow.current(manifest)
text=flow.read_artifact(directory,v['texto']).decode('utf-8')
old_text=(FLOW/'rodadas/artigo_completo_01/versoes/v002.md').read_text(encoding='utf-8')
old_phrase='Para uma matriz pré-treinada W₀, a atualização assume a forma W₀ + BA, com posto r menor que as dimensões da matriz;'
new_phrase='Para uma matriz pré-treinada W₀ de dimensões d × k, a atualização é representada por ΔW = BA, de modo que o peso adaptado é W₀ + BA, com posto r muito menor que o mínimo entre d e k;'
assert text.strip()==old_text.replace(old_phrase,new_phrase).strip(),'Regressão ou mudança adicional em v003'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

old=json.loads((HERE/'preservacao_antes.json').read_text(encoding='utf-8'))['arquivos']
changed=[p for p,h in old.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
assert not changed,changed
tables=re.findall(r'(?m)^\|.*(?:\n\|.*)*',text)
assert len(tables)==6,len(tables)
mapping=['T1_configuracoes.md','T2_prompting.md','T3_global.md','T4_pareado.md','T6_incerteza.md','T5_recursos.md']
for block,name in zip(tables,mapping):
    source=(DER/'tabelas'/name).read_text(encoding='utf-8')
    assert block.strip()==re.search(r'(?m)^\|.*(?:\n\|.*)*',source)[0].strip(),name
inventory=json.loads((DER/'manifesto.json').read_text(encoding='utf-8'))
evaluations=inventory['execucoes']
assert len(evaluations)==14
assert sum(len(r['logs']) for r in evaluations)==33
assert json.loads((DER/'divergencias.json').read_text(encoding='utf-8'))==[]
inspection=json.loads((DER/'inspecao_correspondencia_commits.json').read_text(encoding='utf-8'))
assert len(inspection)==5
for r in inspection:
    assert all(r[k] for k in ['vulneravel_encontrada_pai','corrigida_encontrada_pai','corrigida_encontrada_commit','funcao_corrigida_diferente_da_funcao_alterada'])
    for file in r['fontes'].values():assert digest(ROOT/file['arquivo'])==file['sha256']
exports=json.loads((DER/'proveniencia_exports.json').read_text(encoding='utf-8'))
altered_sources=[p for p,h in exports['fontes'].items() if digest(ROOT/p)!=h]
altered_code=[p for p,h in exports['codigo'].items() if digest(ROOT/p)!=h]
assert not altered_sources,altered_sources
assert altered_code==['03_experimentos/codigo/consolidacao_artigo/04_exportar_artigo.py','03_experimentos/codigo/consolidacao_artigo/recuperar_tokenizer.py'],altered_code
audit={'versao':v['numero'],'sha256':v['texto']['sha256'],'arquivos_preservados':len(old),'alteracoes_historicas':changed,'fontes_editoriais_conferidas_por_hash':len(manifest['fontes']),'tabelas_conferidas':mapping,'avaliacoes':14,'arquivos_previsao':33,'divergencias_metricas':[],'commits_inspecionados':5,'testes_cientificos':'Oito testes passaram na execução local registrada nesta conversa.','fontes_exportadas_inalteradas':len(exports['fontes']),'diferencas_hash_codigo':[{'arquivo':altered_code[0],'motivo':'Fixação posterior do cache MPLCONFIGDIR no workspace.'},{'arquivo':altered_code[1],'motivo':'Inclusão posterior da recuperação do tokenizer7B e assert de identidade com3B; artefatos recuperados possuem proveniência própria. Nenhuma alteração de cálculo.'}],'observacao':'Código final congelado na rodada. Proveniência da exportação anterior preservada; diferenças explicitadas, sem apagar cronologia ou alterar resultados.'}
audit.update({'rodada':'artigo_completo_02','manuscrito':'v003','diff_integral_v002_v003':'A única alteração textual foi a correção P1 da definição LoRA; comparação integral feita localmente, normalizando apenas espaços externos.'})
(HERE/'auditoria_final.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

checks=[]
def add(start,source,locator,verification):
    # Registrar o trecho literal final, junto à fonte realmente conferida.
    paras=text.split('\n\n')
    found=[p for p in paras if p.startswith(start)]
    assert len(found)==1,(start,len(found))
    checks.append({'alegacao':found[0],'fonte':source,'localizador':locator,'verificacao':verification})
def result(start,file,loc,verification):add(start,(DER/file).relative_to(ROOT).as_posix(),loc,verification)
PRIM='02_referencias/verificacao_introducao_seminarios_2026/'
add('A avaliação de modelos',PRIM+'primevul_pdf.txt','páginas físicas 2 e 6; seção IV, avaliação','Conferido que as métricas agregadas, o desbalanceamento, os pares e a restrição de FPR são discutidos. O artigo não transfere os números de Ding ao bloco Qwen.')
add('O PrimeVul foi desenvolvido',PRIM+'primevul_pdf.txt','páginas 2–6; criação e avaliação do PrimeVul','C/C++, deduplicação, divisão temporal e diretrizes de avaliação; texto final qualifica a correspondência na release e não declara compreensão semântica.')
add('Essa cautela encontra respaldo',PRIM+'risse_pdf.txt','página física 2 e páginas 7–10; limitações e transformações','Conferidas dificuldades nas técnicas e conjuntos daquele trabalho; não universalizadas. A descrição de TrapEval também foi conferida em Huang, pp. 1–4 e 7–10, nas leituras primárias registradas.')
add('A análise dessas condições',PRIM+'qlora_pdf.txt','pp. 1–4, seção 3; NF4, base congelada e adaptação','Escopo de memória/adaptação; não se transfere equivalência de tarefas. Qwen pp. 1,3–4,7–8 e LoRA pp. 1,4–5 conferidos no registro primário.')
add('LoRA representa',PRIM+'lora_pdf.txt','pp. 4–5, seção 4.1; W0+BA','Base congelada, matrizes de baixo posto. QLoRA distingue armazenamento e computação; implementação local AdamW convencional, conferida em 06_treinar_qlora.py:273–274.')
add('O posicionamento científico',PRIM+'huang_pdf.txt','pp. 1–4 e 7–10; TrapEval, V2P/V2N, modelos','Protocolo e modelo Instruct conferidos; o estudo local não executa esses testes nem diagnostica Semantic Trap ou reivindica prioridade.')
result('Realizou-se uma consolidação','manifesto.json','execucoes; logs; treinos_oficiais','14 avaliações/33 arquivos; nove classificadores, quatro avaliações de prompting e referência de tamanho. A consolidação executada foi em CPU; não houve novas execuções de modelos.')
result('A release original foi recuperada','manifesto.json','fontes/release e inventário','Contagens conferidas nos seis JSONL recuperados e registradas na auditoria; coincidência com prefixos históricos, sem alegação de hashes completos passados.')
result('Cada log foi alinhado','auditoria_integridade.json','identidade; reutilizações teste e validação','Alinhamento integral por posição/idx/projeto/commit/rótulo, sem divergências. Reutilizações oficiais conferidas por conteúdo, preservadas posicionalmente.')
result('A auditoria distinguiu','inspecao_correspondencia_commits.json','cinco registros; fontes.pai/commit; decisões','Arquivos primários antes/depois e diffs conferidos para os cinco pares. Membro benigno corresponde a outra função preexistente; não é prova de validade dos demais pares. Hashes das dez cópias primárias reconferidos.')
result('As avaliações por prompting','manifesto.json','quatro registros prompting, historico.observacoes e n_cortadas; logs','FP16 e parser conferidos no código 03; limite 8192 consta dos quatro registros históricos, com 76 truncadas no global e 38 no pareado, não inferido do default atual do script.')
add('Para os classificadores','03_experimentos/codigo/06_treinar_qlora.py','argumentos 168–175; otimizador/agendamento 269–280; loop 300–340','Receitas históricas conferem lr0.0002/lote16/warmup0.03/r16/alpha32/dropout0.05; AdamW peso0, agendamento linear e treinamento da cabeça. NF4/double quant/compute BF16 conferidos em classificador.py.')
result('Todos os pilotos 3B','manifesto.json','treinos_oficiais; argumentos das receitas; seis rodadas','Composições, seeds e orçamentos conferidos. Pareamento por tamanho utiliza comprimentos limitados a 2048; código histórico confirma seleção sem reutilização. Comparação não causal.')
result('A seleção histórica','selecao_epocas.json','seis rodadas; historica_estrita; ajustada_reconstruida; mesma','Seleção ajustada reconferível e mantida nas quatro rodadas com tamanho; duas sem registro de empates têm null e limite explícito. Subamostra da AUC por época não confundida com dev completo.')
add('Para cada checkpoint 7B','03_experimentos/codigo/07_avaliar_classificador.py','carga e merge, linhas 113–123; variante e época','Mesmo checkpoint/seed em NF4 com adaptador e BF16 mesclada. Construção e representação diferem simultaneamente, impedindo isolamento causal de bits.')
result('Os classificadores e a referência','tokenizacao_proveniencia.json','revisao_modelo_recuperada; historico; pares_tokens_identicos_2048; pares_ambos_nao_truncados','Tokenizer recuperado da revisão histórica, comprimentos/truncamentos confrontados aos logs; revisão própria do baseline ausente e explicitada. Tokenizers 3B/7B têm o mesmo hash.')
add('A regra classificatória','03_experimentos/codigo/consolidacao_artigo/comum.py','best_f1 e fpr_threshold, linhas 39–49; metrics','Score>limiar, agrupamento de empates no F1 e corte nextafter; seleção de restrição nos negativos do dev. Limiares aplicados sem recálculo no teste.')
add('No teste global, calcularam-se','03_experimentos/dados/artigo_seminarios_2026/fontes_publicas/calc_vd_score_oficial.py','calc_vd_score, curva ROC e comparação inclusiva','Código oficial escolhe ponto no conjunto fornecido e usa >=. Procedimento local distinto usa calibração no dev e >; FPR de teste explicitamente relatada.')
add('No pareado, orientando','03_experimentos/codigo/consolidacao_artigo/02_consolidar_metricas.py','pair categories e pair_value; política historico/dev_f1','Categorias P-C/P-V/P-B/P-R conferidas contra decisões, ordenação meio crédito independente de limiar. Referência de simetria não adotada como teste semântico.')
result('Os scores históricos','divergencias.json','lista vazia; verificação round4 na consolidação','Contagens, categorias históricas e métricas calibradas/AUC coincidiram na precisão publicada; logs têm cinco casas. Limite de precisão preservado.')
result('A variação entre seeds','estatistica.json','parametros; seeds_7b; comparacoes; por_execucao','10.000 réplicas, seed20261008,550grupos, alinhamento de variantes e seeds, pesos por pares. Média e DP descritivos; IC condicionado a modelos. Estabilidade max0.10448pp expressa 0.10pp.')
result('Para examinar truncamento','sensibilidade_truncamento.csv','n_pares e ordenacao; recorte465','Denominador465 e política constante. Cruzamento com cinco exclusões resulta460, conferido em sensibilidade_correspondencia.csv; mudança composicional explicitada.')
add('Os recursos provêm','03_experimentos/codigo/07_avaliar_classificador.py','linhas 125–157; janela/reset/tempo e preço; manifesto historico','GPU/versões conferidos nos CSVs e receitas. Memória alocada e janela após carga/merge; tempo dividido por n_teste e custo histórico. Não é energia, faturamento ou latência individual.')
result('A junção dos 33','auditoria_integridade.json','identidade; arquivos de 14 avaliações','33arquivos alinhados, cobertura integral; 1128posições e1126idx distintos no pareado. Campos documentais conferidos sem certificar correspondência semântica.')
result('No prompting global','metricas_por_execucao.csv','duas linhas prompting teste; metricas_pareadas.csv prompting','Precisão, revocação, F1 e FPR reconferidos; categorias somam564. Escopo restrito à instrução/parser registrados.')
result('A referência de tamanho alcançou','metricas_por_execucao.csv','dez linhas de classificadores/referência; f1/auc/precisao/recall','Valores das tabelas e faixas conferidos. F1 máximo3Breal e comparação não causal; tabelas verificadas integralmente por igualdade aos exports derivados.')
result('O limiar F1 e o limiar','metricas_por_execucao.csv','fnr_limiar_fpr_dev; fpr_teste_limiar_fpr_dev; limiar_fpr','FPR acima do nominal explicitada, somente seed2 7B abaixo. Baseline limiar2048 com regra estrita implica nenhum positivo. São pontos de decisão distintos.')
result('A ordenação da referência','metricas_pareadas.csv','politica dev_f1; ordenacao e P_C','Ordenação, empates e categorias conferidos para dezconfigurações; PC5–8 nos seis 7B. Ordenação não implica duas decisões corretas.')
result('A média de ordenação','estatistica.json','seeds_7b; comparacoes última linha','NF4mean50.62SD5.17, BF16mean49.97SD4.63, diferença0.65ppIC[-1.22,2.54]. IC não comprova equivalência nem representa futuros treinamentos.')
result('Nos 465 pares','tokenizacao_proveniencia.json','pares_tokens_identicos_2048=32; pares_ambos_nao_truncados=465','Resultados por seed conferidos na sensibilidade e32sequências idênticas. Empates de score32–40; não inferir identidade apenas por empate ou isolar efeito causal do truncamento.')
result('Ao remover os cinco','estatistica.json','sensibilidade_cinco; linhas dos seis7B; variacao_pp','Faixas559 reconferidas; maior alteração0.2239308pp arredondada0.22. Não valida559pares nem recupera contrapartes semprevisões.')
result('NF4 registrou','tabelas_artigo.md','Tabela5 derivados: recursos; seislinhas7B','Memórias4.63/12.49vs14.15/20.76; redução67%apóscarga e40%picos; tempos59.6–60.0vs46.8–47.1ms e custos. Números descritivos, sem repetição independente de desempenho.')
result('A calibração também altera','metricas_pareadas.csv','3Breal politica historico, P_B564','Discussão corrigida limita afirmação zero ao pareado; F1global0.262 fica separado. As demais sínteses da discussão e conclusão correspondem às checagens numéricas anteriores e mantêm limitações.')

# Cobertura integral das tabelas numéricas (cabeçalhos/células), sem presumir que o controlador entende ciência.
for i,block in enumerate(tables):
    checks.append({'alegacao':block,'fonte':(DER/'tabelas_artigo.md').relative_to(ROOT).as_posix(),'localizador':'tabela derivada '+mapping[i], 'verificacao':'Cada célula coincide com a tabela gerada diretamente dos CSVs/JSONs já conferidos. Numeração no artigo ajustada pela aparição; identificadores de arquivos preservados.'})
verification={'versao':v['numero'],'sha256':v['texto']['sha256'],'verificador':'Codex — conferência local de fontes, métricas e incorporação','escopo':'Conteúdo científico/editorial do manuscrito. Identificação, regras de extensão e compilação/diagramação são limitações externas explicitadas no fechamento; não se declara prontidão de submissão.','pendencias':[],'checagens':checks}
(HERE/'verificacao_integracao.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'auditoria':audit,'checagens_cientificas':len(checks)},ensure_ascii=False,indent=2))
