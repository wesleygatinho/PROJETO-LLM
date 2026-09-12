# Guia de partida — o que falta para começar a rodar

Escrito em linguagem simples, de propósito. Sem alterar o cronograma.

---

## 1. A notícia boa: não falta ideia, falta bancada

Tudo o que é "pensamento" já está pronto: o que você vai pesquisar, por quê, como medir,
quais modelos, quais dados, em que ordem. Isso está nos documentos de planejamento.

O que falta é **material**, não ideia. É como ter a receita pronta e ainda não ter a cozinha
montada. O que falta se resume a:

1. uma conta com crédito no RunPod (a "cozinha" alugada);
2. o conjunto de dados baixado (os "ingredientes");
3. um modelo pequeno baixado (a "panela");
4. um script simples que faz o modelo responder sim/não e conta os acertos (a "receita executada");
5. uma planilha onde você anota cada resultado.

Quando esses 5 itens existirem, você **já começou a pesquisa**. O resto do cronograma
é repetir isso mudando uma coisa de cada vez.

---

## 2. Checklist do que precisa existir antes do primeiro experimento

Marque conforme for fazendo.

**Contas e acesso**
- [ ] Conta no **RunPod** com algum crédito (comece com pouco, ex.: US$ 20–30; o primeiro objetivo é só fazer funcionar).
- [ ] Conta no **Hugging Face** (é de onde se baixam os modelos e o dataset) e um *token* de acesso criado nas configurações.
- [ ] Conta no **GitHub** (você já tem o repositório local; suba ele para não perder nada).

**Dados**
- [ ] Baixar o **PrimeVul** (está no GitHub do projeto DLVulDet/PrimeVul e no Hugging Face).
- [ ] Abrir um arquivo dele e entender o formato: cada linha é uma função de código com um rótulo (0 = sem falha, 1 = com falha). Existe também a versão "pareada": a função com falha e a mesma função já corrigida, lado a lado.
- [ ] Localizar os arquivos de **treino / validação / teste**. No começo você usa **só o teste**.

**Modelo**
- [ ] Escolher um modelo **pequeno** para começar (ex.: Qwen2.5-Coder-1.5B-Instruct ou 3B-Instruct). Pequeno = baixa rápido, roda barato, erro aparece cedo. O de 7B fica para depois que tudo funcionar.

**Código (um script só, no começo)**
- [ ] Carregar o modelo na GPU.
- [ ] Para cada função do teste: montar o texto da pergunta ("esta função tem vulnerabilidade? responda SIM ou NÃO") + o código.
- [ ] Pegar a resposta do modelo e transformar em 0 ou 1 (essa parte, o "parsing", dá mais trabalho do que parece: o modelo às vezes responde "Sim, porque..." em vez de só "SIM").
- [ ] Comparar com o rótulo verdadeiro e calcular acertos: precisão, revocação, F1, taxa de falsos positivos (o scikit-learn faz isso em uma linha cada).
- [ ] Gravar tudo num CSV.

**Planilha de resultados** (crie antes de rodar, com estas colunas)
`data | modelo | tamanho | precisão (16/8/4 bits) | método de quantização | prompt (versão) | seed | nº de funções | F1 | precisão | revocação | FPR | memória GPU (GB) | tempo por função (s) | GPU usada | preço/hora | custo total (US$) | observações`

**Medir custo (pode ser simples no início)**
- [ ] Memória: `torch.cuda.max_memory_allocated()` no fim da rodada.
- [ ] Tempo: relógio antes e depois do laço.
- [ ] Dinheiro: preço por hora do pod × tempo que ficou ligado.
- [ ] Energia: fica para depois (pynvml/nvidia-smi); não trave nisso agora.

---

## 3. Glossário — os termos do cronograma em português simples

| Termo que aparece | O que significa, na prática |
|---|---|
| **Bancada / harness** | O conjunto "ambiente + dados + script + planilha" funcionando. É a cozinha montada. |
| **Baseline / ponto de referência** | O resultado do modelo **sem mexer em nada** (tamanho original, sem treino extra). É o número contra o qual você compara tudo depois. |
| **Etapa 1** | Montar a bancada e obter o baseline. É só isso. |
| **16 bits / 8 bits / 4 bits** | Quantos bits o modelo usa para guardar cada número dos seus "pesos". Menos bits = ocupa menos memória e roda mais rápido, mas pode errar um pouco mais. 16 é o "normal"; 4 é o "bem encolhido". |
| **Quantizar / quantização** | O ato de encolher o modelo reescrevendo os números com menos bits. |
| **NF4, AWQ, GPTQ** | Três **jeitos diferentes** de quantizar (de encolher). O trabalho compara qual deles perde menos qualidade. |
| **QLoRA** | Uma forma barata de **treinar** o modelo para a sua tarefa sem retreinar ele inteiro: você congela o modelo grande e treina só uma "pecinha" pequena por cima. |
| **Cabeça de classificação** | Em vez de o modelo escrever texto, você coloca nele uma saída que dá direto uma nota "vulnerável ou não". É mais limpo de medir. |
| **Prompting / prompt** | Só perguntar ao modelo por texto, sem treinar. É o que a Etapa 1 faz. |
| **Avaliação pareada** | Testar o modelo na função **com falha** e na **mesma função corrigida**. Se ele diz "vulnerável" para as duas, não entendeu nada. |
| **VD-S** | Uma medida que responde: "se eu só aceitar no máximo 0,5% de alarmes falsos, quantas falhas reais o modelo deixa passar?" Quanto menor, melhor. Só faz sentido quando o modelo dá uma nota (não só sim/não). |
| **F1** | Uma média entre "acertou as que apontou" (precisão) e "achou as que existiam" (revocação). Resume qualidade em um número. |
| **FPR (taxa de falsos positivos)** | De todo código **sem** falha, quanto o modelo marcou errado como "com falha". Alarme falso. |
| **Seed** | Um número que fixa o "sorteio" interno do treino. Rodar com 3 seeds = repetir 3 vezes para ver se o resultado é estável, não sorte. |
| **Contaminação** | Quando o teste tem código que também estava no treino. O modelo "decora" e parece melhor do que é. Por isso usamos o PrimeVul, que é limpo. |
| **PTQ** | Quantizar **depois** que o modelo já está treinado (sem treinar de novo). AWQ e GPTQ são PTQ. |
| **Merge (mesclar)** | Depois de treinar a "pecinha" do QLoRA, grudar ela de volta no modelo para ficar um modelo só. |
| **Curva custo × qualidade** | Um gráfico: eixo X = quanto custa (memória/tempo/dinheiro), eixo Y = qualidade. Serve para achar o ponto em que você paga pouco e ainda tem qualidade boa. |
| **Núcleo mínimo (NMV)** | O menor conjunto de experimentos que ainda rende uma dissertação. O resto é bônus. |

Se aparecer outro termo que trave, anote aqui e a gente explica.

---

## 4. Como organizar as pastas

Proposta (já criei as pastas vazias; **não movi nenhum arquivo seu**):

```
MESTRADO - ESTUDO LLM/
├── 01_planejamento/      ← os documentos de plano (dossiê v3, protocolo, cronograma, análise, log, guia, slides)
├── 02_referencias/       ← (suas pastas "pdfs das referencias" e "pdf_to_markdown" já cumprem esse papel; pode deixar como estão)
├── 03_experimentos/
│   ├── codigo/           ← os scripts (inferencia.py, avaliacao.py, ...)
│   ├── dados/            ← PrimeVul baixado (NÃO vai para o Git: é grande)
│   ├── resultados/       ← os CSVs/planilhas de resultado
│   └── logs/             ← saídas de execução, erros, prints
├── 04_escrita/
│   ├── qualificacao/
│   ├── dissertacao/
│   └── artigo/
└── 05_reunioes/          ← anotações de cada conversa com o orientador (data, decisões, próximos passos)
```

O que fazer com o que já existe:
- Os `.md` de planejamento que estão na raiz podem ir para `01_planejamento/` quando quiser (arraste e solte). Deixei na raiz para não quebrar nada agora.
- `RECORTE_A_dossie_completo.md` (v1) e `_v2.md` são versões antigas: mantenha só por histórico ou apague — a **v3** é a que vale.
- O PDF `Projeto_Mestrado_...pdf` é o projeto original; guarde em `01_planejamento/`.
- Criei um `.gitignore` na raiz para o Git **não** subir dados grandes, modelos e a pasta `dados/`.

---

## 5. Como organizar as ideias (um arquivo, um papel)

Você tem 5 documentos e cada um responde a uma pergunta diferente. Quando bater a confusão, é só saber qual abrir:

| Pergunta que você está se fazendo | Abra |
|---|---|
| "O que é o meu trabalho e por quê?" | `RECORTE_A_dossie_completo_v3.md` |
| "Como exatamente eu vou medir e comparar?" | `RECORTE_A_protocolo_experimental.md` |
| "Quando faço cada coisa?" | `RECORTE_A_cronograma.md` |
| "Esse número que eu cito está certo? De onde veio?" | `ANALISE_CRITICA_RECORTE_A.md` + `LEITURA_INTEGRAL_LOG.md` |
| "Por onde eu começo, na prática?" | este guia |
| "O que eu falo para o orientador?" | `RECORTE_A_apresentacao.tex` |

Regra simples: **não abra tudo ao mesmo tempo**. Nas próximas semanas, só o guia e o protocolo importam.

---

## 6. A sua primeira sessão no RunPod (o que vai acontecer, em ordem)

Não é para fazer hoje — é para você visualizar que é curto:

1. Criar um pod com **1 GPU de 24 GB** (ex.: RTX 4090) e o template de PyTorch.
2. Abrir o terminal do pod e instalar: `transformers`, `datasets`, `scikit-learn`, `pandas`, `accelerate`.
3. Fazer login no Hugging Face com o seu token.
4. Baixar o PrimeVul e o modelo pequeno.
5. Rodar o script em **50 funções**.
6. Anotar na planilha: F1, precisão, revocação, FPR, memória, tempo, custo.
7. **Desligar o pod** (para não gastar crédito à toa).

Se no fim disso existir uma linha preenchida na planilha, a pesquisa começou.
Quando você quiser, eu escrevo o script dessa primeira sessão pronto para colar.
