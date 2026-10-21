# Análise do corpus de referência da escrita

Data-base: 07/10/2026. Identificadores e hashes: `inventario_fontes.json`. Páginas abaixo são as páginas físicas do PDF, contadas a partir de 1; não necessariamente coincidem com paginação impressa. Esta análise distingue observações dos textos e escolhas editoriais para o novo estudo.

As localizações seguem marcadores gerados na extração; a conferência visual foi parcial: primeiras páginas de todos os artigos e páginas internas selecionadas de A01/A08/A12. As demais passagens foram examinadas em texto extraído, não certificadas visualmente. Para A12, conferir também `textos_extraidos/A12_colunas.txt`, além da extração linear e do PDF original.

## 1. Inventário de leitura

| ID | Arquivo original | Tema/título de identificação | Páginas |
|---|---|---|---:|
| A01 | `16064-673-12774-1-10-20210707.pdf` | Detecção de glaucoma usando redes em cápsula | 12 |
| A02 | `16071-673-12781-1-10-20210707.pdf` | Nódulos da tireoide em termografia; CNNs em cascata | 12 |
| A03 | `16074-673-12784-1-10-20210707.pdf` | Esteatose hepática não alcoólica; imagens térmicas | 11 |
| A04 | `2016_art_jafdemendonca.pdf` | Redes neurais na otimização de placas laminadas | 16 |
| A05 | `21638-673-17578-1-10-20220908.pdf` | PPM-UNet; segmentação de rins em TC | 9 |
| A06 | `25300-673-20775-1-10-20230728.pdf` | Câncer peniano; imagens histopatológicas e CNNs em cascata | 12 |
| A07 | `3679-673-3654-5094-2-20180816.pdf` | Glaucoma; variantes de padrões locais binários | 11 |
| A08 | `41242-1658-33598-1-10-20260323.pdf` | Verificação de fatos; DistilBERT e FEVER | 10 |
| A09 | `6246-673-5511-1-10-20190605.pdf` | Vértebras/fraturas; U-Net 3D e Deep Belief Network | 12 |
| A10 | `6258-673-5523-1-10-20190605.pdf` | Paralisia do sexto nervo; vídeos, CNN e curvatura Isophotes | 12 |
| A11 | `6273-673-5538-1-10-20190605.pdf` | Meta-aprendizagem de extração de características; glaucoma | 6 |
| A12 | `6470-25971-1-PB.pdf` | Glaucoma; índices taxonômicos e aprendizado de máquina | 10 |

Anselmo aparece como coautor no corpus; o texto publicado não permite atribuir cada passagem a ele individualmente. A01–A03 e A05–A11 compartilham apresentação semelhante ao SBC de uma coluna; A04 é de CILAMCE, e A12 tem duas colunas e referências numéricas. Os formatos de A04/A12 não serão transferidos para a diagramação do novo artigo.

## 2. Traços observados e localização

| Dimensão | Observação | Exemplos verificáveis |
|---|---|---|
| Introdução | Contextualização do problema, necessidade prática, limites das abordagens e objetivo progressivamente delimitado | A01 pp.1–2; A02 pp.1–3; A06 pp.1–2; A08 pp.1–2 |
| Objetivo | Sujeito como trabalho/pesquisa seguido de avaliar, apresentar, investigar ou propor; formulações variam | A01 p.2; A07 p.2; A08 p.2; A11 p.2; A12 p.2 |
| Retomada entre parágrafos | Demonstrativo com substantivo que recupera a ideia anterior; a referência costuma ter objeto identificável | A08 pp.2,5,7; A06 pp.2,5 |
| Método | Visão geral seguida do detalhamento de etapas, dados, parâmetros, ambiente e finalidade das escolhas | A01 p.4; A02 pp.3–7; A03 p.4; A05 pp.2–3; A09 pp.4–5; A10 p.5 |
| Verbos de execução | Passiva analítica e construções com se no pretérito, alternadas com descrição técnica no presente | A01 pp.4–7; A06 pp.5–7; A07 pp.3–7; A08 pp.3–5 |
| Pessoa e voz | Impessoalidade frequente; primeira pessoa plural também existe em decisões, propostas e interpretações | A08 pp.3,8–9; A09 pp.9–10; A11 pp.2,4–5 |
| Conexões lógicas | Finalidade, sequência, oposição, consequência e acréscimo são expressas por conectivos e pelo próprio encadeamento | A01 pp.2,8–9; A02 pp.7–9; A06 pp.6–7; A08 pp.2,5–7 |
| Referências | Autor integrado à frase e referência ao fim da proposição; convenções gráficas variam por veículo | A01 p.2; A08 pp.1–2; A12 p.2 |
| Tabelas e figuras | Chamada textual, descrição de contraste ou etapa e interpretação ligada ao objetivo | A01 pp.8–9; A06 pp.6–8; A08 pp.7–8; A11 p.4 |
| Resultados | Número, condição e explicação do contraste; algumas passagens apoiam escolha de próxima etapa | A06 pp.6–7; A08 pp.7–8; A10 pp.8–9 |
| Cautela e limites | Há modalidades de hipótese e reconhecimento de amostras/protocolos limitados, mas o grau de cautela não é uniforme | A01 p.9; A07 p.9; A09 pp.9–10; A10 pp.9–10 |
| Conclusão | Retomada do trabalho realizado, achados centrais e continuidade; tamanho e organização variam | A01 p.10; A04 p.14; A05 pp.7–8; A07 p.10; A11 p.5; A12 pp.8–9 |

As localizações orientam conferência, não constituem certificação da qualidade científica desses estudos. Erros de extração devem ser resolvidos no PDF antes de transcrever uma passagem.

## 3. Escolha das referências mais próximas

A08 é a referência mais próxima pela área de PLN, pelo estudo de um Transformer e pela descrição de dados/configurações. A01 e A06 ajudam a observar encadeamento de procedimentos, tabelas e interpretação. A09/A10 contribuem para a explicitação de limites e a continuidade do trabalho. A04 p.14 e a seção de resultados preliminares de A11 pp.4–5 ilustram relatos de pesquisas em desenvolvimento. Essa observação não assegura que um texto preliminar satisfaça requisitos de qualquer disciplina/veículo ou valide sua generalização.

Essa ponderação não exclui os demais textos, nem declara que o artigo mais próximo tenha o melhor rigor. O novo estudo deverá preservar suas próprias definições de métricas, seeds, limiares e implantação.

## 4. Adaptações necessárias

O corpus contém termos de valorização, como promissor, eficiente ou superior, e interpretações que nem sempre explicitam todas as condições. Eles não serão transportados automaticamente. Tampouco serão reproduzidas conclusões de equivalência por dispersão, explicações causais sem desenho apropriado ou comparações diretas entre protocolos distintos.

Adotar a progressão acadêmica e a explicação de decisões, com cautela determinada pela evidência deste projeto. Modalizar uma frase não basta para tornar uma causalidade demonstrada: o texto deve identificar hipótese, confundidores e limites.

Não instituir regras ausentes no corpus: proibição geral de passiva, gerúndio ou primeira pessoa plural; número fixo de frases; conectivo obrigatório a cada parágrafo; objetivo sempre na mesma fórmula; ordem única de seções. A decisão para nosso manuscrito é uma adaptação explicitamente registrada no [guia editorial](../../04_escrita/artigo/seminarios_2026/PADRAO_ESCRITA.md).
