"""Registra compilação e prova a preservação do conteúdo, sem reescrever o artigo."""
import json,hashlib,sys,shutil
from pathlib import Path
from datetime import datetime,timezone
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent;ARTICLE=HERE.parents[1]
DOC=ARTICLE/'revisao/introducao_2026-10-07/previa_rascunho_sbc.tex'
before=(HERE/'fonte_antes.txt').read_text(encoding='utf-8')
after=DOC.read_text(encoding='utf-8')
oldbody=before.split('\\begin{document}',1)[1]
newbody=after.split('\\begin{document}',1)[1]
newbody=newbody.replace('\\begin{sbcfitwidth}\n\\begin{tabular}',
                        '\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}')
newbody=newbody.replace('\\end{tabular}\n\\end{sbcfitwidth}\n\\end{table}',
                        '\\end{tabular}}\n\\end{table}')
newbody=newbody.replace('\\begin{thebibliography}{99}',
                        '\\clearpage\n\\begin{thebibliography}{99}')
assert oldbody==newbody,'O corpo sofreu alteração além das caixas/quebra de página declaradas.'
qa=json.loads((HERE/'verificacao_pdf.json').read_text(encoding='utf-8'))
assert qa['sha256_tex']==hashlib.sha256(DOC.read_bytes()).hexdigest()
assert qa['referencias_sem_interrogacao'] and not any('Overfull' in w or 'undefined' in w or 'Error' in w for w in qa['avisos_relevantes'])
shutil.copyfile(DOC.with_suffix('.log'),HERE/'compilacao_final.log')
record={'instante_utc':datetime.now(timezone.utc).isoformat(),
    'erro_original':'LaTeX Error: File natbib.sty not found.',
    'solucao':'miktex packages install natbib, executado com êxito no perfil do usuário.',
    'compilacao_local':'latexmk -pdf previa_rascunho_sbc.tex, código de saída 0.',
    'configuracao':['Diretivas pdfLaTeX e UTF-8 no documento existente.',
        '.latexmkrc local com passagens automáticas e SyncTeX; bibliografia incorporada.',
        'compilar_sbc.cmd compila na pasta correta mesmo quando chamado de outro diretório.',
        'Idioma brazilian; tabelas só reduzem quando necessário, sem ampliar as estreitas.',
        'Removida quebra forçada antes das referências.'],
    'corpo_cientifico_preservado':True,'verificacao_preservacao':'Comparação exata do corpo após reverter somente os invólucros de tabelas e a quebra de página.',
    'inspecao_visual':'Primeira página em resolução maior e folhas de contato de todas as 15 páginas. Sem cortes ou sobreposições observados.',
    'pdf':qa,'compilador_interno':json.loads((HERE/'compilador_interno.json').read_text(encoding='utf-8')),
    'limites':['Prévia interna do Codex ainda falha na preparação do ambiente; PDF local compila e pode ser aberto.',
        'Autoria completa e regras de extensão continuam pendentes.',
        'Resumo e Abstract estão mais longos que as dez linhas do guia local. Não houve reescrita ou redução artificial de fonte para forçar a extensão.']}
(HERE/'registro.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copyfile(ARTICLE/'README.md',HERE/'README_antes.md')
readme=(ARTICLE/'README.md').read_text(encoding='utf-8')
readme=readme.replace('compilação e diagramação continuam pendentes.',
    'a compilação local do documento SBC foi corrigida e o PDF atual foi inspecionado; a prévia interna do Codex continua com falha de ambiente.')
readme=readme.replace('**Pendências para entrega:** autoria/afiliação completa, regras de extensão e validação de compilação/diagramação. O compilador interno falhou ao preparar o ambiente Windows antes do TeX; não há PDF final validado.',
    '**Compilação local corrigida:** o mesmo documento gerou um PDF de 15 páginas com MiKTeX, após instalar natbib. [PDF atual](revisao/introducao_2026-10-07/previa_rascunho_sbc.pdf) · [Como compilar](revisao/introducao_2026-10-07/COMPILAR_SBC.md) · [Registro técnico](revisao/configuracao_sbc_2026-10-08/registro.json). As páginas foram inspecionadas, sem cortes ou sobreposições observados. A prévia interna do Codex ainda falha antes do TeX.\n\n**Pendências para entrega:** autoria/afiliação completa, regras de extensão e ajuste editorial do comprimento dos resumos. O PDF local serve à visualização da versão atual; não se declara conformidade final de submissão.')
readme=readme.replace('A pasta `entrega/` não contém PDF final validado; apresentação e submissão não foram realizadas.',
    'O PDF atual está ao lado do documento aberto; não foi criado outro manuscrito nem aberta nova aba. A pasta `entrega/` permanece histórica; apresentação e submissão não foram realizadas. Os fechamentos anteriores preservam o estado da compilação nas respectivas etapas.')
(ARTICLE/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps({'pdf':qa['arquivo_pdf'],'paginas':qa['paginas'],'corpo_preservado':True,'registro':str(HERE/'registro.json')},ensure_ascii=False))
