from pathlib import Path
import json, math, re, html
from statistics import mean
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf/Guia_Completo_do_Projeto_Mestrado_09-10-2026.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
TMP = ROOT / 'tmp/pdfs'
for name, filename in [('Body','calibri.ttf'),('Bold','calibrib.ttf'),('Italic','calibrii.ttf'),('Light','calibril.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+filename))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')

NAVY=HexColor('#142D42'); TEAL=HexColor('#087E86'); INK=HexColor('#253E50')
MUTED=HexColor('#5C6D79'); PALE=HexColor('#EAF5F4'); LINE=HexColor('#D7E2E7')
GOLD=HexColor('#D39E43'); CREAM=HexColor('#FAF8F3'); RED=HexColor('#B65C4C')
W,H=595.276,841.89; M=48; WIDTH=W-2*M
styles={
 'p':ParagraphStyle('p',fontName='Body',fontSize=11.6,leading=16.2,textColor=INK,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Body',fontSize=9.4,leading=12.7,textColor=MUTED),
 'h2':ParagraphStyle('h2',fontName='Bold',fontSize=15,leading=19,textColor=NAVY),
 'box':ParagraphStyle('box',fontName='Body',fontSize=11.2,leading=15.5,textColor=INK),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=10.1,leading=13,textColor=INK),
 'head':ParagraphStyle('head',fontName='Bold',fontSize=10,leading=12.8,textColor=white),
 'code':ParagraphStyle('code',fontName='Mono',fontSize=9.3,leading=13.5,textColor=NAVY),
}
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Entendendo o projeto de mestrado: do início aos resultados')
c.setAuthor('Guia didático do projeto - PPGCC UFMA')
c.setSubject('PrimeVul, Qwen2.5-Coder, QLoRA, avaliação de vulnerabilidades e implantação')
pages=[]; y=0; current=''; foot=''; page_no=0; min_y=10000

def para(text,style='p',width=None,x=M,gap=8):
    global y,min_y
    p=Paragraph(text,styles[style]); pw,ph=p.wrap(width or WIDTH,700)
    if y-ph < 63: raise RuntimeError(f'Overflow page {page_no} {current}: y={y}, h={ph}, text={text[:80]}')
    p.drawOn(c,x,y-ph); y-=ph+gap; min_y=min(min_y,y)
    return ph

def h2(text):
    global y
    y-=5; para(text,'h2',gap=8)

def box(title,text,color=PALE):
    global y,min_y
    p=Paragraph('<b>'+title+'</b><br/>'+text,styles['box']); _,ph=p.wrap(WIDTH-28,700)
    height=ph+24
    if y-height<63: raise RuntimeError(f'Box overflow p{page_no}')
    c.setFillColor(color);c.roundRect(M,y-height,WIDTH,height,9,fill=1,stroke=0)
    p.drawOn(c,M+14,y-height+12); y-=height+13;min_y=min(min_y,y)

def table(headers, rows, widths=None, size=10.1):
    global y,min_y
    cs=ParagraphStyle('ct',parent=styles['cell'],fontSize=size,leading=size*1.28)
    data=[[Paragraph(str(x),styles['head']) for x in headers]]+[[Paragraph(str(x),cs) for x in row] for row in rows]
    t=Table(data,colWidths=widths or [WIDTH/len(headers)]*len(headers),hAlign='LEFT')
    t.setStyle(TableStyle([
      ('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
      ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
      ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
      ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#F0F5F7')]),
      ('LINEBELOW',(0,-1),(-1,-1),0.5,LINE),
    ]))
    _,th=t.wrap(WIDTH,700)
    if y-th<63:raise RuntimeError(f'Table overflow p{page_no}: {y=} {th=}')
    t.drawOn(c,M,y-th);y-=th+13;min_y=min(min_y,y)

def bullet(label,text): para('<b>'+label+'</b> '+text)

def start(title,kicker,source=''):
    global y,current,foot,page_no,min_y
    page_no+=1;current=title;foot=source;min_y=10000
    pages.append({'page':page_no,'title':title,'source':source})
    c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(TEAL);c.rect(0,H-8,W,8,fill=1,stroke=0)
    c.setFont('Bold',9);c.setFillColor(TEAL);c.drawString(M,H-43,kicker.upper())
    p=Paragraph(title,ParagraphStyle('title',fontName='Bold',fontSize=25,leading=29,textColor=NAVY))
    _,ph=p.wrap(WIDTH,100);p.drawOn(c,M,H-64-ph);y=H-81-ph
    c.bookmarkPage(f'p{page_no}');c.addOutlineEntry(title,f'p{page_no}',0,False)

def end():
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,53,W-M,53)
    if foot:
        p=Paragraph(foot,ParagraphStyle('foot',parent=styles['small'],fontSize=7.8,leading=9.4))
        _,ph=p.wrap(WIDTH-32,30);p.drawOn(c,M,57)
    c.setFillColor(MUTED);c.setFont('Body',8);c.drawString(M,33,'PPGCC UFMA  |  Guia didático  |  Registros até 09/10/2026')
    c.setFont('Bold',9);c.drawRightString(W-M,33,f'{page_no:02d}')
    pages[-1]['lowest_content_y']=round(min_y,1);c.showPage()

def flow(items):
    global y
    bw=(WIDTH-24)/3;bh=74
    for i,(a,b) in enumerate(items):
        xx=M+i*(bw+12)
        c.setFillColor(PALE);c.roundRect(xx,y-bh,bw,bh,8,fill=1,stroke=0)
        p=Paragraph('<b>'+a+'</b><br/>'+b,styles['box']);_,ph=p.wrap(bw-18,100);p.drawOn(c,xx+9,y-12-ph)
        if i<2:
            c.setFillColor(TEAL);c.setFont('Bold',13);c.drawCentredString(xx+bw+6,y-44,'>')
    y-=bh+17

def bars(rows,max_value=100,suffix='%',ref=None,height=26):
    global y
    left=M+169;barwidth=WIDTH-228
    for label,value,color in rows:
        c.setFillColor(INK);c.setFont('Body',10.1);c.drawString(M,y-13,label)
        c.setFillColor(HexColor('#EDF2F4'));c.roundRect(left,y-17,barwidth,12,3,fill=1,stroke=0)
        c.setFillColor(color);c.roundRect(left,y-17,max(1,barwidth*value/max_value),12,3,fill=1,stroke=0)
        if ref is not None:
            xx=left+barwidth*ref/max_value;c.setStrokeColor(GOLD);c.setLineWidth(1.3);c.line(xx,y-20,xx,y-2)
        c.setFillColor(INK);c.setFont('Bold',10);c.drawRightString(W-M,y-14,('%0.2f'%value).replace('.',',')+suffix)
        y-=height
    y-=9

# 01 - capa
page_no=1;pages.append({'page':1,'title':'Capa'})
c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColor(TEAL);c.rect(0,H-15,W,15,fill=1,stroke=0)
c.setFillColor(HexColor('#1D4057'));c.circle(W+50,485,225,fill=1,stroke=0)
c.setFillColor(GOLD);c.setFont('Bold',10);c.drawString(M,H-80,'MESTRADO EM CIÊNCIA DA COMPUTAÇÃO  /  UFMA')
for txt,yy,sz in [('Entendendo',H-155,43),('o projeto',H-208,43),('desde o início',H-261,43)]:
    c.setFont('Bold',sz);c.setFillColor(white);c.drawString(M,yy,txt)
p=Paragraph('Como modelos de inteligência artificial foram avaliados para detectar vulnerabilidades em código, quanto custaram e o que os resultados ensinam.',ParagraphStyle('cover',fontName='Body',fontSize=17,leading=23,textColor=HexColor('#D4E8EF')))
p.wrap(WIDTH-20,200);p.drawOn(c,M,382)
c.setStrokeColor(HexColor('#477083'));c.line(M,348,W-M,348)
c.setFont('Bold',12);c.setFillColor(white);c.drawString(M,314,'UM GUIA PARA QUEM ESTÁ COMEÇANDO DO ZERO')
for i,t in enumerate(['Conceitos explicados antes das siglas','Dataset, experimentos, resultados e decisões','Exemplos didáticos, gráficos, tabelas e glossário']):
    c.setFont('Body',12);c.setFillColor(HexColor('#D4E8EF'));c.drawString(M,280-i*25,t)
c.setFont('Body',10.5);c.setFillColor(white);c.drawString(M,112,'Base documental consultada em 9 de outubro de 2026')
c.setFont('Body',9.5);c.setFillColor(HexColor('#B3D0DA'));c.drawString(M,89,'Relato do trabalho realizado e de seus limites, com próximos passos separados.')
c.setFont('Bold',9);c.drawRightString(W-M,33,'01');c.bookmarkPage('p1');c.addOutlineEntry('Capa','p1',0,False);c.showPage()

# 02
start('Como ler este guia','Seu caminho de aprendizagem')
para('Este documento foi escrito para uma pessoa que ainda não conhece programação, inteligência artificial ou pesquisa experimental. A leitura começa pelos conceitos, passa pelos dados e chega aos resultados reais do projeto. Não é necessário entender matemática avançada.')
box('A pergunta em uma frase','É possível usar um modelo menor e mais econômico para reconhecer falhas de segurança em código, sem confiar em pontuações que escondem o problema?')
table(['Percurso','Páginas','O que você vai entender'],[
 ['1. Começar do zero','3-6','Código, vulnerabilidade, modelos e origem do projeto.'],
 ['2. Conhecer os dados','7-11','PrimeVul, rótulos, partições, pares e versões.'],
 ['3. Aprender a avaliar','12-15','Erros, F1, AUC, limiares e avaliação pareada.'],
 ['4. Acompanhar a execução','16-21','Infraestrutura, prompting, ajuste e pilotos.'],
 ['5. Interpretar os resultados','22-27','Desempenho, sementes, recursos e auditoria.'],
 ['6. Situar o estado atual','28-34','Limites, entregas, próximos passos, glossário e fontes.'],
 ],[135,55,WIDTH-190])
h2('Três cuidados durante a leitura')
para('<b>Exemplo didático</b> significa uma situação inventada para ensinar. <b>Resultado do projeto</b> significa um número extraído dos registros locais. <b>Planejado</b> significa que a proposta existe, mas não há evidência de execução naquele bloco.')
para('Os resultados adotam a consolidação de 08/10/2026 e o manuscrito atual. Notas antigas ajudam a contar a história; interpretações antigas mais fortes foram substituídas pela leitura científica mais cuidadosa da versão atual. As fontes [S1]-[S9] e [R1]-[R6] estão nas páginas 33-34.','small')
end()

# 03
start('Primeiro: qual problema queremos resolver?','1 / Conceitos fundamentais','Base: anteprojeto e manuscrito atual [S1, S4]. Exemplo de código criado para ensino.')
para('Um programa é um conjunto de instruções que diz ao computador o que fazer. Essas instruções são o <b>código-fonte</b>. Uma <b>função</b> é um trecho organizado desse código que realiza uma tarefa: ler um arquivo, copiar dados ou processar uma mensagem, por exemplo.')
para('Uma vulnerabilidade é uma falha que pode comprometer a segurança. Dependendo do caso, ela pode permitir acesso indevido a dados, execução de comandos ou interrupção de um serviço. Nem todo erro de programa é uma vulnerabilidade, e reconhecer uma falha pode exigir contexto que não aparece em uma única função.')
h2('Um exemplo sem precisar saber programar')
para('Imagine uma função que copia uma mensagem para um espaço com capacidade de oito posições. Se ela aceita uma mensagem maior sem conferir o limite, pode escrever fora do espaço reservado. Uma correção possível é verificar o tamanho antes da cópia.')
table(['Versão vulnerável - exemplo','Versão corrigida - exemplo'],[
 ['Receber mensagem<br/>Copiar mensagem para o espaço reservado','Receber mensagem<br/><b>Conferir se ela cabe</b><br/>Se couber, copiar; caso contrário, rejeitar'],
 ],[WIDTH/2,WIDTH/2])
box('O que o projeto pede ao modelo','Receber o corpo de uma função C/C++ e indicar se ela deve ser classificada como vulnerável. A avaliação compara a resposta com o rótulo do dataset.')
para('O trabalho executado classifica funções. Ele não demonstra localização exata da linha defeituosa nem correção automática de programas. A utilidade possível é apoiar a triagem: ajudar uma pessoa a escolher o que examinar primeiro.')
end()

# 04
start('O que é um modelo de linguagem?','1 / Inteligência artificial sem mistério','Base: configurações e fundamentação do manuscrito [S4].')
para('Um modelo de linguagem aprende regularidades a partir de muitos exemplos de texto. Quando é especializado em código, também aprende padrões de programas. Depois do treinamento, usa números internos, chamados <b>parâmetros</b> ou <b>pesos</b>, para produzir respostas ou representações de uma entrada.')
para('LLM é a sigla em inglês para modelo de linguagem de grande porte. Isso não significa que o modelo seja uma pessoa lendo o código: ele calcula uma saída. Um texto convincente ou uma nota alta não garante que tenha identificado a falha correta.')
table(['Termo','Tradução prática no projeto'],[
 ['Qwen2.5-Coder','Família de modelos especializados em código utilizada nos experimentos.'],
 ['3B e 7B','Aproximadamente 3 e 7 bilhões de parâmetros. B significa bilhão.'],
 ['Base','Modelo usado como ponto de partida para o ajuste do classificador.'],
 ['Instruct','Variante preparada para seguir instruções textuais, usada nos testes YES/NO.'],
 ['Token','Unidade em que o texto é dividido para entrar no modelo; pode ser parte de uma palavra, símbolo ou outro trecho.'],
 ['Contexto','Quantidade de tokens que o modelo recebe naquela configuração.'],
 ],[115,WIDTH-115])
h2('Duas maneiras de fazer a mesma pergunta')
para('<b>Por instrução:</b> enviar uma pergunta e interpretar a palavra YES ou NO que o modelo escreve. <b>Por classificação:</b> acrescentar uma saída que calcula uma nota para as duas classes. A segunda opção permite variar o limite usado para dar o alarme.')
box('Modelo maior não é garantia','O 7B tem mais parâmetros que o 3B. Isso pode aumentar a capacidade e o custo, mas o desempenho depende da tarefa, dos dados e de como a avaliação é feita.')
end()

# 05
start('Como o projeto nasceu','1 / Da pergunta inicial ao recorte atual','Base: anteprojeto, dossiê v3 e protocolo [S1, S2].')
para('O anteprojeto do mestrado em Ciência da Computação do PPGCC UFMA foi organizado em torno desta pergunta: <b>quão pequeno e barato pode ser um modelo mantendo desempenho na detecção de vulnerabilidades?</b> A linha indicada nos documentos é Modelagem Computacional.')
para('A proposta combina três assuntos: detectar falhas de segurança, reduzir o custo dos modelos e avaliar com dados e regras mais rigorosos. O trabalho foi concebido como estudo empírico: executar experimentos, comparar resultados e produzir evidências, sem depender da invenção de um novo algoritmo.')
table(['Frente inicial','O que se pretendia investigar'],[
 ['1. Referências iniciais','Medir modelos sem especialização adicional para ter um ponto de comparação.'],
 ['2. Quantização','Usar menos bits e comparar métodos como NF4, AWQ e GPTQ.'],
 ['3. Ajuste eficiente','Especializar modelos pequenos com QLoRA e saída de classificação.'],
 ['4. Avaliação e robustez','Contrastar benchmarks e testar mudanças de código que preservam seu significado.'],
 ['5. Qualidade e custo','Relacionar desempenho, memória, tempo, dinheiro e, no plano amplo, energia.'],
 ],[118,WIDTH-118])
para('O dossiê v3 registra um acervo de 50 artigos, após revisar 41 e incorporar nove referências fundamentais. Essa é uma informação do histórico documental. O manuscrito atual de Seminários usa um conjunto menor, de 13 referências científicas verificadas para aquele texto.')
box('Por que o foco ficou mais específico?','Os resultados tornaram importante entender o que as métricas realmente medem. O artigo atual se concentra em Qwen2.5-Coder, PrimeVul, contraste global/pareado e duas implantações do 7B. O plano completo do mestrado é mais amplo.')
end()

# 06
start('Linha do tempo do trabalho','1 / O caminho percorrido','Base: histórico Git, notas de execução e registros editoriais [S3-S6]. Datas em horário local quando disponível.')
table(['Quando','O que os registros mostram'],[
 ['Antes e durante set/2026','Anteprojeto, revisão de literatura, versões do dossiê, protocolo, cronograma e organização das pastas.'],
 ['10/09/2026','Primeiro commit do repositório disponível: início do registro versionado. Isso não data o começo de todo o estudo.'],
 ['11-17/09','Montagem dos scripts, primeiros testes por instrução, avaliação pareada, ajustes de contexto e controle do ambiente.'],
 ['19/09','Decisão de migrar da v0.1 para a release original do PrimeVul; resultados anteriores foram arquivados.'],
 ['23-25/09','Reexecução das referências na release original e pilotos 3B: treino 1:1 e treino com proporção original.'],
 ['26-29/09','Investigação do tamanho da função e terceiro piloto 3B, com seleção de benignas de tamanho semelhante.'],
 ['04-06/10','Treino 7B com três sementes, avaliações NF4/BF16 e teste do terceiro braço 3B.'],
 ['06-07/10','Correção da pontuação de empates e alinhamento do F1 pelo limiar da validação.'],
 ['07-08/10','Plano do artigo, consolidação dos registros, estatística, inspeção de pares, redação e ciclos de revisão.'],
 ['Estado consultado em 09/10','Manuscrito completo, resultados consolidados e PDF SBC local. Há pendências editoriais e extensões experimentais.'],
 ],[103,WIDTH-103],size=10.5)
para('O histórico preserva decisões intermediárias e correções. Uma anotação antiga dizendo que algo estava pendente deve ser lida com sua data: os registros posteriores mostram que consolidação, recuperação dos dados e compilação local já avançaram.','small')
end()

# 07
start('Dataset: o material usado para ensinar e testar','2 / Entendendo os dados','Base: release original recuperada, esquema JSONL e scripts [S3, S5].')
para('<b>Dataset</b> significa conjunto de dados. Neste projeto, é uma coleção de funções de programas, acompanhadas de informações que permitem identificar cada exemplo e de um rótulo para a tarefa. Pense em um livro de exercícios com gabarito.')
para('O <b>rótulo</b> é a resposta usada como referência: <b>1 = vulnerável; 0 = não vulnerável segundo a rotulação do conjunto</b>. O zero não é uma prova universal de segurança. A qualidade da pesquisa depende também da qualidade desse gabarito.')
table(['Campo real','O que significa'],[
 ['func','O texto do corpo da função que entra no modelo.'],
 ['target','O rótulo 0 ou 1 usado para comparar com a predição.'],
 ['project','O projeto de origem, como Chrome ou Linux.'],
 ['commit_id','Identificação de uma versão ou mudança no histórico do projeto.'],
 ['idx e big_vul_idx','Identificadores presentes nos arquivos, úteis para rastreabilidade.'],
 ['cwe','Campo de categoria de fraqueza; pode estar vazio.'],
 ['hash','Campo fornecido no registro. Não substitui a conferência de identidade e posição realizada na consolidação.'],
 ],[113,WIDTH-113])
h2('Como esses dados ficam guardados?')
para('Os arquivos usam <b>JSONL</b>: cada linha contém um registro estruturado. Os scripts leem o código e o rótulo, e a consolidação usa também posição, identificador, projeto e commit para ligar cada previsão ao exemplo certo.')
box('O rótulo não deve entrar na pergunta','Durante a avaliação, o modelo recebe o código. O rótulo é usado depois, pelo avaliador, para conferir o resultado. Mostrar o gabarito ao modelo tornaria a avaliação inútil.')
end()

# 08
start('Por que o PrimeVul foi escolhido?','2 / Origem e qualidade do dataset','Base: manuscrito e fontes primárias nele verificadas [S4; R1, R2].')
para('O PrimeVul reúne funções C/C++ de projetos de código aberto. Seu trabalho de construção usa informações de correções de vulnerabilidades e busca melhorar a rotulação, remover duplicações e organizar a separação dos dados no tempo.')
para('Um <b>commit</b> é uma mudança registrada no histórico de um projeto. Um <b>patch</b> é o conjunto de alterações dessa mudança. Quando o patch corrige uma vulnerabilidade, é possível estudar a função antes e depois da correção. Essa associação exige cuidado: uma mudança pode alterar várias funções, e nem toda função alterada contém o defeito.')
h2('O problema de avaliar com exemplos repetidos')
para('Imagine estudar para uma prova e encontrar exatamente a mesma pergunta no teste. Você pode acertar porque reconheceu o exercício, sem conseguir resolver um novo problema. Em modelos, cópias ou exemplos muito semelhantes entre treino e teste podem produzir um efeito parecido: <b>vazamento de informação</b>.')
flow([('Deduplicar','Reduzir cópias ou repetições inadequadas.'),('Separar no tempo','Organizar treino e teste segundo o histórico.'),('Conferir rótulos','Melhorar a relação entre função e falha.')])
para('Esses cuidados atendem problemas diferentes. A rotulação busca um gabarito mais correto. Deduplicação e divisão cronológica reduzem algumas formas de vazamento. Nenhum deles, sozinho, garante que o teste seja perfeito.')
box('Uma correção importante da linguagem','Documentos antigos chamavam a avaliação de "descontaminada". A interpretação atual é mais precisa: o PrimeVul reduz riscos conhecidos, mas não prova ausência de contato com esse código no pré-treinamento do Qwen.')
para('A escolha do dataset faz parte do método científico: um teste rigoroso pode revelar limitações que uma avaliação mais fácil não mostraria.','small')
end()

# 09
start('Treino, validação e teste','2 / Três papéis diferentes','Base: contagens oficiais recuperadas e manuscrito [S4, S5].')
para('O conjunto principal é dividido em três partes. Elas têm papéis diferentes e não devem ser tratadas como se fossem uma única pilha de exercícios.')
table(['Partição','Funções','Vulneráveis','Não vulneráveis'],[
 ['Treino','184.427','5.574','178.853'],
 ['Validação','25.430','699','24.731'],
 ['Teste','25.911','695','25.216'],
 ['Total das três','235.768','6.968','228.800'],
 ],[133,108,111,WIDTH-352])
bullet('Treino:','é o material usado para atualizar os adaptadores e a cabeça do classificador. É o momento em que o modelo aprende com exemplos e gabaritos.')
bullet('Validação, ou dev:','serve para escolher a época e calibrar limiares de decisão. É como um simulado usado para ajustar a estratégia.')
bullet('Teste:','serve para descrever como a configuração escolhida se comporta em dados separados. O ideal confirmatório é definir as escolhas antes de consultá-lo.')
h2('O conjunto é desbalanceado')
para('No teste, apenas <b>695 de 25.911 funções, ou 2,68%, são vulneráveis</b>. As demais 97,32% têm rótulo não vulnerável. Isso significa que uma resposta "não" para tudo pareceria acertar muito, embora não encontrasse nenhuma falha.')
box('Como visualizar a proporção','Em cada 1.000 funções com essa proporção, seriam cerca de 27 vulneráveis e 973 não vulneráveis. É uma ilustração arredondada, não outro experimento.')
para('Neste projeto, o teste foi consultado durante o desenvolvimento das receitas. Por isso, o artigo atual chama a análise de <b>retrospectiva e exploratória</b>, mesmo que os limiares reportados tenham sido calibrados na validação.')
end()

# 10
start('O que é a avaliação pareada?','2 / Olhar antes e depois da correção','Base: partições pareadas e definições do manuscrito [S4, S5].')
para('Na avaliação global, cada função é julgada individualmente. Na avaliação <b>pareada</b>, a pergunta fica mais exigente: o modelo distingue uma função vulnerável da versão rotulada como sua correção?')
flow([('Antes','A função com rótulo vulnerável.'),('Depois','A função associada à correção.'),('Comparação','O alarme ou a nota muda na direção esperada?')])
para('As versões de um par compartilham muito código e contexto. Isso ajuda a investigar se a resposta acompanha a mudança relevante, em vez de acompanhar apenas o projeto, o estilo ou o tamanho da função. Mas o par precisa ter sido montado corretamente.')
table(['Partição pareada','Pares','Funções nos pares'],[
 ['Treino pareado','4.354','8.708'],
 ['Validação pareada','562','1.124'],
 ['Teste pareado','564','1.128'],
 ],[WIDTH-220,110,110])
box('564 pares não são 564 funções','Cada par tem dois membros. Por isso, 564 pares correspondem a 1.128 registros. O conjunto pareado é um recorte específico e não uma nova coleção a ser somada automaticamente às contagens do conjunto global.')
para('Também não há um par de teste para cada uma das 695 funções vulneráveis do teste global. São construções relacionadas, mas com denominadores diferentes. Comparar percentuais sem dizer qual conjunto foi usado pode confundir a leitura.')
para('Nos experimentos do projeto, as receitas de treino foram montadas a partir do treino global. Os pares de validação foram usados para escolher checkpoints; os pares de teste foram usados para avaliar as previsões.')
end()

# 11
start('A mudança de versão do dataset','2 / Uma decisão que protege a comparação','Base: downloader, README experimental, arquivo v01 e auditoria [S3, S5].')
para('O projeto começou usando a versão <b>PrimeVul-v0.1</b>. Depois, a conferência mostrou que ela era um subconjunto diferente da distribuição original do artigo. A v0.1 adiciona metadados, mas conserva apenas vulnerabilidades para as quais certos metadados foram recuperados.')
table(['Comparação','Release original','v0.1'],[
 ['Treino global','184.427 funções','175.797 funções'],
 ['Vulneráveis do treino','5.574','4.862'],
 ['Teste global','25.911 funções','24.788 funções'],
 ['Vulneráveis do teste','695','549'],
 ['Teste pareado','564 pares','435 pares'],
 ['Validação pareada','562 pares','480 pares'],
 ],[WIDTH-270,135,135])
para('Em 19/09, a decisão foi usar a <b>release original</b> como referência. As rodadas anteriores ficaram preservadas em <b>resultados/v01/</b>, e os testes principais foram refeitos na distribuição original. Portanto, seus números não devem ser misturados em uma mesma comparação sem identificação.')
h2('O que passou a ser conferido?')
para('Os scripts verificam os seis arquivos esperados e suas contagens por rótulo. Os registros de execução identificam a release. A consolidação posterior recuperou os arquivos oficiais, calculou hashes completos atuais e comparou os prefixos históricos disponíveis.')
box('Hash é uma impressão digital do arquivo','Ajuda a perceber se os bytes mudaram. Um hash conferido hoje não passa a ser um hash completo registrado no passado. E um arquivo idêntico à fonte oficial ainda pode conter rótulos ou correspondências problemáticas.')
para('A lição é simples: antes de comparar modelos, é preciso confirmar que todos responderam à mesma prova.','small')
end()

# 12
start('Como contar os acertos e os erros','3 / Métricas sem decorar fórmulas','Base: método do manuscrito [S4]. Exemplo numérico criado para ensino.')
para('O avaliador compara duas coisas: o rótulo de referência e o que o detector respondeu. Isso produz quatro situações. "Positivo" significa que o detector apontou uma vulnerabilidade.')
table(['O que existe no gabarito','O detector diz vulnerável','O detector diz não vulnerável'],[
 ['Vulnerável','<b>Verdadeiro positivo (VP)</b><br/>Encontrou a falha.','<b>Falso negativo (FN)</b><br/>Deixou a falha passar.'],
 ['Não vulnerável','<b>Falso positivo (FP)</b><br/>Deu um alarme falso.','<b>Verdadeiro negativo (VN)</b><br/>Não gerou alarme indevido.'],
 ],[143,178,WIDTH-321])
h2('Um exemplo para usar nas próximas páginas')
para('Considere uma coleção fictícia de 1.000 funções: 30 vulneráveis e 970 não vulneráveis. Um detector acha 12 das vulneráveis e dispara 48 alarmes falsos. Ele deixa passar as outras 18 vulneráveis e acerta 922 não vulneráveis.')
table(['VP','FN','FP','VN','Total'],[['12','18','48','922','1.000']])
para('A acurácia desse detector seria (12 + 922) / 1.000 = <b>93,4%</b>. Parece boa até perceber que um detector dizendo "não vulnerável" para tudo teria <b>97%</b> de acurácia nesse exemplo e encontraria zero vulnerabilidades.')
box('Por que acurácia sozinha engana aqui?','A classe não vulnerável domina a coleção. Acertar essa classe pode esconder o fracasso justamente na tarefa mais importante: encontrar as falhas.')
para('Essa é a razão de o projeto combinar métricas. Cada uma responde a uma pergunta diferente sobre utilidade, erros e esforço de revisão.')
end()

# 13
start('Precisão, revocação, F1 e falsos alarmes','3 / Quatro perguntas úteis','Base: definições usadas no manuscrito [S4]. Contas sobre o exemplo fictício da página 12.')
bullet('Precisão:','quando o detector dá um alarme, quantas vezes ele está certo? No exemplo: 12 acertos / 60 alarmes = <b>20%</b>. A cada cinco alarmes, só um corresponde a vulnerabilidade no gabarito.')
bullet('Revocação, ou recall:','de todas as vulnerabilidades, quantas foram encontradas? São 12 / 30 = <b>40%</b>. O detector encontra quatro de cada dez falhas.')
bullet('F1:','combina precisão e revocação pela média harmônica. Ele cai quando uma das duas é baixa. No exemplo: 2 × 0,20 × 0,40 / (0,20 + 0,40) = <b>0,267</b>, ou 26,7%.')
bullet('FPR:','entre as funções não vulneráveis, quantas receberam alarme falso? São 48 / 970 = <b>4,95%</b>. O denominador é o total não vulnerável, e não o total de alarmes.')
bullet('FNR:','entre as vulnerabilidades, quantas passaram despercebidas? São 18 / 30 = <b>60%</b>. É o complemento da revocação nesse conjunto.')
box('Precisão e FPR não são a mesma coisa','Precisão olha para a caixa de alarmes. FPR olha para todas as funções não vulneráveis. Quando há muitas funções não vulneráveis, mesmo uma FPR aparentemente pequena pode gerar muito trabalho.')
h2('Um exemplo com a dimensão real do teste')
para('Há 25.216 funções não vulneráveis no teste global do projeto. Uma FPR de 1% representaria aproximadamente 252 alarmes falsos; uma FPR de 0,5%, cerca de 126. Isso é uma conta ilustrativa sobre o tamanho do conjunto, não a medição de um detector específico.')
para('Nos resultados, F1 = 0,262 significa uma pontuação F1 de 26,2%. Não significa acertar 26,2% de todas as funções. A unidade e a definição importam tanto quanto o número.')
end()

# 14
start('Notas, limiares e AUC','3 / Entender a régua antes de comparar','Base: calibração e métricas do manuscrito [S4].')
para('Um classificador pode gerar uma <b>nota</b>, ou escore, em vez de apenas sim ou não. No projeto, ela é a diferença entre duas saídas numéricas, chamadas logits: saída vulnerável menos saída não vulnerável. Quanto maior a nota, maior a preferência relativa pela classe vulnerável. Ela não é, por si só, uma probabilidade calibrada.')
para('O <b>limiar</b> é o ponto a partir do qual o alarme é disparado. A regra usada é <b>nota &gt; limiar</b>. Mover o limiar muda quantos alarmes são dados. Um limiar alto costuma reduzir alarmes falsos, mas pode deixar mais falhas passar.')
table(['Limiar utilizado','Como foi escolhido','Para que serve'],[
 ['Maior F1','Buscar o maior F1 na validação global.','Calcular F1, precisão, revocação, FPR e categorias pareadas.'],
 ['Poucos falsos positivos','Limitar FPR a até 0,5% na validação global.','Observar FNR e FPR reais no teste, com a mesma regra.'],
 ],[118,184,WIDTH-302])
para('São <b>dois limiares diferentes</b>. Um valor de F1 e uma taxa de falhas perdidas em regime de poucos alarmes podem, portanto, descrever pontos de operação diferentes do mesmo modelo.')
h2('AUC: a qualidade da ordenação global')
para('A AUC ROC resume quanto os escores tendem a colocar funções vulneráveis acima de funções não vulneráveis no conjunto global. Uma referência sem discriminação tem AUC 0,5; uma separação perfeita tem 1. Ela não é uma taxa de acerto e não mostra sozinha quantos alarmes serão úteis em um limiar específico.')
box('Cuidado com o nome VD-Score','A medida local de FNR usa um limiar escolhido na validação e aplicado ao teste. O VD-Score oficial escolhe um ponto na própria curva do conjunto avaliado. O artigo atual diferencia os procedimentos e mostra a FPR efetiva do teste.')
end()

# 15
start('Duas medidas diferentes dentro dos pares','3 / Decidir corretamente ou ordenar as notas','Base: definições e revisão metodológica [S4, S5].')
para('Uma avaliação pareada pode olhar para as duas <b>decisões</b> ou para a <b>ordem das notas</b>. Essas medidas têm regras diferentes e não devem receber o mesmo nome.')
table(['Categoria','Vulnerável recebe','Corrigida recebe','Leitura'],[
 ['P-C','Vulnerável','Não vulnerável','As duas decisões corretas.'],
 ['P-V','Vulnerável','Vulnerável','Alarme nas duas versões.'],
 ['P-B','Não vulnerável','Não vulnerável','Nenhum alarme nas duas.'],
 ['P-R','Não vulnerável','Vulnerável','Decisões invertidas.'],
 ],[65,126,130,WIDTH-321],size=10)
para('As categorias dependem do limiar. Já a <b>ordenação pareada</b> pergunta se a versão vulnerável recebe nota maior que a corrigida. Se sim, o par vale 1; se as notas são iguais, vale 0,5; se a corrigida tem nota maior, vale 0. A média desses créditos é a pontuação reportada.')
box('Exemplo: ordenar certo sem acertar as duas decisões','Notas 0,8 e 0,7 colocam a vulnerável acima da corrigida. Mas, se o limiar for 0,5, as duas recebem alarme: categoria P-V. Ordenação favorável não garante P-C.')
para('Dar meio crédito aos empates mantém a referência de ordenação sem sinal em torno de <b>50%</b>, sob simetria entre as versões. Esse valor também pode ocorrer com todas as notas empatadas. Não é uma prova de compreensão ou de sua ausência.')
para('O antigo "25% de acaso" para P-C só vale para palpites binários independentes com 50% de chance de cada resposta. Não é uma referência universal para um detector que quase sempre diz não. E não é a referência da ordenação.')
para('A correção de empates foi incorporada ao código em outubro. A consolidação usa meio crédito e preserva as colunas históricas, sem fingir que a regra sempre foi essa.','small')
end()

# 16
start('A bancada de experimentos','4 / Como a pesquisa foi executada','Base: README do código, trava de versões e notas de reprodutibilidade [S3, S6].')
para('Para rodar os modelos, o projeto usou uma <b>GPU NVIDIA A40 de 48 GB</b>, alugada no RunPod. A GPU é um processador adequado a muitas operações numéricas em paralelo. Sua memória, frequentemente chamada de VRAM, precisa comportar pesos e dados temporários do processamento.')
para('Um <b>pod</b> é o ambiente de execução alugado. A rotina foi criar a máquina, instalar as versões previstas, baixar dados e modelo, executar, salvar resultados e preservar os artefatos antes de encerrar a sessão.')
table(['Peça da bancada','Papel'],[
 ['Python, PyTorch e Transformers','Executar scripts, operações numéricas e modelos.'],
 ['PEFT e bitsandbytes','Aplicar adaptação eficiente e carregar a base quantizada.'],
 ['Git e repositório','Registrar mudanças de código e documentos ao longo do tempo.'],
 ['CSV','Guardar tabelas de resultados e informações das execuções.'],
 ['Logs e receitas','Guardar previsões, decisões e configurações que explicam cada resultado.'],
 ['Trava de ambiente','Conferir versões e GPU para reduzir mudanças involuntárias.'],
 ],[168,WIDTH-168])
h2('Por que controlar o ambiente?')
para('Nos testes históricos da v0.1, trocar A40 por RTX A5000 mudou nove de 870 respostas mesmo com as demais escolhas iguais. Em outro teste, uma nova sessão A40 com o ambiente travado reproduziu 870 de 870 respostas. São observações específicas, que justificam controlar a comparação, sem garantir identidade em qualquer execução futura.')
box('Preço usado nos registros','US$ 0,50 por hora de A40. É um preço histórico utilizado para estimativas do projeto; não é uma consulta ao preço atual nem uma fatura real.')
end()

# 17
start('Primeiros resultados: perguntar YES ou NO','4 / Etapa 1 - referência por instrução','Base: quatro avaliações oficiais e tabelas consolidadas [S3-S5].')
para('Primeiro foi testado o caminho mais direto: enviar cada função aos modelos Qwen2.5-Coder-3B-Instruct e 7B-Instruct, sem exemplos, e pedir apenas YES ou NO. Esse uso é chamado <b>zero-shot prompting</b>: uma instrução sem exemplos adicionais de treino para aquela avaliação.')
para('As rodadas oficiais na release original usaram FP16, limite registrado de 8.192 tokens para o código e decodificação gulosa, sem sorteio da resposta. Um analisador transformou a primeira decisão reconhecida em 0 ou 1. Não houve resposta indefinida nas quatro avaliações consolidadas.')
table(['Modelo','F1','Precisão','Revocação','FPR'],[
 ['3B Instruct','0,119','0,102','0,144','3,49%'],
 ['7B Instruct','0,062','0,038','0,160','11,00%'],
 ],[145,78,84,96,WIDTH-403])
table(['No teste pareado','P-C','P-V','P-B','P-R'],[
 ['3B Instruct','16','67','463','18'],
 ['7B Instruct','14','78','454','18'],
 ],[145,88,88,88,WIDTH-409])
para('O 3B encontrou 100 das 695 funções vulneráveis no teste global. O 7B encontrou 111, mas gerou muito mais alarmes falsos: 2.774, contra 879 do 3B. Assim, seu pequeno aumento de revocação veio com uma forte queda de precisão.')
box('O que foi aprendido nessa etapa?','Na instrução utilizada, aumentar o tamanho de 3B para 7B não trouxe melhor F1. Nos pares, ambos acertaram as duas versões em poucos casos e quase sempre disseram não para as duas.')
para('Isso descreve os dois modelos e esse prompt. Não demonstra que todas as instruções, modelos ou formas de raciocínio teriam o mesmo resultado. Como as saídas eram palavras, essas rodadas não entram na ordenação contínua de escores.','small')
end()

# 18
start('Depois: especializar o modelo com QLoRA','4 / Etapa 3 - aprender com exemplos','Base: código, receitas e método do manuscrito [S3, S4; R3, R4].')
para('Perguntar a um modelo pronto é diferente de <b>ajustá-lo</b>. No ajuste fino, o sistema vê exemplos do treino e recebe uma indicação de quanto sua resposta está errada. O processo modifica componentes treináveis para melhorar a tarefa.')
para('Treinar todos os bilhões de parâmetros seria caro. A <b>LoRA</b> mantém a base congelada e aprende matrizes adicionais pequenas, chamadas adaptadores. A cabeça de classificação também aprende. Uma analogia é manter um livro e acrescentar anotações especializadas, em vez de reescrever todas as páginas.')
para('A <b>QLoRA</b> combina essa adaptação com a base armazenada em quatro bits. No projeto, a base usa NF4, dupla quantização e cálculo em BF16. O otimizador utilizado foi AdamW convencional; não foram usados os otimizadores paginados do artigo QLoRA.')
flow([('Base congelada','Qwen2.5-Coder Base em NF4.'),('Parte treinável','Adaptadores LoRA e cabeça de duas classes.'),('Saída','Uma nota para comparar com os limiares.')])
h2('Três palavras que aparecem nos registros')
bullet('Época:','uma passagem pelos exemplos de treino daquela receita. Três épocas significam rever aquele material três vezes.')
bullet('Perda, ou loss:','um número que indica o erro segundo a regra de aprendizado. Cair no treino é esperado; não basta para provar melhora em dados separados.')
bullet('Checkpoint:','versão salva do ajuste, por exemplo ao fim de uma época. A validação ajuda a escolher qual será avaliada.')
box('Ajuste eficiente não garante aceleração','Economizar memória durante o treino não garante inferência mais rápida. A velocidade também depende de operações, bibliotecas, GPU, lotes e da forma de implantar o adaptador.')
end()

# 19
start('O piloto 3B: três receitas de treino','4 / Escolher o que o modelo vai estudar','Base: receitas oficiais, notas históricas e tabela consolidada [S3-S5].')
para('Antes de gastar mais com o 7B, foram exploradas três formas de montar o material de treino do 3B. Todas mantiveram as 5.574 funções vulneráveis do treino original.')
table(['Receita','Não vulneráveis','Épocas','Treino','Custo da rodada'],[
 ['1:1 sorteado','5.574','3','3,37 h','US$ 1,85'],
 ['Proporção original','178.853','1','10,16 h','US$ 5,14'],
 ['1:1 + tamanho','5.574','3','4,98 h','US$ 2,65'],
 ],[132,104,55,78,WIDTH-369],size=10)
bullet('1:1 sorteado:','para cada vulnerável, usar uma não vulnerável sorteada. As classes ficam equilibradas: 11.148 funções por época.')
bullet('Proporção original:','usar as 184.427 funções do treino completo. Há aproximadamente 32 não vulneráveis para cada vulnerável.')
bullet('1:1 com controle de tamanho:','selecionar, sem reposição, uma não vulnerável cujo número de tokens visíveis seja próximo ao da vulnerável. A intenção é reduzir a informação que o comprimento fornece sobre a classe.')
h2('Por que não comparar apenas o custo total?')
para('Uma receita vê muito mais exemplos; outras repetem conjuntos menores por três épocas. O custo da tabela inclui o tempo total registrado da rodada, enquanto a coluna de horas indica treino. As receitas não tiveram orçamento de computação igual.')
box('Uma exploração, não um teste causal isolado','As configurações diferem em composição, volume de exemplos e duração. Compará-las mostra padrões úteis, mas não permite atribuir toda diferença a uma única mudança, como balanceamento ou tamanho.')
para('Cada receita 3B teve uma semente. O terceiro braço nasceu depois dos resultados dos dois primeiros, como investigação de uma possível característica superficial aprendida pelo modelo.')
end()

# 20
start('O achado que mudou a interpretação: tamanho','4 / Aprendizado por atalho','Base: baseline de comprimento e discussão atual [S4, S5]. Exemplo inventado para ensino.')
para('No conjunto global, funções vulneráveis tendem a ser mais longas que as não vulneráveis. Isso permite uma regra muito simples: atribuir maior nota às funções com mais tokens. Ela não precisa ler o significado do código.')
para('O projeto mediu exatamente essa referência, chamada <b>heurística de comprimento</b> ou baseline de tamanho. Seu escore é o número de tokens visíveis após o corte em 2.048 tokens. O limiar de maior F1 foi escolhido na validação, como nos classificadores.')
box('Resultado real da heurística','No teste global: F1 = <b>0,200</b> e AUC = <b>0,810</b>. Nos 564 pares: ordenação = <b>21,10%</b>, dando meio crédito aos empates. A mesma regra parece útil em uma avaliação e desfavorável na outra.')
h2('Como isso pode acontecer?')
para('Considere uma função fictícia com 100 tokens e uma falha de limite. A correção acrescenta uma verificação e passa a ter 110 tokens. Uma regra "mais longo = mais vulnerável" dá nota maior à versão corrigida. Ela segue uma correlação do conjunto global, mas erra a direção da mudança relevante.')
table(['Exemplo fictício','Antes','Depois'],[
 ['Rótulo de referência','Vulnerável','Corrigida'],
 ['Comprimento','100 tokens','110 tokens'],
 ['Nota da heurística','100','110'],
 ['Efeito','A versão vulnerável fica abaixo','A versão corrigida parece mais suspeita'],
 ],[183,145,WIDTH-328])
para('Isso é <b>aprendizado por atalho</b>: usar uma pista correlacionada à resposta em vez da propriedade que se deseja medir. Os resultados são compatíveis com essa preocupação; o estudo não identificou de forma causal tudo o que os modelos aprenderam.')
para('Até uma regra invertida de comprimento pode parecer favorável nos pares. Por isso, ordenar bem também não prova compreensão de segurança.','small')
end()

# 21
start('O controle de tamanho e a chegada ao 7B','4 / Do piloto às três sementes','Base: receitas, seleção de épocas e análise atual [S3-S5].')
para('O terceiro piloto procurou evitar que a classe pudesse ser reconhecida só pelo comprimento. Para cada vulnerável, foi escolhida uma não vulnerável com tamanho tokenizado próximo, limitado a 2.048 tokens. O número de exemplos permaneceu 1:1.')
para('A ideia é comparável a ensinar alguém a reconhecer frutas sem deixar que todas as maçãs sejam grandes e todas as laranjas pequenas. Ao equilibrar o tamanho, essa pista deixa de resolver a tarefa no treino. Outras pistas ainda podem existir.')
h2('Como foi escolhida a época?')
para('Historicamente, a escolha usou a <b>ordenação estrita</b> dos 562 pares de validação, contando empates como erro, e a AUC de uma amostra de validação como desempate. A correção posterior deu meio crédito aos empates. Nos quatro treinos com controle de tamanho, foi possível refazer essa verificação: as épocas selecionadas não mudaram.')
para('Nos pilotos 3B 1:1 e proporção original, os empates por época não foram registrados. Os checkpoints históricos foram mantidos. Na proporção original só houve uma época, portanto não existia outra época a escolher.')
table(['Configuração com controle de tamanho','Semente','Época selecionada'],[
 ['3B','1','3'],['7B','1','3'],['7B','2','2'],['7B','3','3'],
 ],[WIDTH-220,100,120])
box('Por que repetir com sementes diferentes?','A semente controla sorteios do treinamento, como inicialização e ordem dos exemplos. Treinar com sementes 1, 2 e 3 ajuda a enxergar variação. Não cria três novos conjuntos de teste.')
para('O 7B repetiu a receita 1:1 com controle de tamanho por até três épocas. Cada treino levou cerca de 7,9 horas. Em seguida, o checkpoint selecionado de cada semente foi avaliado nas duas implantações, NF4 e BF16.')
end()

# 22
start('O que os resultados principais mostram?','5 / Ler o global junto com o pareado','Base: tabelas 3 e 4 da consolidação [S5]. Todos os F1 abaixo usam limiar da validação.')
table(['Configuração','F1 global','AUC global','Ordenação pareada'],[
 ['Só comprimento','0,200','0,810','21,10%'],
 ['3B 1:1 sorteado','0,195','0,795','42,38%'],
 ['3B proporção original','0,262','0,851','37,50%'],
 ['3B 1:1 + tamanho','0,121','0,746','49,20%'],
 ['7B NF4 - média de 3','0,128','0,743','50,62%'],
 ],[177,84,91,WIDTH-352])
para('A linha do 7B resume as três sementes e está arredondada. A ordenação usa 564 pares e meio crédito nos empates. Prompting não aparece nesta tabela porque gera decisões, não os escores contínuos usados aqui.','small')
h2('Ordenação pareada: onde a comparação muda')
bars([('Só comprimento',21.10,MUTED),('3B proporção original',37.50,RED),('3B 1:1 sorteado',42.38,RED),('3B 1:1 + tamanho',49.20,TEAL),('7B NF4 - média',50.62,TEAL)],ref=50)
para('A marca dourada indica 50%, referência de ordenação sem preferência por uma versão. O gráfico descreve estimativas; a incerteza do 7B está na página seguinte.','small')
box('A principal lição dos experimentos','O melhor F1 global entre essas configurações, 0,262, veio do 3B com proporção original. Mas sua ordenação pareada ficou em 37,50%. Ter a melhor métrica global não significou distinguir melhor a função da sua correção.')
para('O controle de tamanho acompanhou pontuações globais menores e ordenação próxima de 50%. Esse padrão merece investigação, mas as receitas diferentes não permitem concluir que a mudança de tamanho foi a única causa.')
end()

# 23
start('Por que uma única semente não basta?','5 / Variação e incerteza no 7B','Base: tabela 6, intervalos e comparação alinhada [S5].')
table(['Semente 7B','NF4 - ordenação','BF16 - ordenação'],[
 ['1','55,23%','53,28%'],['2','45,04%','44,68%'],['3','51,60%','51,95%'],
 ['Média','50,62%','49,97%'],
 ],[WIDTH-280,140,140])
para('Olhar só para a semente 1 poderia sugerir um resultado favorável; olhar só para a 2 sugeriria o oposto. O desvio padrão entre as três sementes foi de <b>5,17 pontos percentuais em NF4</b> e <b>4,63 em BF16</b>. São apenas três treinamentos, portanto a caracterização da variação continua limitada.')
h2('O que é o intervalo de incerteza?')
para('A consolidação repetiu a conta em 10.000 reamostragens dos grupos de pares. Esse procedimento é chamado <b>bootstrap</b>. A unidade sorteada foi projeto/commit: 550 grupos contêm os 564 pares, e todos os pares de um grupo permanecem juntos.')
table(['Medida','Estimativa','Intervalo de 95%'],[
 ['NF4','50,62%','47,92% a 53,33%'],
 ['BF16','49,97%','47,14% a 52,73%'],
 ['Diferença NF4 - BF16','0,65 p.p.','-1,22 a 2,54 p.p.'],
 ],[182,98,WIDTH-280])
box('A leitura correta','Os intervalos são condicionais aos três modelos observados. Incluem 50% nas médias e diferenças nos dois sentidos entre implantações. Isso não prova acaso nem equivalência, e não prevê com precisão novos treinamentos.')
para('As três sementes responderam aos mesmos 564 pares: não temos 1.692 pares independentes. O bootstrap manteve o alinhamento entre sementes e implantações. Commits do mesmo projeto ainda podem ser dependentes; nenhum teste de hipótese foi realizado nessa consolidação.','small')
end()

# 24
start('Quantização: memória e tempo não andam juntos','5 / As duas implantações do 7B','Base: tabelas de recursos e método [S4, S5].')
para('Quantizar é armazenar os pesos com uma representação numérica mais compacta. <b>NF4</b> é uma representação de quatro bits; <b>BF16</b> usa 16 bits. Menos bits pode economizar memória, mas o resultado real depende também da forma como o cálculo é executado.')
para('Cada checkpoint 7B foi avaliado de duas maneiras: <b>base NF4 com adaptador separado</b> e <b>base BF16 com adaptador mesclado</b>. Mesclar significa incorporar a atualização LoRA aos pesos. As duas configurações mudam quantização e mesclagem ao mesmo tempo.')
table(['Recurso','NF4 + adaptador','BF16 mesclado'],[
 ['Memória após carga','4,63 GB','14,15 GB'],
 ['Pico de memória registrado','12,49 GB','20,76 GB'],
 ['Tempo por função no teste','59,6-60,0 ms','46,8-47,1 ms'],
 ['Custo estimado do teste','US$ 0,2145-0,2160','US$ 0,1684-0,1696'],
 ],[199,150,WIDTH-349])
box('Resultado observado nesse ambiente','NF4 usou cerca de <b>67% menos memória após a carga</b> e <b>40% menos no pico</b>. Porém, o tempo amortizado por função foi cerca de 28% maior. BF16 foi aproximadamente 22% mais rápido em tempo por função.')
para('O teste usou A40, Transformers, contexto de 2.048 tokens e lotes de até 32.768 tokens. O tempo é o total de pontuação do teste dividido pelo número de funções; não é a espera de uma chamada individual. O pico foi medido na pontuação de validação, teste e pares, podendo não incluir a mesclagem.')
para('As diferenças de ordenação não foram distinguíveis nos intervalos reportados. Isso compara duas implantações completas, sem isolar o efeito da quantização. Também não certifica economia de energia, faturamento real ou desempenho em outra GPU.')
end()

# 25
start('E se só pudermos aceitar poucos alarmes falsos?','5 / Um teste de utilidade prática','Base: FNR* e FPR* das tabelas consolidadas [S5].')
para('Um detector pode ser difícil de usar se encher a caixa de revisão com alarmes falsos. O projeto também avaliou um ponto mais restritivo: escolher um limiar que permita FPR de até <b>0,5% na validação</b> e aplicá-lo ao teste sem reajuste.')
table(['Configuração','Vulnerabilidades perdidas no teste (FNR)','Alarmes falsos no teste (FPR)'],[
 ['Só comprimento','100,00%','0,00%'],
 ['3B 1:1 sorteado','94,10%','0,54%'],
 ['3B proporção original','88,06%','0,65%'],
 ['3B 1:1 + tamanho','96,26%','0,63%'],
 ['7B NF4 semente 1','97,99%','0,69%'],
 ['7B NF4 semente 2','98,71%','0,38%'],
 ['7B NF4 semente 3','98,27%','0,56%'],
 ],[181,164,WIDTH-345])
para('Nesse ponto, a configuração 3B com proporção original perdeu aproximadamente 88 de cada 100 vulnerabilidades. O 7B perdeu cerca de 98 de cada 100. A redução de alarmes veio com uma grande perda de sensibilidade.')
box('O limite da validação não é garantia no teste','O limiar fica fixo, mas a distribuição dos escores muda entre conjuntos. Por isso, várias linhas ultrapassaram 0,5% de FPR no teste. O artigo mostra o valor efetivo, em vez de afirmar que a restrição foi atendida em todas as configurações.')
para('No baseline de comprimento, o limiar restritivo coincidiu com o teto de 2.048 tokens. Como a decisão exige nota estritamente maior, nenhuma função disparou alarme: FPR zero e FNR 100%. É uma consequência dessa combinação de corte e regra, não uma incapacidade universal de toda heurística de tamanho.')
end()

# 26
start('Consolidar: transformar registros em evidência','5 / O trabalho de conferência em outubro','Base: implementação, manifesto, auditoria e suplemento [S5].')
para('Depois das execuções, o projeto tinha tabelas, logs e receitas espalhados no histórico. A consolidação de 08/10 reuniu essas fontes para conferir identidades, refazer métricas e produzir tabelas e análises rastreáveis.')
table(['Material coberto','Quantidade','Papel'],[
 ['Avaliações','14','Quatro por instrução, nove de classificadores e uma heurística.'],
 ['Arquivos de previsão','33','Quatro de prompting, 27 dos classificadores e dois do tamanho.'],
 ['Receitas de treinamento','6','Três receitas 3B e três sementes 7B já existentes.'],
 ['Arquivos do dataset','6','Treino, validação e teste, globais e pareados.'],
 ],[174,81,WIDTH-255])
para('Um mesmo classificador produz arquivos para validação, teste e pareado; por isso, número de avaliações e número de logs não são iguais. A conferência alinhou cada previsão à posição, ao identificador, ao projeto, ao commit e ao rótulo da fonte oficial.')
h2('Por que a identidade importa?')
para('Se o log de uma função for ligado ao rótulo de outra, a métrica fica errada mesmo que a fórmula esteja certa. Alguns membros corrigidos são reutilizados na release oficial; por isso, juntar apenas pelo identificador poderia multiplicar ou perder registros. A consolidação preservou as posições oficiais.')
box('O que a conferência conseguiu e o que não conseguiu','As métricas principais reproduziram a precisão publicada, sem divergências numéricas registradas. Mas os escores salvos têm cinco casas decimais: não é possível recuperar uma precisão interna que nunca foi gravada.')
para('Foram implementados inventário, reconstrução das métricas, bootstrap e exportação. Oito testes científicos passaram. Essa consolidação foi em CPU, sem novo treinamento, sem inferência dos modelos e sem uso de RunPod.')
end()

# 27
start('Conferir também os pares e o corte do código','5 / Sensibilidades e problemas encontrados','Base: auditoria de pares, tokenização e tabelas de sensibilidade [S4, S5].')
para('<b>Truncamento</b> é cortar a entrada quando ela ultrapassa o limite. Os classificadores receberam até 2.048 tokens do início da função. Se a correção está depois desse ponto, a diferença relevante pode ficar invisível.')
para('Dos 564 pares de teste, <b>465 cabem integralmente</b> nesse limite. Em 32 pares, as duas sequências de entrada ficam idênticas depois do corte. As avaliações 7B tiveram de 32 a 40 empates de nota; score igual sozinho não prova entrada idêntica, pois também há arredondamento e outras possibilidades.')
h2('Uma inspeção focalizada de correspondência')
para('Foram examinados 15 pares com diferença de cabeçalho ou assinatura. A consulta aos arquivos do commit e do seu pai confirmou <b>cinco casos em que o membro rotulado como corrigido é outra função</b>. Eles pertencem a libjpeg, PHP, rizin, Linux e drogon.')
table(['Recorte da análise','Pares','Para que serve'],[
 ['Principal oficial','564','Manter a referência do benchmark.'],
 ['Sem truncamento','465','Verificar o resultado quando o código cabe integralmente.'],
 ['Sem as cinco correspondências inadequadas','559','Medir a influência desses casos específicos.'],
 ['Interseção dos dois controles','460','Aplicar ambos os recortes ao mesmo tempo.'],
 ],[217,53,WIDTH-270])
box('Esses cinco casos explicam o resultado?','Nas seis avaliações 7B, removê-los mudou a ordenação em no máximo 0,22 ponto percentual. O padrão geral permaneceu. Isso não certifica os demais 559 pares nem estima a frequência do problema em todo o PrimeVul.')
para('Os recortes são retrospectivos e mudam a composição da amostra. Não substituem o conjunto principal. Também não foi trocada uma função por outra sem previsão histórica disponível.')
end()

# 28
start('O que podemos concluir com responsabilidade','6 / Significado e limites da pesquisa','Base: discussão e limitações do manuscrito atual [S4].')
table(['Evidência observada','Conclusão que ela sustenta'],[
 ['Comprimento: AUC 0,810 e ordenação 21,10%.','Uma característica superficial pode separar classes globalmente e ordenar os pares na direção desfavorável.'],
 ['Melhor F1 global: 0,262; ordenação 37,50%.','O melhor resultado global desta comparação não identificou melhor as duas versões da correção.'],
 ['7B: médias de ordenação próximas de 50% e variação entre sementes.','Uma única execução pode sugerir uma história incompleta; os intervalos não provam acaso nem equivalência.'],
 ['NF4: menos memória, mais tempo amortizado.','Nesse ambiente, as duas implantações trocaram memória por tempo.'],
 ],[218,WIDTH-218])
h2('Os limites que acompanham essas conclusões')
para('<b>Desenho:</b> o estudo é exploratório e retrospectivo; houve consulta ao teste durante o desenvolvimento. As receitas não têm o mesmo volume nem o mesmo orçamento. Base/Instruct e contextos também diferem entre etapas.')
para('<b>Amostra:</b> há uma semente por receita 3B e três no 7B; os pares não são completamente independentes. A inspeção semântica dos rótulos não foi completa, e o corte de entrada esconde parte do código.')
para('<b>Generalização:</b> os resultados se referem a uma família de modelos, um dataset, uma GPU e uma biblioteca. Não permitem afirmar que todo LLM falha, que todo ajuste é inútil ou que quatro bits sempre mantêm a qualidade.')
box('O valor científico do trabalho','Ele torna visível a diferença entre obter bons indicadores em uma coleção e discriminar uma falha da sua correção. A contribuição atual é uma caracterização documentada, com medidas de recursos e limites explícitos.')
end()

# 29
start('O que está pronto e o que continua aberto','6 / Estado do projeto em 09/10/2026','Base: README atual, consolidação e registros de fechamento [S5, S6].')
table(['Estado','Bloco do projeto'],[
 ['Realizado','Anteprojeto, dossiês, protocolo, cronograma e organização do repositório.'],
 ['Realizado','Referências por prompting 3B/7B na release original; heurística de comprimento.'],
 ['Realizado','Três receitas 3B e treino 7B com três sementes; avaliações NF4/BF16 do 7B.'],
 ['Realizado','Recuperação da release, conferência das previsões, métricas, bootstrap e sensibilidades.'],
 ['Realizado','Manuscrito completo de Seminários, revisões editoriais, bibliografia e suplemento.'],
 ['Visualização disponível','Compilação local do manuscrito SBC em PDF de 15 páginas, com inspeção registrada.'],
 ['Pendente para entrega','Autoria e afiliação completas, regras de extensão e ajuste do comprimento dos resumos.'],
 ['Sem execução demonstrada neste bloco','Comparação AWQ/GPTQ/INT8, outras famílias e UniXcoder; energia, motor vLLM, robustez por transformações e contraste controlado com benchmarks legados.'],
 ],[137,WIDTH-137],size=10.3)
para('A prévia interna de LaTeX do Codex permaneceu com falha de ambiente, mas uma compilação local posterior com MiKTeX gerou o PDF. Os fechamentos anteriores preservam o estado antigo; o README atual registra a atualização.')
box('Revisão do texto não é conclusão do mestrado','O artigo teve ciclos de redação e conferência com Codex e Claude, com registros preservados. Aprovação editorial não é defesa acadêmica, submissão aceita ou validação independente de todos os dados. A apresentação e a submissão não constam como realizadas.')
para('Os planos do artigo indicam 11/11/2026 como data-alvo de Seminários. Isso é uma data planejada nos documentos, não confirmação das regras atuais da disciplina.','small')
end()

# 30
start('Como continuar a pesquisa a partir daqui','6 / Próximos passos com base no que foi aprendido','Base: conclusão do manuscrito e distinção entre recorte atual e plano amplo [S2, S4, S6].')
para('Os próximos passos têm dois níveis: terminar a entrega do artigo atual e desenhar novas evidências para o projeto mais amplo. Eles não precisam ser confundidos.')
h2('Para terminar o artigo de Seminários')
bullet('Fechar identificação e formato:','completar autoria e afiliação, confirmar limite de páginas e ajustar resumos e apresentação às regras da disciplina ou do veículo.')
bullet('Preservar a rastreabilidade:','manter tabelas, fontes, suplemento, receitas, scripts e versões ligados ao manuscrito final. Uma nova revisão deve identificar qual versão dos resultados utiliza.')
h2('Para fortalecer a evidência experimental')
bullet('Definir uma avaliação confirmatória:','fixar receitas, critérios e limiares antes de consultar um novo teste. Isso reduz a influência das observações usadas para desenvolver as escolhas.')
bullet('Ampliar repetições e comparabilidade:','usar mais sementes e controlar o orçamento de treino quando a pergunta for sobre composição do dataset ou escala do modelo.')
bullet('Revisar correspondências e contexto:','examinar de forma sistemática os pares e planejar como tratar código que não cabe no limite de entrada.')
bullet('Separar efeitos de implantação:','por exemplo, incluir BF16 com adaptador separado para distinguir mesclagem de quantização; repetir medições de recursos e latência individual.')
box('Para retomar o plano amplo do mestrado','AWQ, GPTQ, INT8, outras famílias, UniXcoder, energia e robustez continuam como possibilidades do planejamento. Sua prioridade e viabilidade devem ser ajustadas à pergunta de pesquisa, à orientação e aos recursos disponíveis.')
para('A decisão mais útil agora é escolher qual pergunta precisa de nova evidência. Acrescentar mais experimentos sem uma pergunta clara pode aumentar o custo sem melhorar a conclusão.')
end()

# 31
start('Glossário para consultar durante a leitura','6 / Tradução dos termos principais')
table(['Termo','Significado neste guia'],[
 ['Ajuste fino','Treinamento adicional para adaptar um modelo a uma tarefa.'],
 ['Adaptador LoRA','Matrizes pequenas treináveis acrescentadas a uma base congelada.'],
 ['AUC ROC','Resumo da discriminação global dos escores ao variar limiares. Não é acurácia.'],
 ['Baseline','Referência de comparação: um modelo inicial ou uma regra simples.'],
 ['Benchmark','Dados e regras usados para comparar métodos de avaliação.'],
 ['BF16 / FP16','Duas representações numéricas diferentes de 16 bits.'],
 ['Bootstrap','Recalcular uma estatística em amostras sorteadas a partir dos registros observados.'],
 ['Cabeça de classificação','Saída treinável que transforma a representação do código em notas para classes.'],
 ['Checkpoint','Estado salvo de um modelo ou adaptador em determinado momento.'],
 ['Commit / patch','Uma mudança registrada / as alterações dessa mudança no código.'],
 ['Dataset / split','Conjunto de dados / uma partição, como treino ou teste.'],
 ['Época / loss','Uma passagem pelo treino / a medida de erro usada no aprendizado.'],
 ['F1 / precisão / recall','Equilíbrio entre precisão e recall / acerto entre alarmes / falhas encontradas.'],
 ['FPR / FNR','Alarmes falsos entre não vulneráveis / falhas perdidas entre vulneráveis.'],
 ['Inferência','Usar o modelo para produzir uma saída, sem atualizar seus parâmetros.'],
 ['Limiar / score','Limite da decisão / nota que será comparada a esse limite.'],
 ['NF4 / quantização','Formato de quatro bits / representação numérica mais compacta.'],
 ['Seed / semente','Número que controla os sorteios de uma execução de treinamento.'],
 ['Token / truncamento','Unidade da entrada / corte da entrada que excede o limite.'],
 ['VRAM / pico','Memória da GPU / maior alocação observada na janela de medição.'],
 ],[127,WIDTH-127],size=10)
end()

# 32
start('Onde encontrar cada parte no projeto','6 / Um mapa dos arquivos','Base: organização atual das pastas e README do código [S3, S6]. Caminhos relativos à raiz do projeto.')
table(['Pasta','O que ela guarda'],[
 ['01_planejamento/','Anteprojeto, dossiês, protocolo e planos do artigo.'],
 ['02_referencias/','Artigos, extrações de texto, inventários e conferências de fontes.'],
 ['03_experimentos/codigo/','Scripts históricos e o bloco novo consolidacao_artigo/.'],
 ['03_experimentos/dados/','Dataset e materiais recuperados; artefatos grandes ficam fora do Git.'],
 ['03_experimentos/resultados/','CSVs históricos, arquivo v01/ e resultados derivados do artigo.'],
 ['03_experimentos/logs/','Previsões e registros das execuções, incluindo material descartado identificado.'],
 ['04_escrita/artigo/seminarios_2026/','Texto atual, bibliografia, LaTeX, suplemento e histórico editorial.'],
 ['05_reunioes/','Materiais de reunião e consultas registradas sobre escrita e decisões.'],
 ],[222,WIDTH-222],size=10)
h2('O papel dos scripts, em ordem lógica')
para('<b>00 e 02:</b> baixar/conferir e inspecionar os dados. <b>01 e ambiente.py:</b> preparar e conferir o ambiente. <b>03 e 04:</b> gerar decisões por instrução e contar categorias pareadas. <b>05:</b> comparar logs. <b>06:</b> treinar adaptadores. <b>07:</b> avaliar classificadores. <b>08:</b> medir a heurística de comprimento.')
para('No diretório <b>consolidacao_artigo/</b>, os módulos 01-04 inventariam, reconstroem métricas, calculam estatística e exportam tabelas/figura. Eles trabalham sobre registros existentes, sem precisar repetir inferência ou treinamento.')
box('Quando houver versões diferentes','Para os resultados atuais, usar a pasta consolidacao_2026-10-08 e o manuscrito artigo_completo.md. Dossiês, planos, notas e revisões antigos continuam úteis como história, mas podem descrever um estado anterior.')
end()

# 33
start('Fontes deste relato','6 / Como conferir a explicação','Este guia foi elaborado a partir dos arquivos disponíveis na pasta compartilhada, sem novos experimentos com modelos.')
para('A explicação prioriza resultados consolidados e o manuscrito atual. Os caminhos abaixo são relativos a <b>D:/UFMA UNIVERSIDADE/MESTRADO - ESTUDO LLM/</b>. Referências [S1]-[S9] identificam documentos do próprio projeto.','small')
entries=[
 ('S1','Origem do projeto','01_planejamento/Projeto_Mestrado_Deteccao_Vulnerabilidade_Eficiente (1).pdf','Anteprojeto, objetivos e escopo amplo.'),
 ('S2','Planejamento revisado','01_planejamento/RECORTE_A_dossie_completo_v3.md; RECORTE_A_protocolo_experimental.md','Evolução das perguntas, literatura e matriz planejada.'),
 ('S3','Execução histórica','03_experimentos/codigo/README.md; 00_baixar_primevul.py; requisitos_travados.txt; resultados/NOTAS_etapa1.md; NOTAS_etapa3.md','Scripts, versões, receitas, resultados e decisões datadas.'),
 ('S4','Síntese científica atual','04_escrita/artigo/seminarios_2026/texto/artigo_completo.md','Método, resultados, interpretação, limitações e referências.'),
 ('S5','Evidência consolidada','03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08/','Tabelas, métricas, manifesto, auditoria, intervalos e sensibilidades. Implementação em codigo/consolidacao_artigo/IMPLEMENTACAO_2026-10-08.md.'),
 ('S6','Estado editorial atual','04_escrita/artigo/seminarios_2026/README.md; revisao/reescrita_opus_extra_2026-10-08/FECHAMENTO.md','Texto, revisões, PDF local e pendências. O README inclui atualizações posteriores ao fechamento.'),
 ('S7','Suplemento atual','04_escrita/artigo/seminarios_2026/revisao/reescrita_opus_extra_2026-10-08/07_previa_v003/SUPLEMENTO.md','Detalhes metodológicos e fontes documentais de inspeção.'),
 ('S8','Dados recuperados','03_experimentos/dados/artigo_seminarios_2026/release_original/','Seis JSONL usados para conferir esquema, contagens e identidade.'),
 ('S9','Histórico versionado','Histórico Git local, desde o commit db3b15a de 10/09/2026','Datas e sequência das alterações rastreadas; parte do trabalho recente ainda está fora dos commits.'),
]
for key,title,path,usage in entries:
    para(f'<b>[{key}] {title}.</b> {html.escape(path)}<br/><font color="#5C6D79">{usage}</font>','small',gap=11)
end()

# 34
start('Para lembrar e para aprofundar','6 / A história completa em poucas ideias','Referências científicas abaixo constam das fontes verificadas no manuscrito atual [S4].')
para('O projeto começou com uma pergunta de eficiência. Montou uma bancada, conferiu dados e modelos, corrigiu a escolha da release e mediu uma referência por instrução. Depois, especializou classificadores, investigou o tamanho da função e ampliou o estudo para três sementes do 7B.')
para('A consolidação mostrou por que a avaliação precisa de várias lentes. A coleção global pode premiar uma característica superficial, enquanto o par vulnerável/corrigida revela outro comportamento. A implantação compacta também pode poupar memória e consumir mais tempo. As conclusões atuais descrevem essas configurações, com seus limites.')
box('Você entendeu o projeto se conseguir explicar...','Por que dizer "não" para tudo parece acertar muito; por que 564 pares são 1.128 registros; por que AUC não é acurácia; por que ordenar as versões não garante duas decisões corretas; e por que quatro bits não significam automaticamente mais velocidade.')
h2('Seis leituras para aprofundar')
refs=[
 ('R1','Ding et al. (2024)','Vulnerability Detection with Code Language Models: How Far Are We?','https://arxiv.org/abs/2403.18624','Origem do PrimeVul e avaliação.'),
 ('R2','Risse e Böhme (2024)','Uncovering the Limits of Machine Learning for Automatic Vulnerability Detection','https://www.usenix.org/conference/usenixsecurity24/presentation/risse','Limites dos detectores e pares.'),
 ('R3','Hu et al. (2021)','LoRA: Low-Rank Adaptation of Large Language Models','https://arxiv.org/abs/2106.09685','Adaptação com poucos parâmetros.'),
 ('R4','Dettmers et al. (2023)','QLoRA: Efficient Finetuning of Quantized LLMs','https://arxiv.org/abs/2305.14314','Ajuste sobre base quantizada.'),
 ('R5','Hui et al. (2024)','Qwen2.5-Coder Technical Report','https://arxiv.org/abs/2409.12186','Família de modelos utilizada.'),
 ('R6','Huang et al. (2026)','Do Fine-Tuned LLMs Understand Vulnerabilities? An Investigation into the Semantic Trap','https://arxiv.org/abs/2601.22655','Contrastes de avaliação em código.'),
]
for key,author,title,url,desc in refs:
    para(f'<b>[{key}] {author}.</b> <link href="{url}" color="#087E86">{title}</link>. {desc}','small',gap=9)
para('Os links remetem às obras identificadas nos registros locais. Este guia não realiza uma revisão sistemática nova nem certifica novidade científica. Seu objetivo é ensinar o caminho percorrido pelo projeto e permitir que os resultados sejam lidos com clareza.','small')
end()

c.save()
(TMP/'paginas_guia.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':page_no,'min_content_y':min(p.get('lowest_content_y',10000) for p in pages)},ensure_ascii=False))
