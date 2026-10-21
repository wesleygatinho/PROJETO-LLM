"""Documenta a rodada concluída; não redige nem altera o manuscrito."""
import json,sys,shutil,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent; ARTICLE=HERE.parents[1]
def main():
    stage=HERE/sys.argv[1]
    integrated=json.loads((HERE/'integracao.json').read_text(encoding='utf-8'))
    final=json.loads((HERE/sys.argv[2]/'retorno.json').read_text(encoding='utf-8'))
    assert final['decisao']=='aprovar' and final['itens']==[]
    assert final['sha256']==integrated['sha256_integral']
    trans=json.loads((stage/'transposicao.json').read_text(encoding='utf-8'))
    audit=json.loads((stage/'conferencia_tabelas_preservacao.json').read_text(encoding='utf-8'))
    calls=[]
    for path in sorted(HERE.glob('*/resposta_bruta.json')):
        raw=json.loads(path.read_text(encoding='utf-8'))
        config=json.loads((path.parent/'configuracao.json').read_text(encoding='utf-8'))
        assert not raw.get('is_error') and 'claude-opus-5-5' in raw['modelUsage']
        calls.append({'etapa':path.parent.name,'modelo_real':list(raw['modelUsage']),
            'esforco_configurado':config['esforco_solicitado'],'session_id':raw['session_id'],
            'custo_estimado_usd':raw.get('total_cost_usd'),'teto_usd':config['teto_usd'],
            'arquivo_resposta':str(path),'sha256_resposta':hashlib.sha256(path.read_bytes()).hexdigest()})
    assert len({x['session_id'] for x in calls})==len(calls)
    record={'instante_utc':datetime.now(timezone.utc).isoformat(),'integracao':integrated,
        'sessoes':calls,'custo_estimado_total_usd':sum(x['custo_estimado_usd'] for x in calls),
        'decisao_final':final,'compilacao':json.loads((stage/'compilacao.json').read_text(encoding='utf-8')),
        'preservacao':audit,'pendencias_entrega':['Autoria e afiliação completas não confirmadas.',
        'Extensão e regras de páginas não confirmadas.',
        'Compilação e diagramação não validadas: falha de preparação do ambiente Windows antes do TeX.']}
    dest=HERE/'fechamento.json';assert not dest.exists()
    dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    session_table='\n'.join(f"| {x['etapa']} | {x['session_id']} | {x['custo_estimado_usd']:.4f} |" for x in calls)
    text=f'''# Fechamento da reescrita com Claude Opus — 08/10/2026

Versão {integrated['versao_integrada']} integrada após parecer de aprovação, sem apontamentos obrigatórios abertos. A aprovação se refere ao conteúdo científico/editorial examinado, com os limites de leitura declarados em cada parecer. Não certifica a diagramação ou a prontidão para submissão.

## Responsabilidades e esforço

Conforme a orientação do pesquisador, Claude Opus 5.5 realizou diagnóstico, reescrita integral, correções e conferências em sessões distintas. Todas as chamadas desta rodada configuraram explicitamente `--effort xhigh` (EXTRA), modelo real `claude-opus-5-5`, acesso somente Read/Glob/Grep e teto de US$ 3 por chamada. Codex orientou, conferiu fontes e registros, normalizou envelopes quando necessário, transpôs citações/LaTeX e integrou arquivos. Codex não reescreveu a prosa do manuscrito.

| Etapa | Sessão real | Custo estimado (US$) |
| --- | --- | --- |
{session_table}

Total estimado da CLI: US$ {record['custo_estimado_total_usd']:.4f}. Configuração, pedidos, respostas brutas e pareceres permanecem em cada subpasta. São {len(calls)} chamadas independentes, com teto aplicado individualmente, conforme autorização. Os metadados comprovam a configuração e o modelo retornado, sem converter a autoavaliação em garantia de qualidade.

## Mudanças de escrita

O diagnóstico identificou um texto organizado em torno de consolidação e auditoria, com contexto pouco desenvolvido, objetivo tardio e relacionados superficiais. Claude reescreveu Resumo, Abstract, Introdução, Fundamentação e trabalhos relacionados, Materiais e métodos, Resultados, Discussão, Limitações e Conclusão. A estrutura passou a articular problema de detecção, limitações da avaliação, objetivo e contribuições delimitadas. A Introdução permaneceu em cinco parágrafos, sem lista de contribuições. O corpus A08 foi lido integralmente; passagens de A01 e A06 foram usadas nas etapas de diagnóstico/correção. Isso serve de referência de organização e encadeamento, sem atribuir um padrão individual a um coautor nem copiar frases.

O artigo usa {len(trans['referencias'])} referências científicas verificadas e {trans['numero_citacoes']} ocorrências de citação vinculadas no LaTeX. Foram acrescentados Devign, ReVeal, LineVul, DiverseVul, SecLLMHolmes, Saito/Rehmsmeier e Field/Welsh às seis fontes anteriores. Metadados e versões efetivamente lidas estão no catálogo; DOI foi incluído quando verificado. O corpo e a bibliografia científica não contêm links de GitHub. Cinco commits permanecem como fontes documentais da inspeção, exclusivamente no suplemento. Os detalhes de auditoria, custos históricos e rastreabilidade foram concentrados nesse suplemento.

## Correções e conferências

A primeira revisão apontou onze problemas, todos respondidos por Claude e declarados resolvidos pela conferência seguinte. Foram precisados a seleção do limiar de baixa FPR; o meio crédito para empates na ordenação; a cronologia histórica da escolha de época; o alcance descritivo da comparação global/pareada; a diferença entre geração YES/NO e ajuste da cabeça classificadora; as citações vinculadas; a interpretação dos intervalos; os empates de comprimento; a unidade de pares; os papéis dos dois limiares; e o alcance das conclusões. Essa conferência encontrou ainda uma atribuição incorreta à rotulação do PrimeVul. Claude a corrigiu separando exatidão dos rótulos de mitigação de vazamento por deduplicação e divisão cronológica. Uma nova sessão avaliou a versão corrigida.

As seis tabelas experimentais foram comparadas deterministicamente aos resultados congelados; não houve diferença nas células reproduzidas. A tabela de partições foi conferida nos registros da release. Os {audit['fontes_experimentais_preservadas']} arquivos de código, resultados e logs cobertos pelo inventário de preservação mantiveram seus hashes. Nenhum treinamento, inferência, recuperação de pesos, uso de GPU ou RunPod foi executado nesta reescrita. As versões e a bibliografia anteriores foram preservadas; a bibliografia atual tem nome próprio.

O briefing inicial desta rodada confundia seleção de época e limiar F1. Claude identificou a discrepância, Codex conferiu os registros e a orientação posterior foi corrigida. O erro e sua resolução permanecem no histórico; não foram apagados. Uma resposta trouxe prefácio antes do JSON: somente o envelope foi normalizado, com resposta bruta preservada. Um erro inicial de codificação do console ocorreu após salvar o retorno; não exigiu repetir a chamada.

## Arquivos atuais

- Manuscrito: [texto/artigo_completo.md](../../texto/artigo_completo.md).
- LaTeX no mesmo documento aberto: [previa_rascunho_sbc.tex](../introducao_2026-10-07/previa_rascunho_sbc.tex).
- Bibliografia atual: [artigo_opus_extra.bib](../../referencias/artigo_opus_extra.bib).
- Suplemento: [{stage.name}/SUPLEMENTO.md]({stage.name}/SUPLEMENTO.md).
- Parecer final: [{sys.argv[2]}/retorno.json]({sys.argv[2]}/retorno.json).
- Versões e contratos: [rodada artigo_opus_extra_01](../fluxo_editorial/rodadas/artigo_opus_extra_01/manifesto.json).
- Metadados deste fechamento: [fechamento.json](fechamento.json).

## Pendências e limites

A compilação interna falhou na preparação do ambiente Windows, antes de haver diagnóstico de linha TeX: `Could not prepare the LaTeX preview`; `windows sandbox: helper_unknown_error: setup refresh had errors`. O diagnóstico foi salvo por versão. Não houve compilação externa, substituição do documento ou abertura de nova aba. PDF, quebras, tabelas renderizadas, citações renderizadas e número de páginas ainda não foram validados. Autoria/afiliação completas e regras de extensão também precisam ser confirmadas. Não foi produzido PDF final para entrega.

As leituras de revisão incluem buscas focais nos originais; o último parecer conserva seus limites próprios, e não se afirma que todos os revisores leram todos os arquivos. As conferências locais de Codex complementaram os registros, inclusive onde o revisor não confirmou dados. Os resultados continuam exploratórios e retrospectivos; acesso prévio ao teste, poucas sementes, truncamento, pares não certificados e condições específicas de implantação permanecem explícitos no manuscrito. As referências adicionais e a aprovação editorial não eliminam esses limites.
'''
    (HERE/'FECHAMENTO.md').write_text(text,encoding='utf-8')
    (HERE/'README.md').write_text('# Reescrita integral por Claude Opus 5.5 xhigh\n\n[Fechamento, arquivos atuais e pendências](FECHAMENTO.md).\n\nAs subpastas numeradas preservam chamadas reais, versões e conferências. `antes/` guarda a versão substituída; os experimentos permanecem preservados.\n',encoding='utf-8')
    old=HERE/'antes/README.md';assert not old.exists();shutil.copyfile(ARTICLE/'README.md',old)
    (ARTICLE/'README.md').write_text(f'''# Artigo de Seminários — PPGCC UFMA — 11/11/2026

**Estado em 08/10/2026: manuscrito reescrito integralmente por Claude Opus 5.5 com esforço xhigh, corrigido e conferido em sessões novas.** Codex orientou, verificou fontes/registros e integrou os arquivos. O parecer final aprova o conteúdo examinado sem apontamentos obrigatórios abertos; compilação e diagramação continuam pendentes.

- [Artigo completo atual](texto/artigo_completo.md).
- [Fonte SBC no mesmo documento aberto](revisao/introducao_2026-10-07/previa_rascunho_sbc.tex).
- [Bibliografia atual — 13 fontes científicas](referencias/artigo_opus_extra.bib).
- [Fechamento, mudanças, chamadas reais e pendências](revisao/reescrita_opus_extra_2026-10-08/FECHAMENTO.md).
- [Suplemento atual](revisao/reescrita_opus_extra_2026-10-08/{stage.name}/SUPLEMENTO.md).
- [Versões e pareceres atuais](revisao/fluxo_editorial/rodadas/artigo_opus_extra_01/manifesto.json).
- [Catálogo com metadados e versões lidas](revisao/reescrita_opus_extra_2026-10-08/catalogo_verificado.json).
- [Verificação das fontes adicionais](../../../02_referencias/verificacao_reescrita_opus_2026-10-08/LEITURA_ADICIONAIS.md).

**Pendências para entrega:** autoria/afiliação completa, regras de extensão e validação de compilação/diagramação. O compilador interno falhou ao preparar o ambiente Windows antes do TeX; não há PDF final validado.

Os experimentos históricos foram preservados, sem treino, inferência ou RunPod nesta reescrita. A análise continua retrospectiva e exploratória, com os limites declarados no artigo. Os resultados congelados estão em `03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08`. `texto/secoes/artigo_opus_extra/` guarda as seções atuais. As tabelas/figura e os produtos da consolidação anterior permanecem em suas pastas históricas.

## Histórico preservado

- [README anterior](revisao/reescrita_opus_extra_2026-10-08/antes/README.md).
- [Fechamento da primeira redação integral](revisao/artigo_completo_2026-10-08/FECHAMENTO.md).
- [Suplemento anterior](revisao/artigo_completo_2026-10-08/SUPLEMENTO.md).
- [Bibliografia anterior congelada](referencias/artigo.bib).
- [Primeiro ciclo integral](revisao/fluxo_editorial/rodadas/artigo_completo_01/manifesto.json).
- [Conferência integral anterior](revisao/fluxo_editorial/rodadas/artigo_completo_02/manifesto.json).

## Guias do projeto

- [Plano de escrita](PLANO_ESCRITA.md).
- [Matriz histórica de evidências](MATRIZ_EVIDENCIAS.md).
- [Padrão de escrita](PADRAO_ESCRITA.md).
- [Template SBC e proveniência](template_sbc/README.md).
- [Mecanismo editorial](revisao/fluxo_editorial/README.md).
- [Plano técnico](../../../01_planejamento/artigo_seminarios_2026/PLANO_EXECUCAO.md).
- [Cronograma histórico](../../../01_planejamento/artigo_seminarios_2026/CRONOGRAMA_CHECKLIST.md).

Planos e matrizes anteriores representam seu estado datado. A pasta `entrega/` não contém PDF final validado; apresentação e submissão não foram realizadas.
''',encoding='utf-8')
    print(json.dumps({'fechamento':str(HERE/'FECHAMENTO.md'),'sessoes':len(calls),'custo_estimado_usd':record['custo_estimado_total_usd'],'pendencias':record['pendencias_entrega']},ensure_ascii=False))
if __name__=='__main__':main()
