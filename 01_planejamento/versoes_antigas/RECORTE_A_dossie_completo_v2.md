# RECORTE A — Dossiê Completo (v2 — revisado contra as fontes)

**Detecção eficiente de vulnerabilidades em código por modelos de linguagem: quantização e ajuste fino eficiente sob avaliação descontaminada**

Registro consolidado do Recorte A (projeto de mestrado, PPGCC UFMA). Esta é a **versão 2**, revisada frase a frase contra os 41 artigos-fonte em markdown (ver `ANALISE_CRITICA_RECORTE_A.md`). Toda afirmação numérica central foi conferida na fonte primária.

Data da revisão: setembro de 2026.

---

## Registro de revisões (o que mudou da v1 para a v2)

Mudanças substantivas em relação à versão original (cada uma detalhada e justificada em `ANALISE_CRITICA_RECORTE_A.md`):

1. **Vul-RAG:** "16 a 24% relativos" → **"16 a 24 pontos percentuais absolutos"** de acurácia pareada (erro fatual corrigido).
2. **Avatar (Shi et al.):** deixa de ser "[preprint] 2023" e passa a **"[revisado por pares], ICSE-SEIS 2024"**.
3. **Semantic Trap:** removidos os exemplos não presentes na fonte ("gestão de memória, protocolos de rede"); descrito pelo mecanismo real (padrão funcional; V2P vs V2N; gap CodeBLEU).
4. **JITVUL:** removida a atribuição não confirmada "construído sobre o PrimeVul"; descrito como benchmark pareado JIT sobre 879 CVEs.
5. **QLoRA em dados desbalanceados:** removida a afirmação de que "a F1 do QLoRA por classificação despenca" — não é testada por Ouchebara (que balanceou os dados); reclassificada como lacuna a investigar.
6. **Autoria adicionada** a 5 referências antes listadas só por título (Al Atiiq; Huang; Kaniewski/Schmidt/Heer; Gao, S. [TREAT]; Niu, C. [TokenPowerBench]).
7. **VD-S:** esclarecido que exige score contínuo/probabilidade e, portanto, pertence às etapas com **cabeça de classificação** — não ao baseline de *prompting* da Etapa 1.
8. **Regimes de quantização:** separação explícita entre *weight-only* (NF4/AWQ/GPTQ — núcleo do projeto) e *weight+activation* (W4A4/W8A8 — Wu/SmoothQuant).
9. **DeepSeek-Coder-V2:** registrada a natureza MoE (16B total / 2,4B ativos) e a implicação de memória para a seleção de modelos.
10. **Enquadramento estratégico:** o cenário de "reenquadramento eficiência×qualidade" passa de plano B a **cenário-base**, à luz da convergência dos preprints de 2026.
11. Correções menores de nomes de arquivo/ano no corpus (AWQ = 2024; SmoothQuant = 2023).

---

## Índice

1. Visão geral e definição
2. Contexto acadêmico
3. O problema explicado em linguagem simples
4. Metodologia (cinco etapas)
5. Etapa 1 detalhada (roteiro de execução)
6. Cronograma
7. Revisão de literatura (estado da arte 2024 a 2026)
8. Lacunas de pesquisa
9. Roteiro recomendado em três estágios
10. Metodologia de medição de eficiência
11. Ferramentas e frameworks
12. Referências consultadas
13. Ressalvas importantes

---

## 1. Visão geral e definição

**Pergunta central:** para detectar vulnerabilidade em código, quão pequeno e barato dá para deixar o modelo sem perder qualidade?

**O que é:** dissertação de mestrado em Ciência da Computação (PPGCC UFMA). É um trabalho de método mais avaliação: além de medir, especializa modelos pequenos via ajuste fino eficiente (QLoRA) para a tarefa e verifica se isso fecha a diferença para modelos grandes, sob avaliação descontaminada.

**Natureza da contribuição:** não é inventar um algoritmo novo. É um estudo empírico sistemático mais uma recomendação prática, com um gancho científico forte (a contaminação dos benchmarks tradicionais). Estudo de avaliação e caracterização — tipo aceito e de baixo risco. **A originalidade concentra-se no eixo ainda não coberto pela literatura: efeito do *método* de quantização sobre a *classificação* de vulnerabilidade, sob avaliação descontaminada** (ver §8).

**Duas perguntas de pesquisa norteadoras:**
- Um modelo pequeno especializado por QLoRA recupera o desempenho de um modelo maior?
- Qual método de quantização preserva melhor a qualidade na detecção?

**Nota de calibração (à luz da literatura de 2026):** a evidência recente (Kaniewski 2026; Huang et al. 2026; Gao, S. et al./TREAT 2025) sugere que, sob avaliação **pareada descontaminada**, quase todos os modelos ficam perto do acaso e o QLoRA provavelmente **não** fecha a lacuna de qualidade. Por isso, a contribuição robusta e de baixo risco é a **caracterização de custo para uma qualidade reconhecidamente limitada** — assumida aqui como cenário-base, não como contingência (ver §9).

---

## 2. Contexto acadêmico

- **Programa:** PPGCC UFMA, mestrado em Ciência da Computação. Duas linhas: Arquitetura de Sistemas Computacionais e Modelagem Computacional. Este trabalho se encaixa em **Modelagem Computacional** (reconhecimento de padrões e aprendizado de máquina). Verificar o Lattes do possível orientador, pois o recorte é fortemente puxado pela linha de quem orienta.
- **Recursos computacionais:** GPUs alugadas sob demanda (RunPod).
- **Funil do mestrado:** estudo dirigido (levantamento e delimitação) → qualificação → dissertação.
- **Relação com o TCC (Recorte B):** o autor conduz um TCC de Engenharia da Computação em tema correlato mas distinto (avaliação de eficiência na geração de código). Compartilham fundamentação e infraestrutura, mas têm tarefa, método e contribuição próprios. Recomenda-se transparência com as duas orientações.

---

## 3. O problema explicado em linguagem simples

**A tarefa.** Detecção de vulnerabilidade aqui é classificação: dá-se ao modelo uma função (um pedaço de código) e ele responde se tem vulnerabilidade ou não (ou qual tipo). Não é gerar código, é julgar código. A avaliação fica limpa e barata (compara a resposta com o rótulo verdadeiro), diferente de geração, onde é preciso rodar testes.

**As duas alavancas de eficiência.**
- **Quantização.** Um modelo guarda seus pesos em 16 bits por padrão. Quantizar é reescrever esses números com menos bits (8 ou 4), reduzindo muito a memória de GPU e acelerando a inferência, com alguma perda possível de qualidade. Há vários métodos (AWQ, GPTQ, GGUF, bitsandbytes/NF4) que perdem quantidades diferentes. **Distinção importante:** o núcleo deste projeto é quantização *weight-only* (só os pesos em 4 bits; ativações em 16 bits — regime W4A16), que é bem mais branda que a quantização *weight+activation* (W4A4).
- **QLoRA.** Forma barata de ajustar um modelo pequeno para ficar especialista numa tarefa, sem retreinar o modelo inteiro. Hipótese a testar: um modelo pequeno especializado por QLoRA alcança um modelo grande e genérico?

**O gancho científico.** Muitos resultados publicados usam benchmarks contaminados (dados repetidos entre treino e teste), o que superestima o desempenho. Contrastar um benchmark antigo com um limpo evidencia isso. **Ressalva de originalidade:** essa demonstração já está bem estabelecida na literatura (PrimeVul, e confirmada por Kaniewski, Huang et al. e TREAT); no Recorte A ela é **confirmatória/pedagógica**, não a contribuição principal.

---

## 4. Metodologia (cinco etapas)

1. **Reproduzir baselines.** Pegar dois ou três modelos pequenos abertos em versão Instruct (por exemplo StarCoder2-7B, Qwen2.5-Coder-7B, DeepSeek-Coder 6.7B) e um codificador de referência (UniXcoder, 125M), rodar em precisão cheia (16 bits) sobre o conjunto depurado e pareado (PrimeVul), anotando qualidade. Serve para aprender o harness e ter o ponto de referência.
2. **Ligar a quantização.** Rodar os mesmos modelos em 8 e 4 bits, com diferentes métodos *weight-only* (AWQ, GPTQ, NF4, GGUF), anotando qualidade e custo (memória, latência, energia).
3. **Ligar o QLoRA.** Especializar os modelos pequenos com **cabeça de classificação** na partição de treino e reavaliar, comparando modelo pequeno especializado contra modelo maior não especializado.
4. **Mostrar o efeito da contaminação.** Rodar o mesmo modelo num benchmark antigo (Devign ou Big-Vul) e num limpo (PrimeVul), evidenciando a queda no limpo. Incluir teste de robustez a perturbações que preservam a semântica.
5. **Montar as curvas de trade-off.** Cruzar qualidade e custo, achar o joelho da curva e escrever a recomendação prática.

**Métricas de qualidade (dado desbalanceado, F1 sozinho engana):** F1 da classe vulnerável, **VD-S** (taxa de falsos negativos sob taxa de falsos positivos ≤ 0,5%), **acurácia pareada** (o modelo distingue a função vulnerável da sua versão corrigida?) e taxa de falsos positivos. **Nota metodológica:** VD-S e a curva ROC exigem um score contínuo/probabilidade — logo só se aplicam aos caminhos com **cabeça de classificação** (Etapas 3+), não ao baseline de *prompting* sim/não da Etapa 1. Nesta, reportar F1/precisão/revocação/FPR.

**Métricas de custo:** memória de GPU (pico), latência (primeiro token e por token), vazão (tokens por segundo), energia e valor por hora da instância.

**Decisão-chave de desenho:** usar **cabeça de classificação, não geração**. A evidência mostra que classificação supera a formulação por geração nesta tarefa (Ouchebara & Dupont 2025) e que tarefas de compreensão toleram melhor a quantização do que a geração autorregressiva (Wu et al. 2023 — com a ressalva de que o resultado "robusto" de Wu é para arquitetura *encoder* sob W4A4; ver §7.4).

---

## 5. Etapa 1 detalhada (roteiro de execução)

Objetivo: montar a bancada e ter um número de referência confiável.

Decisão que molda tudo: na Etapa 1 usa-se **prompt** (mostra a função e pede sim/não), sem treino. Treinar para classificar entra só na Etapa 3 (QLoRA). Para prompt funcionar, usar as versões **Instruct** dos modelos.

Passos:
1. **Subir o ambiente.** No RunPod, subir um pod com uma GPU (24 GB roda os 7B **densos** em 16 bits; atenção: DeepSeek-Coder-V2-Lite é MoE de 16B **totais** e não cabe em 24 GB em 16 bits — usar o DeepSeek-Coder 6.7B denso para paridade). Instalar Python, PyTorch e Transformers, baixar o primeiro modelo. Começar pelo menor (3B) para depurar rápido.
2. **Pegar e entender o dataset.** Baixar o PrimeVul (o limpo, principal). Abrir os dados: cada item é uma função com um rótulo; há pares de função vulnerável e corrigida; localizar a divisão treino/validação/teste (temporal). Na Etapa 1 usa-se só o teste.
3. **Escrever o laço de inferência.** Para cada função do teste, montar o prompt (instrução fixa mais o código), enviar ao modelo, ler a resposta e converter para decisão. A parte trabalhosa é o *parsing* robusto da resposta.
4. **Escrever a avaliação.** Com predições e rótulos, calcular F1, precisão, revocação e acurácia (scikit-learn). F1 da classe vulnerável é a métrica principal desta etapa (VD-S entra a partir da Etapa 3).
5. **Rodar por modelo e anotar tudo.** Registrar qualidade (F1, precisão, revocação, FPR) e custo básico (memória, tempo por predição, valor por hora).
6. **Conferir a bancada.** Comparar com números de artigos que usaram os mesmos modelos e datasets (p.ex. StarCoder2-7B no PrimeVul ≈ F1 baixíssimo, ordem de 3%). Diferença absurda indica bug no prompt ou no parsing.

Dicas: temperatura 0 (determinístico); começar com ~50 funções; registrar modelo/precisão/prompt junto de cada número; **rodar ≥3 seeds e reportar intervalos de confiança** (diferencial em relação aos preprints de split único). Pronto da etapa: uma tabela com F1 e custo de dois ou três modelos em 16 bits no PrimeVul, confiável.

---

## 6. Cronograma

Ciclo aproximado de vinte e quatro meses, ajustável ao calendário do PPGCC.

| Fase | Atividades | Meses |
|---|---|---|
| Estudo dirigido | Revisão do estado da arte, definição das métricas descontaminadas, montagem do arcabouço e reprodução de baselines (Etapa 1) | 1 a 6 |
| Consolidação | Quantização (Etapa 2), início do QLoRA com cabeça de classificação (Etapa 3) e estudo de contaminação (Etapa 4) | 6 a 12 |
| Qualificação | Redação e defesa da qualificação com fundamentação, problema e resultados preliminares | 12 a 15 |
| Dissertação | Conclusão da Etapa 3, análise de trade-off (Etapa 5), redação e submissão de artigo | 15 a 24 |

O TCC (Recorte B) roda em paralelo e fecha antes, reaproveitando o mesmo harness e datasets.

---

## 7. Revisão de literatura (estado da arte 2024 a 2026)

### 7.1. Formulação, taxonomia e evolução

O problema é formulado em quatro granularidades: classificação binária de função, classificação por tipo de fraqueza (CWE), detecção em nível de linha ou instrução (localização) e detecção em nível de repositório (raciocínio inter-procedural).

Evolução das abordagens: redes neurais em grafo (Devign, Zhou et al. 2019); modelos pré-treinados codificadores (CodeBERT, Feng et al. 2020; GraphCodeBERT, Guo et al. 2021; UniXcoder, Guo et al. 2022); e LLMs de código (Qwen2.5-Coder, StarCoder2, DeepSeek-Coder, CodeLlama, Granite Code). Observação recorrente: codificadores totalmente ajustados permanecem baselines fortes — em particular o **UniXcoder**, que só é empatado (não superado) por LLMs muito maiores ajustados sob avaliação descontaminada (PrimeVul, Ding et al. 2024; Ouchebara & Dupont 2025). Métodos SOTA e modelos pré-treinados costumam superar LLMs na detecção em avaliações multitarefa (Yin et al. 2024, sobre Big-Vul).

Boa parte dos modelos de código de ponta vem de laboratórios asiáticos (Alibaba/Qwen, DeepSeek), e datasets/benchmarks importantes (MegaVul, ReposVul, Vul-RAG, TREAT) têm autores em instituições chinesas — reflexo do peso real da pesquisa asiática na área. Contrapesos ocidentais fortes estão igualmente presentes (PrimeVul, IRIS, SecLLMHolmes, QLoRA, GPTQ, AWQ, LoRA, Avatar, vLLM). A qualidade deve ser julgada por **venue e revisão por pares**, não por origem geográfica.

### 7.2. LLMs para detecção de vulnerabilidade

**Técnicas empregadas:** prompting sem/poucos exemplos, raciocínio em cadeia, ajuste fino supervisionado, sistemas multi-agente, recuperação aumentada por conhecimento (RAG) e abordagens neuro-simbólicas (LLM mais análise estática).

**O que funciona melhor:**
- **IRIS** (neuro-simbólico; Li, Dutta & Naik, ICLR 2025): acopla um LLM à análise estática (CodeQL). Em CWE-Bench-Java (120 vulnerabilidades em Java), o CodeQL sozinho detecta 27; o IRIS com GPT-4 detecta **55** e reduz a taxa média de falsas descobertas em ~5 pontos (de 90,03% para 84,82%); com modelo aberto de 7B (DeepSeek-Coder) detecta **52**; descobriu **4** vulnerabilidades antes desconhecidas. Ressalva: mesmo assim a AvgF1 é baixa (0,177) e o AvgFDR permanece ~85% — "detecta mais, com muito ruído".
- **Vul-RAG** (recuperação de conhecimento; Du et al. 2024/2025): eleva a acurácia pareada em **16 a 24 pontos percentuais absolutos** (p.ex. GPT-4o de 0,08 para 0,32; benchmark próprio PairVul, 586 pares do Linux kernel). Porém, um estudo de reprodutibilidade (**Kaniewski, Schmidt & Heer, 2026**) observou um **platô em torno de 0,30 de acurácia pareada** com modelos abertos, pouco acima do acaso (0,25), com um modelo de **4B igualando um de 30B** — a escala isolada não ajuda.

**O que falha:**
- **Fragilidade / não-robustez:** modelos avançados mudam de resposta diante de renomeações de função ou variável (erro em ~26% dos casos) e de adição de funções de biblioteca (~17%), com respostas não-determinísticas e raciocínio infiel (Ullah et al., SecLLMHolmes, IEEE S&P 2024; 228 cenários, C e Python).
- **Desempenho baixo em condições realistas:** em nível de instrução, o melhor modelo (Claude-3.7-Sonnet) atinge só ~**24% de F1** (23,83%) com raciocínio correto (SecVulEval, Ahmed et al. 2025; 25.440 funções, 5.867 CVEs). Em avaliações multitarefa, métodos SOTA e pré-treinados geralmente superam LLMs (Yin et al. 2024).
- **Atalho semântico (Semantic Trap):** modelos ajustados por SFT atingem F1 alto associando **padrões funcionais/superficiais** (código funcionalmente parecido; distância textual medida por CodeBLEU) à probabilidade de vulnerabilidade, sem entender a causa-raiz. Manifesta-se como desempenho sensível ao pareamento (alto em V2N não-pareado, colapsa em V2P pareado) e fragilidade a perturbações que preservam a semântica (Huang et al., 2026).
- **Viés conservador:** vários modelos exibem alta precisão mas revocação baixa, perdendo vulnerabilidades reais (Gao, S. et al., TREAT, 2025).

### 7.3. Contaminação de dados e benchmarks

**Datasets clássicos e seus problemas (acurácia de rótulo medida pelo PrimeVul):**
- **Devign / CodeXGLUE:** rotulagem manual, mas apenas **24%** das funções amostradas eram de fato vulneráveis.
- **Big-Vul:** extraído de correções de CVE; desbalanceado; **25%** de acurácia de rótulo; duplicação relevante.
- **DiverseVul:** mais amplo (consolida Devign, BigVul, ReVeal, CrossVul, CVEfixes), com ~**60%** de acurácia de rótulo após deduplicação; ainda herda ruído.

**O ponto de virada (PrimeVul, Ding et al., ICSE 2025):** melhora a rotulagem (ONEFUNC 86%, NVDCHECK 92%, ~ SVEN 94%), deduplica, adota divisão **temporal** e propõe métricas realistas. Escala: **6.968 vulneráveis + 228.800 benignas, 140 CWEs, 755 projetos** (razão ~1:32). Achado marcante: o StarCoder2-7B, que marca **68,26% de F1 no Big-Vul, cai para 3,09% no PrimeVul**, indistinguível do acaso. Modelos proprietários avançados, mesmo ajustados, ficam próximos do palpite aleatório sob avaliação pareada.

Contribuições metodológicas centrais do PrimeVul:
- **VD-S (Vulnerability Detection Score):** taxa de falsos negativos sob taxa de falsos positivos ≤ 0,5%. Prioriza minimizar falsos negativos com controle de falsos positivos.
- **Avaliação pareada:** cada função vulnerável é comparada à sua versão corrigida, com quatro desfechos (ambos corretos [P-C], ambos previstos vulneráveis [P-V], ambos benignos [P-B], invertido [P-R]).

**Por que F1 sozinho engana:** a própria fonte (PrimeVul) argumenta que **tanto acurácia quanto F1 enganam** em VD realista, por não refletirem a assimetria entre falsos positivos e falsos negativos. Por isso reportam-se em conjunto F1 da classe vulnerável, taxa de falsos positivos, VD-S e acurácia pareada.

**Benchmarks recentes mais rigorosos:** MegaVul (Ni et al. 2024; 17.380 vulns, 169 CWEs), ReposVul de nível de repositório (Wang et al. 2024), SecVulEval com anotação em nível de instrução (Ahmed et al. 2025), CleanVul com limpeza de rótulos por heurística de LLM (Li, Y. et al. 2024/2025; F1 0,82) e **JITVUL** (Yildiz et al. 2025), benchmark **pareado just-in-time** que liga cada função aos commits que a introduzem e corrigem (879 CVEs, 91 CWEs). Reconhece-se o risco de memorização dos conjuntos antigos pelos LLMs modernos, o que reforça o uso de divisões temporais e de dados posteriores ao corte de conhecimento.

### 7.4. Técnicas de eficiência aplicadas à tarefa

**Quantização.** GPTQ faz quantização one-shot com compensação de erro por informação de segunda ordem (Frantar et al., ICLR 2023); AWQ preserva ~0,1–1% de pesos salientes identificados pela distribuição das ativações e generaliza bem sem overfit ao conjunto de calibração (Lin et al., MLSys 2024); SmoothQuant trata pesos e ativações em conjunto no regime W8A8 (Xiao et al., ICML 2023). Ponto favorável a este projeto: tarefas de **compreensão/classificação** são mais robustas à baixa precisão do que a **geração autorregressiva** — há evidência de degradação desprezível em modelos **codificadores** sob 4 bits, ao contrário de **decodificadores** de geração (Wu et al., INT4, ICML 2023).
**Duas ressalvas críticas (parte da lacuna):** (a) o resultado "robusto" de Wu é para **arquitetura encoder** em tarefas gerais de NLP e no regime agressivo **W4A4** (peso + ativação); o Recorte A usa **decoders de código com cabeça de classificação** e quantização **weight-only (W4A16)** — regime mais brando, mas a transferência do resultado de Wu para esse caso é hipótese a testar, não fato herdado. (b) Para **geração** de código, a quantização exige receita cuidadosa mas é viável (Wei et al., ESEC/FSE 2023, mostram um modelo de 6B em laptop sem degradação significativa, sobretudo em INT8).

**Ajuste fino eficiente (LoRA/QLoRA).** LoRA treina matrizes de baixo posto com pesos congelados, reduzindo parâmetros treináveis em ordens de grandeza (Hu et al., ICLR 2022). QLoRA combina isso à quantização em 4 bits (NF4), viabilizando ajustar um modelo de **65B numa única GPU de 48 GB sem perda relevante** frente ao ajuste em 16 bits (Dettmers et al., NeurIPS 2023 — resultado obtido em instruction-following, não em classificação de vulnerabilidade; a transferência é a própria RQ do projeto). Na tarefa:
- QLoRA com **cabeça de classificação** iguala codificadores totalmente ajustados em conjuntos fáceis (F1 alto no Big-Vul), mas **apenas empata** com esses codificadores no PrimeVul (F1 médio 0,77 ≈ UniXcoder); a formulação por **classificação supera a por geração** (Ouchebara & Dupont, 2025 — Llama-3.1 8B; observar: o "modelo pequeno" é 8B contra encoder de 125M; split único, sem intervalos de confiança).
- LoRA em modelo de código (WizardCoder 13B) superou baseline de codificador (ContraBERT) em detecção binária **em Java**, com margem pequena (F1 0,71 vs 0,68) e apenas 25M de parâmetros treináveis (Shestov et al., IEEE Access 2025).
- **Lacuna a investigar:** o comportamento do QLoRA por classificação sob **dados realmente desbalanceados** (sem balanceamento artificial) permanece pouco medido — Ouchebara balanceou os dados.

**Destilação.** Avatar comprime codificadores de código (CodeBERT/GraphCodeBERT) em ordens de grandeza de tamanho (modelos de 3 MB, 160× menores) e energia (até 184× menos), mantendo desempenho competitivo em predição de vulnerabilidade, com perda pequena (1,67%) (Shi et al., **ICSE-SEIS 2024**). PSO-KDVA aplica destilação + otimização por enxame para **avaliação/assessment (score CVSS)** — tarefa distinta da detecção — retendo 89,3% do desempenho com 0,6% do tamanho (Gao, C. et al., 2025).

**Lacuna na interseção:** quase não há trabalho que meça **isoladamente** o efeito do *método* de quantização (AWQ, GPTQ, NF4, GGUF) sobre a **qualidade de classificação** de vulnerabilidade (não geração), combinado a QLoRA, sob avaliação descontaminada (PrimeVul + pareado + VD-S). É o espaço mais promissor.

---

## 8. Lacunas de pesquisa

1. Efeito isolado do **método** de quantização na classificação de vulnerabilidade (VD-S, acurácia pareada), não sobre geração ou perplexidade. **[núcleo da originalidade]**
2. QLoRA versus ajuste completo no mesmo modelo, sob avaliação descontaminada.
3. Modelo pequeno especializado por QLoRA versus modelo maior genérico: quantificar recuperação de desempenho e custo relativo.
4. Qual método de quantização melhor preserva a discriminação pareada vulnerável/corrigido.
5. Robustez de modelos **quantizados** a perturbações que preservam a semântica (cruzar o protocolo de SecLLMHolmes/Huang et al. com a quantização — ninguém fez). **[diferencial limpo e barato]**
6. Trade-off entre eficiência e robustez adversarial em modelos comprimidos para segurança (sem fonte forte no corpus atual — requer referências adicionais).
7. Detecção descontaminada e eficiente em múltiplas linguagens (além de C/C++) — aspiracional.
8. Benchmark de eficiência padronizado e reprodutível (memória, tokens/s, energia, custo/hora) — **usar** TokenPowerBench (Niu et al. 2025), não reinventar.
9. Comportamento do QLoRA por classificação sob desbalanceamento realista (sem balanceamento artificial).

---

## 9. Roteiro recomendado em três estágios

**Estágio 1 — Fundação (meses 1 a 2 do trabalho experimental).** Adotar PrimeVul e PrimeVul pareado como benchmark primário; adicionar um benchmark temporal recente para controlar contaminação. Nunca reportar só F1 em Big-Vul ou Devign. Métricas: F1 da classe vulnerável, taxa de falsos positivos (baseline de prompt); VD-S e acurácia pareada a partir do estágio com cabeça de classificação. Baselines: UniXcoder totalmente ajustado (125M) e um LLM pequeno em prompt. **Rodar múltiplos seeds + intervalos de confiança.**

**Estágio 2 — QLoRA especializado (meses 3 a 5).** Ajustar por QLoRA (NF4, 4 bits) com **cabeça de classificação** em Qwen2.5-Coder-7B, DeepSeek-Coder 6.7B (denso, para caber em 24 GB) e StarCoder2-7B. Responder à pergunta do modelo pequeno especializado versus maior genérico, com os três eixos explícitos: **7B-4bit-QLoRA vs 7B-16bit vs UniXcoder-125M**. Incluir teste de robustez semântica.

**Estágio 3 — Quantização comparativa (meses 6 a 8).** Comparar AWQ, GPTQ, NF4 e (à parte, por ser CPU/edge) GGUF sobre o modelo já ajustado, medindo VD-S e acurácia pareada (não perplexidade). Documentar o conjunto de calibração e a ordem (quantizar→QLoRA vs QLoRA→PTQ). **Isolar o motor de inferência** ao medir custo (não misturar llama.cpp/GGUF com vLLM/AWQ na mesma curva).

**Limiares que mudam a decisão:**
- Se o QLoRA-7B ficar >5 pontos de VD-S abaixo do UniXcoder ajustado, pivotar para abordagem neuro-simbólica (estilo IRIS) ou RAG de conhecimento (Vul-RAG).
- Se a quantização de 4 bits degradar a acurácia pareada em >3 pontos frente ao 16 bits, recomendar 8 bits como padrão.
- **Cenário-base (não plano B):** se a acurácia pareada permanecer próxima do acaso mesmo após QLoRA — o que a literatura de 2026 torna provável — reenquadrar a contribuição como **estudo de eficiência versus qualidade**: o modelo pequeno quantizado é tão limitado quanto o grande, porém muito mais barato. É um resultado publicável e de baixo risco.

---

## 10. Metodologia de medição de eficiência

**Métricas a reportar:**
- Memória/VRAM: memória de carga (idle) mais pico durante inferência. (Para MoE, o total de parâmetros domina a memória de carga.)
- Latência: tempo até o primeiro token (TTFT), tempo por token de saída (TPOT), latência total.
- Vazão: tokens por segundo.
- Energia: Joules por token e por resposta, potência média em watts, amostrando via nvidia-smi ou pynvml; alinhar à metodologia do TokenPowerBench (separar prefill/decode).
- Custo: valor por hora da instância × tempo de execução, como proxy reprodutível.

**Boas práticas:** fixar tamanho de lote (1 para serviço online), comprimento de entrada/saída, decodificação determinística; **repetir várias vezes e reportar média e percentis com intervalos de confiança**; registrar a instância exata (modelo de GPU e tier), porque o preço varia bastante.

**Preços de referência RunPod (início de 2026, sujeitos a variação):** RTX 4090 24 GB a partir de ~0,34–0,69 USD/h; A100 80 GB PCIe ~1,39 USD/h; H100 80 GB PCIe ~2,89 USD/h. Cobrança por segundo.

---

## 11. Ferramentas e frameworks

- Treino e PEFT: Hugging Face Transformers + PEFT (LoRA/QLoRA), bitsandbytes (NF4 4 bits), TRL, Unsloth, Axolotl.
- Quantização: AutoGPTQ/GPTQModel, AutoAWQ, llama.cpp (GGUF), llm-compressor.
- Serviço e inferência: vLLM (PagedAttention, batching contínuo; Kwon et al. 2023), SGLang, TGI.
- Avaliação: scikit-learn; scripts próprios para VD-S e avaliação pareada (o PrimeVul disponibiliza referência).
- Energia e eficiência: nvidia-smi, pynvml, Zeus; TokenPowerBench como arcabouço de medição de energia da inferência.

---

## 12. Referências consultadas

Predominam artigos científicos e relatórios técnicos. O status de revisão por pares está indicado. Recomenda-se confirmar cada entrada no arXiv/Scholar antes do uso final, com atenção redobrada aos preprints de 2025–2026. **Os 41 arquivos correspondentes foram verificados um a um contra as afirmações deste dossiê (ver `ANALISE_CRITICA_RECORTE_A.md`).**

### 12.1. Detecção de vulnerabilidade: métodos e modelos

- Zhou, Y. et al. **Devign.** NeurIPS, 2019. arXiv:1909.03496. [revisado por pares]
- Feng, Z. et al. **CodeBERT.** Findings of EMNLP, 2020. arXiv:2002.08155. [revisado por pares]
- Guo, D. et al. **GraphCodeBERT.** ICLR, 2021. arXiv:2009.08366. [revisado por pares]
- Guo, D. et al. **UniXcoder.** ACL, 2022. arXiv:2203.03850. [revisado por pares]
- Li, Z.; Dutta, S.; Naik, M. **IRIS.** ICLR, 2025. arXiv:2405.17238. [revisado por pares]
- Du, X. et al. **Vul-RAG.** 2024/2025. arXiv:2406.11147; DOI:10.1145/3797277. [revisado por pares]
- Ullah, S. et al. **SecLLMHolmes.** IEEE S&P, 2024. arXiv:2312.12575; DOI:10.1109/SP54263.2024.00210. [revisado por pares]
- Yin, X.; Ni, C.; Wang, S. **Multitask-based Evaluation of Open-Source LLM on Software Vulnerability.** IEEE TSE, 2024. arXiv:2404.02056. [revisado por pares]
- Zhou, X.; Zhang, T.; Lo, D. **LLM for Vulnerability Detection: Emerging Results and Future Directions.** ICSE-NIER, 2024. arXiv:2401.15468. [revisado por pares]
- Shestov, A. et al. **Finetuning LLMs for Vulnerability Detection (WizardCoder).** IEEE Access, 2025. arXiv:2401.17010. [revisado por pares]
- Yildiz, E. et al. **Benchmarking LLMs and LLM-based Agents in Practical Vulnerability Detection (JITVUL).** ACL, 2025. arXiv:2503.03586. [revisado por pares, verificar]
- Sheng, Z. et al. **LLMs in Software Security: A Survey of Vulnerability Detection Techniques and Insights.** ACM Computing Surveys, 2025. arXiv:2502.07049. [revisado por pares, verificar]
- Gao, Z. et al. **How Far Have We Gone in Vulnerability Detection Using LLMs (VulBench).** 2023. arXiv:2311.12420. [preprint]
- Ouchebara, D. S.; Dupont, S. **Llama-based Source Code Vulnerability Detection: Prompt Engineering vs Fine Tuning.** 2025. arXiv:2512.09006. [preprint, verificar ID]
- Al Atiiq, S.; Gehrmann, C.; Dahlén, K.; Khalil, K. **From Generalist to Specialist: Exploring CWE-Specific Vulnerability Detection.** 2024. arXiv:2408.02329. [preprint]
- Huang, F.; Sun, Y.; Zhang, F.; Yang, Z.; Liu, H.; Liu, Y. **Do Fine-Tuned LLMs Understand Vulnerabilities? An Investigation into the Semantic Trap.** 2026. arXiv:2601.22655. [preprint, verificar ID]
- Kaniewski, S.; Schmidt, F.; Heer, T. **Revisiting Vul-RAG: Reproducibility and Replicability with Open-Weight Models.** 2026. arXiv:2606.04739. [preprint, verificar ID]
- Gao, S. et al. **TREAT: A Code LLMs Trustworthiness/Reliability Evaluation and Testing Framework.** 2025. arXiv:2510.17163. [preprint, verificar ID]

### 12.2. Datasets e benchmarks

- Fan, J.; Li, Y.; Wang, S.; Nguyen, T. N. **Big-Vul.** MSR, 2020, p. 508-512. [revisado por pares]
- Lu, S. et al. **CodeXGLUE.** NeurIPS Datasets and Benchmarks, 2021. arXiv:2102.04664. [revisado por pares]
- Chen, Y. et al. **DiverseVul.** RAID, 2023. arXiv:2304.00409. [revisado por pares]
- Ding, Y. et al. **PrimeVul.** ICSE, 2025. arXiv:2403.18624. [revisado por pares]
- Ni, C. et al. **MegaVul.** MSR, 2024. arXiv:2406.12415; DOI:10.1145/3643991.3644886. [revisado por pares]
- Wang, X. et al. **ReposVul.** ICSE (Industry), 2024. DOI:10.1145/3639478.3647634. [revisado por pares]
- Ahmed, S. et al. **SecVulEval.** 2025. arXiv:2505.19828. [preprint, verificar]
- Li, Y. et al. **CleanVul.** 2024/2025. arXiv:2411.17274. [preprint, verificar]

### 12.3. Eficiência: quantização, PEFT e destilação

- Frantar, E. et al. **GPTQ.** ICLR, 2023. arXiv:2210.17323. [revisado por pares]
- Lin, J. et al. **AWQ.** MLSys, **2024** (Best Paper). arXiv:2306.00978. [revisado por pares]
- Xiao, G. et al. **SmoothQuant.** ICML, **2023**. arXiv:2211.10438. [revisado por pares]
- Hu, E. et al. **LoRA.** ICLR, 2022. arXiv:2106.09685. [revisado por pares]
- Dettmers, T. et al. **QLoRA.** NeurIPS, 2023. arXiv:2305.14314. [revisado por pares]
- Wu, X. et al. **Understanding INT4 Quantization for Transformer Models.** ICML, 2023. arXiv:2301.12017. [revisado por pares]
- Wei, X. et al. **Greener yet Powerful: Taming Large Code Generation Models with Quantization.** ESEC/FSE, 2023. arXiv:2303.05378; DOI:10.1145/3611643.3616302. [revisado por pares]
- Shi, J. et al. **Greening Large Language Models of Code (Avatar).** **ICSE-SEIS, 2024**. arXiv:2309.04076; DOI:10.1145/3639475.3640097. [revisado por pares]
- Gao, C. et al. **Resource-Efficient Automatic Software Vulnerability Assessment (PSO-KDVA).** Engineering Applications of AI, 2025. arXiv:2508.02840. [revisado por pares, verificar]

### 12.4. Modelos de código

- Hui, B. et al. **Qwen2.5-Coder Technical Report.** 2024. arXiv:2409.12186. [relatório técnico]
- Lozhkov, A. et al. **StarCoder 2 and The Stack v2.** 2024. arXiv:2402.19173. [relatório técnico]
- Mishra, M. et al. **Granite Code Models.** 2024. arXiv:2405.04324. [relatório técnico]
- Zhu, Q.; Guo, D.; Shao, Z. et al. (DeepSeek-AI). **DeepSeek-Coder-V2.** 2024. arXiv:2406.11931. [relatório técnico] — MoE 16B/236B (2,4B/21B ativos), 338 linguagens, contexto 128K.

### 12.5. Infraestrutura de inferência e medição de eficiência

- Kwon, W. et al. **Efficient Memory Management for LLM Serving with PagedAttention (vLLM).** SOSP, 2023. arXiv:2309.06180. [revisado por pares]
- Niu, C. et al. **TokenPowerBench: Benchmarking the Power Consumption of LLM Inference.** 2025. arXiv:2512.03024. [preprint, verificar ID]

### 12.6. Referências recomendadas a ACRESCENTAR (ver §13 e a nota de suficiência)

Não presentes no corpus atual, mas importantes para a fundamentação (confirmar bibliografia exata):
- Chakraborty et al. **ReVeal / Deep Learning Based Vulnerability Detection: Are We There Yet?** IEEE TSE, 2021.
- Li et al. **VulDeePecker.** NDSS, 2018.
- Fu & Tantithamthavorn. **LineVul.** MSR, 2022.
- Steenhoek et al. **A Comprehensive Study of the Capabilities of LLMs for Vulnerability Detection.** 2024.
- Risse & Böhme. **Uncovering the Limits of Machine Learning for Automatic Vulnerability Detection.** USENIX Security, 2024.
- Dettmers et al. **LLM.int8().** NeurIPS, 2022 (fundamento do bitsandbytes/8-bit).
- (Survey de quantização, p.ex. Gholami et al. 2021) e referência para **GGUF/llama.cpp**.
- You et al. **Zeus** (medição/otimização de energia), NSDI, 2023.
- (Survey de PEFT) para contextualizar LoRA/QLoRA no panorama de adaptadores.

---

## 13. Ressalvas importantes

- **Revisão por pares versus preprint.** Várias fontes que sustentam a hipótese central (Ouchebara & Dupont 2025; Huang et al. 2026; Kaniewski 2026; TREAT 2025; SecVulEval; CleanVul) são preprints, alguns com split único e sem intervalos de confiança. Ancorar as afirmações centrais em venues revisados (PrimeVul/ICSE, IRIS/ICLR, SecLLMHolmes/S&P, QLoRA/NeurIPS, GPTQ/ICLR, AWQ/MLSys, Avatar/ICSE-SEIS) e tratar os preprints como "evidência emergente".
- **Contaminação e reprodutibilidade.** Muitos F1 altos vêm de datasets contaminados e não se reproduzem sob avaliação rigorosa (68,26%→3,09% é o exemplo canônico). Números de modelos proprietários variam por não-determinismo e versão de API.
- **Datas e identificadores.** Os IDs arXiv de 2025/2026 marcados "verificar" foram coletados por pesquisa automatizada e podem conter imprecisão de numeração; confira o ID junto ao título e aos autores. (Alguns títulos de arquivo no corpus tinham anos trocados — AWQ e SmoothQuant já corrigidos aqui.)
- **Balanceamento geográfico da bibliografia.** A alta presença de trabalhos asiáticos reflete o peso real da área, não um viés de qualidade; o corpus é, de fato, equilibrado entre EUA, Europa e Ásia, em venues de topo. O critério de qualidade é revisão por pares/venue, não origem.
- **Suficiência da bibliografia.** O corpus de 41 artigos é um núcleo forte e suficiente para a qualificação, mas para a fundamentação completa da dissertação recomenda-se acrescentar ~10–15 referências (ver §12.6): fundamentos clássicos de VD (ReVeal, VulDeePecker, LineVul, Steenhoek, Risse & Böhme), fundamentos de quantização/energia (LLM.int8(), survey de quantização, Zeus, GGUF/llama.cpp) e um survey de PEFT.
- **Preços de GPU.** Instantâneos de início de 2026; flutuam com o tier (Secure vs Community).
- **Formatação institucional.** Se o PPGCC exigir formulário/ABNT específico, o modelo oficial prevalece.
- **Escopo deste registro.** Documento consolida definição + levantamento. É base de trabalho, não texto final de qualificação; a redação definitiva deve passar pela leitura direta das fontes e pela orientação.
