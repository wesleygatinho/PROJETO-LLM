# RECORTE A — Dossiê Completo

**Detecção eficiente de vulnerabilidades em código por modelos de linguagem: quantização e ajuste fino eficiente sob avaliação descontaminada**

Registro consolidado de tudo que foi definido para o Recorte A (projeto de mestrado, PPGCC UFMA), incluindo definição, contexto, metodologia, roteiro de execução, cronograma, revisão de literatura (estado da arte 2024 a 2026), lacunas de pesquisa e todas as fontes consultadas com dados bibliográficos.

Documento gerado como memória de trabalho. Data de consolidação: setembro de 2026.

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

**O que é:** tema de dissertação de mestrado em Ciência da Computação (PPGCC UFMA). É um trabalho de método mais avaliação: além de medir, ele especializa modelos pequenos via ajuste fino eficiente (QLoRA) para a tarefa, e verifica se isso fecha a diferença para modelos grandes.

**Natureza da contribuição:** não é inventar um algoritmo novo. É um estudo empírico sistemático mais uma recomendação prática, com um gancho científico forte (a contaminação dos benchmarks tradicionais). É uma dissertação de avaliação e caracterização, tipo aceito e de baixo risco.

**Duas perguntas de pesquisa norteadoras:**
- Um modelo pequeno especializado por QLoRA recupera o desempenho de um modelo maior?
- Qual método de quantização preserva melhor a qualidade na detecção?

---

## 2. Contexto acadêmico

- **Programa:** PPGCC UFMA, mestrado em Ciência da Computação. O programa tem duas linhas: Arquitetura de Sistemas Computacionais e Modelagem Computacional. Este trabalho se encaixa em **Modelagem Computacional** (eixo de reconhecimento de padrões e aprendizado de máquina). Recomenda-se verificar o Lattes do possível orientador, porque o recorte é fortemente puxado pela linha de quem orienta.
- **Recursos computacionais:** GPUs alugadas sob demanda (RunPod).
- **Funil do mestrado:** estudo dirigido (levantamento e delimitação) → qualificação → dissertação. O esforço de cada fase alimenta a próxima.
- **Relação com o TCC (Recorte B):** o autor conduz um TCC de Engenharia da Computação em tema correlato, porém distinto (avaliação de eficiência na geração de código). Os dois trabalhos compartilham fundamentação e infraestrutura, mas têm tarefa, método e contribuição próprios. Recomenda-se transparência com as duas orientações sobre esse tema compartilhado.

---

## 3. O problema explicado em linguagem simples

**A tarefa.** Detecção de vulnerabilidade aqui é classificação: dá-se ao modelo uma função (um pedaço de código) e ele responde se tem vulnerabilidade ou não (ou qual tipo, se for mais fino). Não é gerar código, é julgar código. A avaliação fica limpa e barata (compara a resposta com o rótulo verdadeiro), diferente de geração, onde é preciso rodar testes.

**As duas alavancas de eficiência.**
- **Quantização.** Um modelo guarda seus pesos em números de 16 bits por padrão. Quantizar é reescrever esses números com menos bits (8 ou 4), o que reduz muito a memória de GPU e acelera a inferência, com alguma perda possível de qualidade. Há vários métodos (AWQ, GPTQ, GGUF, bitsandbytes) que perdem quantidades diferentes.
- **QLoRA.** Forma barata de treinar (ajustar) um modelo pequeno para ficar especialista numa tarefa, sem retreinar o modelo inteiro. A hipótese a testar: um modelo pequeno especializado por QLoRA alcança um modelo grande e genérico?

**O gancho científico.** Muitos resultados publicados usam benchmarks contaminados (dados repetidos entre treino e teste), o que superestima o desempenho. Provar isso, contrastando um benchmark antigo com um limpo, é um resultado forte por si só.

---

## 4. Metodologia (cinco etapas)

1. **Reproduzir baselines.** Pegar dois ou três modelos pequenos abertos em versão Instruct (por exemplo StarCoder2, Qwen2.5-Coder, Granite Code) e um codificador de referência (UniXcoder), rodar em precisão cheia (16 bits) sobre o conjunto depurado e pareado, anotando qualidade. Serve para aprender o harness e ter o ponto de referência.
2. **Ligar a quantização.** Rodar os mesmos modelos em 8 e 4 bits, com os diferentes métodos (AWQ, GPTQ, NF4, GGUF), anotando qualidade e custo (memória, latência).
3. **Ligar o QLoRA.** Especializar os modelos pequenos com cabeça de classificação na partição de treino e reavaliar, comparando modelo pequeno especializado contra modelo maior não especializado.
4. **Mostrar o efeito da contaminação.** Rodar o mesmo modelo num benchmark antigo (Devign ou Big-Vul) e num limpo (PrimeVul), evidenciando a queda no limpo. Incluir teste de robustez a perturbações que preservam a semântica.
5. **Montar as curvas de trade-off.** Cruzar qualidade e custo num gráfico, achar o joelho da curva (quase toda a qualidade por fração do custo) e escrever a recomendação prática.

**Métricas de qualidade (dado desbalanceado, F1 sozinho engana):** F1 da classe vulnerável, VD-S (taxa de falsos negativos sob taxa de falsos positivos de no máximo 0,5%), acurácia pareada (o modelo distingue a função vulnerável da sua versão corrigida?) e taxa de falsos positivos.

**Métricas de custo:** memória de GPU (pico), latência (primeiro token e por token), vazão (tokens por segundo), energia e valor por hora da instância.

**Decisão-chave de desenho:** usar cabeça de classificação, não geração. A evidência mostra que classificação tolera melhor a quantização e rende melhor que a formulação por geração nesta tarefa.

---

## 5. Etapa 1 detalhada (roteiro de execução)

Objetivo: montar a bancada e ter um número de referência confiável. Sair sabendo rodar qualquer modelo no dataset e medir sua qualidade, porque todas as etapas seguintes são variações disso.

Decisão que molda tudo: na Etapa 1 usa-se **prompt** (mostra a função e pede sim/não), sem treino. Treinar para classificar entra só na Etapa 3 (QLoRA). Para prompt funcionar, usar as versões **Instruct** dos modelos.

Passos:
1. **Subir o ambiente.** No RunPod, subir um pod com uma GPU (24 GB roda os 7B em 16 bits), instalar Python, PyTorch e a biblioteca transformers da Hugging Face, baixar o primeiro modelo. Começar pelo menor (3B) para depurar rápido e não gastar crédito à toa.
2. **Pegar e entender o dataset.** Baixar o PrimeVul (o limpo, principal). Antes de rodar, abrir os dados e entender o formato: cada item é uma função com um rótulo, e no PrimeVul há pares de função vulnerável e corrigida. Localizar a divisão treino/validação/teste. Na Etapa 1 usa-se só o teste.
3. **Escrever o laço de inferência.** Para cada função do teste, montar o prompt (instrução fixa mais o código), enviar ao modelo, ler a resposta em texto e converter para decisão (sim vira 1, não vira 0). A parte trabalhosa é fazer essa leitura da resposta de forma robusta (o modelo às vezes responde "Sim, esta função..." em vez de só "sim").
4. **Escrever a avaliação.** Com predições e rótulos verdadeiros, calcular F1, precisão, revocação e acurácia (scikit-learn faz cada uma em uma linha). O F1 é a métrica principal porque o dataset é desbalanceado.
5. **Rodar por modelo e anotar tudo.** Rodar os modelos em 16 bits e registrar numa planilha qualidade (F1, precisão, revocação) e custo básico (memória de GPU, tempo por predição, valor por hora do pod).
6. **Conferir se a bancada está correta.** Comparar com números de artigos que usaram os mesmos modelos e datasets. Não precisa bater na casa decimal, mas diferença absurda indica bug no prompt ou na leitura da resposta.

Dicas: fixar temperatura em 0 (geração determinística); começar com umas 50 funções para iterar rápido; registrar junto de cada número exatamente qual modelo, precisão e prompt o geraram. Armadilha principal: a leitura da resposta do modelo (parsing), que consome boa parte do tempo. Pronto da etapa: uma tabela com F1 e custo de dois ou três modelos em 16 bits no PrimeVul, confiável.

---

## 6. Cronograma

Ciclo aproximado de vinte e quatro meses, ajustável ao calendário do PPGCC.

| Fase | Atividades | Meses |
|---|---|---|
| Estudo dirigido | Revisão do estado da arte, definição das métricas descontaminadas, montagem do arcabouço e reprodução de baselines (Etapa 1) | 1 a 6 |
| Consolidação | Quantização (Etapa 2), início do QLoRA com cabeça de classificação (Etapa 3) e estudo de contaminação (Etapa 4) | 6 a 12 |
| Qualificação | Redação e defesa da qualificação com fundamentação, problema e resultados preliminares | 12 a 15 |
| Dissertação | Conclusão da Etapa 3, análise de trade-off (Etapa 5), redação da dissertação e submissão de artigo | 15 a 24 |

O TCC (Recorte B) roda em paralelo e fecha antes, reaproveitando o mesmo harness e datasets.

---

## 7. Revisão de literatura (estado da arte 2024 a 2026)

### 7.1. Formulação, taxonomia e evolução

O problema é formulado em quatro granularidades: classificação binária de função, classificação por tipo de fraqueza (CWE), detecção em nível de linha ou instrução (localização) e detecção em nível de repositório (raciocínio inter-procedural).

A evolução das abordagens: redes neurais em grafo, que modelam a semântica do programa via grafos de código (Devign, Zhou et al., 2019); modelos pré-treinados codificadores (CodeBERT, Feng et al., 2020; GraphCodeBERT, Guo et al., 2021; UniXcoder, Guo et al., 2022); e LLMs de código (Qwen2.5-Coder, StarCoder2, DeepSeek-Coder, CodeLlama, Granite Code). Observação recorrente: codificadores totalmente ajustados, em especial o UniXcoder, permanecem baselines fortes, por vezes superando LLMs bem maiores na detecção (Yin et al., 2024).

Boa parte dos modelos de código de ponta vem de laboratórios chineses (Alibaba/Qwen, DeepSeek), e datasets e benchmarks importantes (MegaVul, ReposVul, Vul-RAG) têm autores em instituições chinesas, o que confirma o peso da pesquisa asiática na área.

### 7.2. LLMs para detecção de vulnerabilidade

**Técnicas empregadas:** prompting sem exemplos e com poucos exemplos, raciocínio em cadeia, ajuste fino supervisionado, sistemas de agentes e multi-agente, recuperação aumentada por conhecimento (RAG) e abordagens neuro-simbólicas (LLM mais análise estática).

**O que funciona melhor:**
- **IRIS** (neuro-simbólico): acopla um LLM a análise estática. Em um conjunto de 120 vulnerabilidades em Java (CWE-Bench-Java), com um modelo proprietário forte detecta 55, contra 27 de uma ferramenta de análise estática consolidada, e melhora a taxa média de falsas descobertas; mantém bom desempenho mesmo com modelo aberto de 7B, detectando 52. Descobriu inclusive vulnerabilidades antes desconhecidas (Li, Dutta, Naik, 2024).
- **Vul-RAG** (recuperação de conhecimento): eleva a acurácia pareada em cerca de 16 a 24% relativos (Du et al., 2024). Porém, um estudo de reprodutibilidade observou um platô em torno de 0,30 de acurácia pareada com modelos abertos, pouco acima do acaso (0,25), e um modelo de 4B igualando um de 30B (estudo de reprodutibilidade, preprint 2026).

**O que falha:**
- **Fragilidade / não-robustez:** modelos avançados mudam de resposta diante de renomeações de função ou variável (erro em cerca de 26% dos casos) e de adição de funções de biblioteca (cerca de 17%), com respostas não-determinísticas e raciocínio infiel (Ullah et al., SecLLMHolmes, 2024).
- **Desempenho baixo em condições realistas:** em nível de instrução, o melhor modelo avaliado atinge apenas cerca de 24% de F1 (SecVulEval, preprint 2025). Em avaliações multitarefa, métodos SOTA e modelos pré-treinados geralmente superam LLMs na detecção (Yin et al., 2024).
- **Atalhos semânticos (Semantic Trap):** há indício de que modelos ajustados atingem F1 alto associando domínios funcionais (gestão de memória, protocolos de rede) à probabilidade de vulnerabilidade, sem entender a causa-raiz (preprint 2026, verificar).
- **Viés conservador:** alguns modelos abertos grandes têm alta precisão mas revocação muito baixa, perdendo muitas vulnerabilidades reais (TREAT, preprint 2025).

### 7.3. Contaminação de dados e benchmarks

**Datasets clássicos e seus problemas:**
- **Devign:** rotulagem manual cuidadosa (FFmpeg, QEMU), mas cara; parcela de rótulos imprecisos e duplicação.
- **Big-Vul:** extraído de correções de CVE; desbalanceado, com estimativas de rótulos imprecisos que chegam a parcela expressiva do conjunto e duplicação relevante.
- **DiverseVul:** mais amplo e diverso (consolida Devign, BigVul, ReVeal, CrossVul, CVEfixes), com cerca de 60% de acurácia de rótulo após deduplicação; ainda herda ruído.
- **CodeXGLUE (defect detection):** usa Devign, herdando seus problemas.

**O ponto de virada (PrimeVul, Ding et al., 2024):** melhora a rotulagem, deduplica, adota divisão temporal e propõe métricas realistas. Achado marcante: um modelo de 7B (StarCoder2) que marca 68,26% de F1 no Big-Vul cai para 3,09% no PrimeVul, indistinguível do acaso. Modelos proprietários avançados, mesmo com ajuste fino, ficam próximos do palpite aleatório sob avaliação pareada.

Contribuições metodológicas centrais do PrimeVul:
- **VD-S (Vulnerability Detection Score):** taxa de falsos negativos sob taxa de falsos positivos de no máximo 0,5%. Prioriza minimizar falsos negativos com controle de falsos positivos.
- **Avaliação pareada:** cada função vulnerável é comparada à sua versão corrigida (compartilhando a maior parte do código), com quatro desfechos (ambos corretos, ambos previstos vulneráveis, ambos benignos, invertido). Mede se o modelo realmente distingue as duas.

**Por que F1 sozinho engana:** num teste balanceado entre vulneráveis e corrigidos, classificar tudo como vulnerável dá revocação 1,0, precisão 0,5 e F1 cerca de 0,67, com taxa de falsos positivos de 100%, ou seja, inútil na prática. Por isso reportam-se em conjunto F1 da classe vulnerável, taxa de falsos positivos, VD-S e acurácia pareada.

**Benchmarks recentes mais rigorosos:** MegaVul (Ni et al., 2024), ReposVul de nível de repositório (Wang et al., 2024), SecVulEval com anotação em nível de instrução (preprint 2025), CleanVul com limpeza de rótulos por heurística de LLM (preprint 2024) e JITVUL, benchmark pareado just-in-time construído sobre o PrimeVul (Yildiz et al., 2025). Reconhece-se ainda o risco de memorização dos conjuntos antigos pelos LLMs modernos, o que reforça o uso de divisões temporais e de dados posteriores ao corte de conhecimento.

### 7.4. Técnicas de eficiência aplicadas à tarefa

**Quantização.** GPTQ faz quantização com compensação de erro baseada em informação de segunda ordem (Frantar et al., 2023); AWQ preserva pesos salientes identificados pela distribuição das ativações, com menor degradação em baixa precisão (Lin et al., 2024); SmoothQuant trata pesos e ativações em conjunto (Xiao et al., 2023). Ponto favorável a este projeto: tarefas de classificação e compreensão são bem mais robustas à baixa precisão do que a geração autorregressiva. Há evidência de degradação desprezível em modelos codificadores sob 4 bits, ao contrário de decodificadores voltados à geração (Wu et al., INT4 Transformers, ICML 2023). Ressalva: esse resultado vem de tarefas gerais de NLP, não isolado para código, o que é justamente parte da lacuna. Para geração de código, a literatura mostra maior sensibilidade (Wei et al., 2023).

**Ajuste fino eficiente (LoRA/QLoRA).** LoRA treina matrizes de baixo posto com pesos congelados (Hu et al., 2022). QLoRA combina isso à quantização em 4 bits, viabilizando o ajuste fino de um modelo de 65B em uma única GPU de 48 GB sem perda relevante frente ao ajuste em 16 bits (Dettmers et al., 2023). Na tarefa:
- QLoRA com **cabeça de classificação** pode igualar codificadores totalmente ajustados em conjuntos fáceis (F1 alto no Big-Vul), mas apenas empatar com esses codificadores no PrimeVul; a formulação por classificação supera a por geração (Ouchebara e Dupont, preprint 2025).
- LoRA em modelo de código (WizardCoder 13B) superou baseline de codificador em detecção binária, com número reduzido de parâmetros treináveis (Shestov et al., 2024).
- Em dados realistas desbalanceados, a F1 do QLoRA por classificação pode despencar, ilustrando que a dificuldade está no desbalanceamento e no realismo, não só no método.

**Destilação.** Avatar comprime codificadores de código em ordens de grandeza de tamanho e energia mantendo desempenho competitivo em predição de vulnerabilidade, com perda pequena (Shi et al., 2023). Registra-se trade-off entre compressão e robustez adversarial, relevante em segurança.

**Lacuna na interseção:** quase não há trabalho que meça isoladamente o efeito da quantização (AWQ, GPTQ, NF4, GGUF) sobre a qualidade de classificação de vulnerabilidade (não geração), combinada a QLoRA, sob avaliação descontaminada. É o espaço mais promissor.

---

## 8. Lacunas de pesquisa

1. Efeito isolado da quantização na classificação de vulnerabilidade (VD-S, acurácia pareada), não sobre geração ou perplexidade.
2. QLoRA versus ajuste completo no mesmo modelo, sob avaliação descontaminada.
3. Modelo pequeno especializado por QLoRA versus modelo maior genérico: quantificar recuperação de desempenho e custo relativo.
4. Qual método de quantização melhor preserva a discriminação pareada vulnerável/corrigido.
5. Robustez de modelos quantizados a perturbações que preservam a semântica.
6. Trade-off entre eficiência e robustez adversarial em modelos comprimidos para uso de segurança.
7. Detecção descontaminada e eficiente em múltiplas linguagens (além de C/C++).
8. Benchmark de eficiência padronizado e reprodutível para a tarefa (memória, tokens por segundo, energia, custo por hora).

---

## 9. Roteiro recomendado em três estágios

**Estágio 1, Fundação (meses 1 a 2 do trabalho experimental).** Adotar PrimeVul e PrimeVul pareado como benchmark primário; adicionar um benchmark temporal recente para controlar contaminação. Nunca reportar só F1 em Big-Vul ou Devign. Métricas obrigatórias: F1 da classe vulnerável, VD-S, acurácia pareada e taxa de falsos positivos. Baselines: UniXcoder totalmente ajustado e um LLM pequeno em prompt.

**Estágio 2, QLoRA especializado (meses 3 a 5).** Ajustar por QLoRA (NF4 4 bits) com cabeça de classificação em Qwen2.5-Coder-7B, DeepSeek-Coder e StarCoder2. Responder à pergunta do modelo pequeno especializado versus maior genérico. Incluir teste de robustez semântica.

**Estágio 3, Quantização comparativa (meses 6 a 8).** Comparar AWQ, GPTQ, NF4 e GGUF sobre o modelo já ajustado, medindo VD-S e acurácia pareada (não perplexidade). Reportar todos os eixos de custo.

**Limiares que mudam a decisão:**
- Se o QLoRA-7B ficar mais de 5 pontos de VD-S abaixo do UniXcoder ajustado, pivotar para abordagem neuro-simbólica (estilo IRIS) ou RAG de conhecimento (Vul-RAG).
- Se a quantização de 4 bits degradar a acurácia pareada em mais de 3 pontos frente ao 16 bits, recomendar 8 bits como padrão de implantação.
- Se a acurácia pareada permanecer próxima do acaso mesmo após QLoRA, reenquadrar a contribuição como estudo de eficiência versus qualidade (o modelo pequeno quantizado é tão limitado quanto o grande, porém muito mais barato), que é em si um resultado publicável.

---

## 10. Metodologia de medição de eficiência

**Métricas a reportar:**
- Memória/VRAM: memória de carga (idle) mais pico durante inferência.
- Latência: tempo até o primeiro token (TTFT), tempo por token de saída (TPOT), latência total.
- Vazão: tokens por segundo.
- Energia: Joules por token e por resposta, potência média em watts, amostrando a potência da GPU via nvidia-smi ou pynvml.
- Custo: valor por hora da instância multiplicado pelo tempo de execução, como proxy reprodutível de custo total, útil quando não há telemetria de energia em nível de facility.

**Boas práticas:** fixar tamanho de lote (1 para serviço online), comprimento de entrada e saída, decodificação determinística; repetir várias vezes e reportar média e percentis; sempre registrar a instância exata (modelo de GPU e tier), porque o preço varia bastante entre tiers.

**Preços de referência RunPod (início de 2026, sujeitos a variação):** RTX 4090 24 GB a partir de cerca de 0,34 a 0,69 dólar por hora; A100 80 GB PCIe cerca de 1,39 dólar por hora; H100 80 GB PCIe cerca de 2,89 dólar por hora. Cobrança por segundo.

---

## 11. Ferramentas e frameworks

- Treino e PEFT: Hugging Face Transformers mais PEFT (LoRA/QLoRA), bitsandbytes (NF4 4 bits), TRL, Unsloth, Axolotl.
- Quantização: AutoGPTQ/GPTQModel, AutoAWQ, llama.cpp (GGUF), llm-compressor.
- Serviço e inferência: vLLM (PagedAttention, batching contínuo), SGLang, TGI.
- Avaliação: scikit-learn para métricas de classificação; scripts próprios para VD-S e avaliação pareada (o PrimeVul disponibiliza referência).
- Energia e eficiência: nvidia-smi, pynvml, Zeus.

---

## 12. Referências consultadas

As fontes consultadas são predominantemente artigos científicos e relatórios técnicos (não foram consultados livros). O status de revisão por pares está indicado. Recomenda-se verificar cada entrada no arXiv ou no Google Scholar antes do uso final, com atenção redobrada aos preprints recentes de 2025 e 2026.

### 12.1. Detecção de vulnerabilidade: métodos e modelos

- Zhou, Y.; Liu, S.; Siow, J.; Du, X.; Liu, Y. **Devign: Effective Vulnerability Identification by Learning Comprehensive Program Semantics via Graph Neural Networks.** NeurIPS, 2019. arXiv:1909.03496. [revisado por pares]
- Feng, Z. et al. **CodeBERT: A Pre-Trained Model for Programming and Natural Languages.** Findings of EMNLP, 2020. arXiv:2002.08155. [revisado por pares]
- Guo, D. et al. **GraphCodeBERT: Pre-training Code Representations with Data Flow.** ICLR, 2021. arXiv:2009.08366. [revisado por pares]
- Guo, D. et al. **UniXcoder: Unified Cross-Modal Pre-training for Code Representation.** ACL, 2022. arXiv:2203.03850. [revisado por pares]
- Li, Z.; Dutta, S.; Naik, M. **IRIS: LLM-Assisted Static Analysis for Detecting Security Vulnerabilities.** ICLR, 2025. arXiv:2405.17238. [revisado por pares]
- Du, X. et al. **Vul-RAG: Enhancing LLM-based Vulnerability Detection via Knowledge-level RAG.** 2024. arXiv:2406.11147; DOI:10.1145/3797277. [revisado por pares]
- Ullah, S. et al. **LLMs Cannot Reliably Identify and Reason About Security Vulnerabilities (SecLLMHolmes).** IEEE S&P, 2024. arXiv:2312.12575; DOI:10.1109/SP54263.2024.00210. [revisado por pares]
- Yin, X.; Ni, C.; Wang, S. **Multitask-based Evaluation of Open-Source LLM on Software Vulnerability.** IEEE Transactions on Software Engineering, 2024. arXiv:2404.02056; DOI:10.1109/TSE.2024.3470333. [revisado por pares]
- Zhou, X.; Zhang, T.; Lo, D. **Large Language Model for Vulnerability Detection: Emerging Results and Future Directions.** ICSE-NIER, 2024. arXiv:2401.15468. [revisado por pares]
- Shestov, A. et al. **Finetuning Large Language Models for Vulnerability Detection.** IEEE Access, 2025. arXiv:2401.17010; DOI:10.1109/ACCESS.2025.3546700. [revisado por pares]
- Yildiz, E. et al. **Benchmarking LLMs and LLM-based Agents in Practical Vulnerability Detection (JITVUL).** ACL, 2025. arXiv:2503.03586. [revisado por pares, verificar]
- Sheng, Z. et al. **Large Language Models in Software Security: A Survey of Vulnerability Detection Techniques and Insights.** ACM Computing Surveys, 2025. arXiv:2502.07049; DOI:10.1145/3769082. [revisado por pares, verificar]
- Gao, Z. et al. **How Far Have We Gone in Vulnerability Detection Using LLMs (VulBench).** 2023. arXiv:2311.12420. [preprint]
- Ouchebara, M.; Dupont, G. **Llama-based Source Code Vulnerability Detection: Prompt Engineering vs Fine Tuning.** 2025. arXiv:2512.09006. [preprint, verificar]
- **From Generalist to Specialist: Exploring CWE-Specific Vulnerability Detection.** 2024. arXiv:2408.02329. [preprint]
- **Do Fine-Tuned LLMs Understand Vulnerabilities? (Semantic Trap).** 2026. arXiv:2601.22655. [preprint, verificar]
- **Revisiting Vul-RAG: Reproducibility and Replicability.** 2026. arXiv:2606.04739. [preprint, verificar]
- **TREAT (avaliação de LLMs em detecção).** 2025. arXiv:2510.17163. [preprint, verificar]

### 12.2. Datasets e benchmarks

- Fan, J.; Li, Y.; Wang, S.; Nguyen, T. N. **A C/C++ Code Vulnerability Dataset with Code Changes and CVE Summaries (Big-Vul).** MSR, 2020, p. 508-512. [revisado por pares]
- Lu, S. et al. **CodeXGLUE: A Machine Learning Benchmark Dataset for Code Understanding and Generation.** NeurIPS Datasets and Benchmarks, 2021. arXiv:2102.04664. [revisado por pares]
- Chen, Y.; Ding, Z.; Alowain, L.; Chen, X.; Wagner, D. **DiverseVul: A New Vulnerable Source Code Dataset for Deep Learning Based Vulnerability Detection.** RAID, 2023. arXiv:2304.00409. [revisado por pares]
- Ding, Y. et al. **Vulnerability Detection with Code Language Models: How Far Are We? (PrimeVul).** ICSE, 2025. arXiv:2403.18624. [revisado por pares]
- Ni, C. et al. **MegaVul: A C/C++ Vulnerability Dataset with Comprehensive Code Representations.** MSR, 2024. arXiv:2406.12415; DOI:10.1145/3643991.3644886. [revisado por pares]
- Wang, X. et al. **ReposVul: A Repository-Level High-Quality Vulnerability Dataset.** ICSE (Industry), 2024. DOI:10.1145/3639478.3647634. [revisado por pares]
- Ahmed, S. et al. **SecVulEval: Benchmarking LLMs for Real-World C/C++ Vulnerability Detection.** 2025. arXiv:2505.19828. [preprint, verificar]
- Li, Y. et al. **CleanVul: Automatic Function-Level Vulnerability Detection using LLM Heuristics.** 2024. arXiv:2411.17274. [preprint, verificar]

### 12.3. Eficiência: quantização, PEFT e destilação

- Frantar, E.; Ashkboos, S.; Hoefler, T.; Alistarh, D. **GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers.** ICLR, 2023. arXiv:2210.17323. [revisado por pares]
- Lin, J. et al. **AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration.** MLSys, 2024. arXiv:2306.00978. [revisado por pares]
- Xiao, G. et al. **SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models.** ICML, 2023. arXiv:2211.10438. [revisado por pares]
- Hu, E. et al. **LoRA: Low-Rank Adaptation of Large Language Models.** ICLR, 2022. arXiv:2106.09685. [revisado por pares]
- Dettmers, T.; Pagnoni, A.; Holtzman, A.; Zettlemoyer, L. **QLoRA: Efficient Finetuning of Quantized LLMs.** NeurIPS, 2023. arXiv:2305.14314. [revisado por pares]
- Wu, X. et al. **Understanding INT4 Quantization for Transformer Models.** ICML, 2023. arXiv:2301.12017. [revisado por pares]
- Wei, X. et al. **Towards Greener Yet Powerful Code Generation via Quantization.** ESEC/FSE, 2023. arXiv:2303.05378; DOI:10.1145/3611643.3616302. [revisado por pares]
- Shi, J. et al. **Greening Large Language Models of Code (Avatar).** 2023. arXiv:2309.04076. [preprint]
- Gao, X. et al. **Resource-Efficient Automatic Software Vulnerability Assessment (PSO-KDVA).** Engineering Applications of Artificial Intelligence, 2025. arXiv:2508.02840. [revisado por pares, verificar]

### 12.4. Modelos de código

- Hui, B. et al. **Qwen2.5-Coder Technical Report.** 2024. arXiv:2409.12186. [relatório técnico]
- Lozhkov, A. et al. **StarCoder 2 and The Stack v2: The Next Generation.** 2024. arXiv:2402.19173. [relatório técnico]
- Mishra, M. et al. **Granite Code Models: A Family of Open Foundation Models for Code Intelligence.** 2024. arXiv:2405.04324. [relatório técnico]
- DeepSeek-AI. **DeepSeek-Coder-V2: Breaking the Barrier of Closed-Source Models in Code Intelligence.** 2024. arXiv:2406.11931. [relatório técnico]

### 12.5. Infraestrutura de inferência e medição de eficiência

- Kwon, W. et al. **Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM).** SOSP, 2023. arXiv:2309.06180. [revisado por pares]
- **TokenPowerBench: Benchmarking Power Consumption of LLM Inference.** 2025. arXiv:2512.03024. [preprint, verificar]

---

## 13. Ressalvas importantes

- **Revisão por pares versus preprint.** As entradas marcadas [preprint] ou [verificar] ainda não passaram por revisão por pares ou não foram confirmadas de forma independente nesta consolidação. Vários achados que sustentam a hipótese central (por exemplo, os números de QLoRA com cabeça de classificação em Ouchebara e Dupont, 2025) vêm de preprints com um único split de dataset e sem intervalos de confiança. Confirme cada um antes de citar e, idealmente, reproduza os números você mesmo.
- **Contaminação e reprodutibilidade.** Muitos números altos de F1 na literatura vêm de datasets contaminados e não se reproduzem sob avaliação rigorosa (a queda de 68,26% para 3,09% de F1 é o exemplo canônico). Números de modelos proprietários variam por não-determinismo e por versão de API, e não são replicáveis a longo prazo.
- **Datas e identificadores.** Alguns identificadores arXiv de 2026 foram coletados por pesquisa automatizada e podem conter imprecisão de numeração; confira o identificador junto ao título e aos autores.
- **Preços de GPU.** São instantâneos de início de 2026 e flutuam; o tier (Secure versus Community) pode alterar bastante o valor.
- **Formatação institucional.** Se o PPGCC exigir formulário de projeto ou padrão ABNT específico, o modelo oficial prevalece sobre a organização adotada aqui.
- **Escopo deste registro.** Este documento consolida o que foi definido em conversa mais um levantamento de literatura. É base de trabalho, não um texto final de qualificação; a redação definitiva deve passar pela leitura direta das fontes e pela orientação.
