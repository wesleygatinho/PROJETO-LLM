# Prompt para verificação independente de originalidade (Recorte A)

> **Como usar:** copie TUDO que está entre as linhas `===== INÍCIO DO PROMPT =====` e
> `===== FIM DO PROMPT =====` e cole numa IA com busca na web ativada
> (ChatGPT com Search/Deep Research, Gemini com Deep Research, Perplexity Pro, Grok DeepSearch, Claude com web search).
> Se a ferramenta tiver modo "deep research", use-o. Rode em pelo menos **duas** IAs diferentes e compare os resultados.

---

===== INÍCIO DO PROMPT =====

# TAREFA

Você é um **revisor cético e adversarial** de uma proposta de mestrado. Seu trabalho **não** é elogiar nem confirmar: é **tentar destruir a alegação de originalidade** deste trabalho, encontrando literatura que já tenha feito, total ou parcialmente, o que ele propõe. Assuma como hipótese de partida que **alguém já fez isso e eu simplesmente não achei**. Sua meta é achar esse trabalho. Se depois de uma busca honesta e exaustiva você não achar, aí sim relate a ausência — mas relate como "não encontrei", nunca como "não existe".

Data de hoje: **14 de setembro de 2026**. Sua busca precisa cobrir publicações até esta data, com ênfase em 2024–2026 (a área se move muito rápido; preprints de 2025 e 2026 são especialmente importantes).

Use busca na web de forma intensiva e iterativa: refine as consultas com base no que encontrar, siga as citações, e não se contente com a primeira página de resultados.

---

# CONTEXTO: O TRABALHO A SER AUDITADO

## Resumo em uma frase

Estudo empírico do **trade-off custo × qualidade** na **detecção de vulnerabilidades em código** com LLMs de código, isolando o efeito do **método de quantização** e do **ajuste fino barato (QLoRA)**, sob **avaliação descontaminada** (PrimeVul, incluindo o subconjunto pareado).

## Detalhamento técnico (leia com atenção — a precisão importa para a busca)

**Tarefa:** classificação binária em **nível de função** ("esta função é vulnerável? sim/não"), em **C/C++**. Não é geração de código, não é reparo automático (APR), não é localização em nível de instrução (statement-level), não é análise inter-procedural ou de repositório.

**Dados:** **PrimeVul** (Ding et al., ICSE 2025) como benchmark primário, incluindo o **PrimeVul-Paired** (cada função vulnerável pareada com sua versão corrigida pelo commit de fix). Contraste com um benchmark antigo/contaminado (Big-Vul ou Devign) apenas para demonstrar o efeito da contaminação.

**Modelos:** decoders de código abertos na faixa de 3B–7B — **Qwen2.5-Coder** (3B e 7B), **StarCoder2-7B**, **DeepSeek-Coder-6.7B** (denso) — mais um baseline encoder pequeno totalmente ajustado, **UniXcoder-125M**.

**Compressão / eficiência (o núcleo):** comparar precisão de **16 bits** contra **4 bits weight-only (regime W4A16)** por três métodos distintos: **NF4 (bitsandbytes)**, **AWQ** e **GPTQ**. GGUF/llama.cpp fica como estudo separado (CPU/edge). O ponto é medir o efeito **do método de quantização**, não apenas "quantizado vs. não quantizado".

**Ajuste fino:** **QLoRA** com **cabeça de classificação** (classification head sobre o decoder, produzindo score contínuo), **não** geração de texto. Sob o **desbalanceamento real** do PrimeVul (~2% de positivos), sem balanceamento artificial das classes. Pipeline de custo honesto: QLoRA(NF4) treina o adaptador → **merge** → **PTQ** (AWQ/GPTQ/INT8) do modelo final, para medir o custo real de inferência (nunca reportar o custo do "QLoRA cru", que não acelera inferência). QA-LoRA como variante comparativa.

**Métricas de qualidade:** F1 da classe vulnerável, FPR, **VD-S** (taxa de falsos negativos sob FPR ≤ 0,5%) e **acurácia pareada** com os quatro desfechos P-C / P-V / P-B / P-R (acaso = 25% de P-C).

**Métricas de custo:** VRAM de carga e de pico, TTFT, TPOT, tokens/s, **energia (J/token, W médio via NVML/pynvml)** e **US$ por inferência** (preço/hora da instância × tempo).

**Entregável central:** uma **curva de trade-off custo × qualidade** com o "joelho" identificado e uma recomendação prática de implantação; mais a comparação entre métodos de quantização; mais (secundário) um teste de **robustez a perturbações que preservam a semântica** aplicado aos **modelos quantizados**.

**Enquadramento explícito (importante para a auditoria):** o trabalho **não aposta** que o modelo pequeno quantizado supere o grande em qualidade. Parte da premissa — extraída da literatura de 2025–2026 — de que **sob avaliação pareada descontaminada quase todos os modelos ficam perto do acaso**, e portanto o valor está em **caracterizar o custo para uma qualidade reconhecidamente limitada**.

## Resultados preliminares já obtidos (setembro de 2026)

Em zero-shot, 16 bits, no teste completo do PrimeVul (24.788 funções, 549 vulneráveis):

- Qwen2.5-Coder-3B-Instruct: F1 0,113 · FPR 3,5% · P-C pareado 3,7% (16/433 pares)
- Qwen2.5-Coder-7B-Instruct: F1 0,051 · FPR 10,9% · P-C pareado 2,3% (10/433 pares)
- Os dois modelos acertam 83 vulneráveis cada, mas só 19 são as mesmas; nenhum par pareado em comum. O modelo maior consome 2,3× a VRAM para ficar pior.

---

# AS ALEGAÇÕES QUE VOCÊ DEVE TENTAR REFUTAR

Trate cada uma como uma hipótese a ser falseada. Para cada uma, busque ativamente contraexemplos.

**C1 — [núcleo da originalidade]** *Ninguém mediu isoladamente o efeito do **método** de quantização (AWQ vs. GPTQ vs. NF4 vs. GGUF) sobre a **qualidade de classificação de vulnerabilidade** — medida por VD-S e/ou acurácia pareada — sob avaliação descontaminada.*
→ Contraexemplo seria: qualquer trabalho que compare métodos de quantização numa tarefa de detecção/classificação de vulnerabilidade, mesmo com métricas diferentes, mesmo em outra linguagem de programação, mesmo em outro benchmark.

**C2** *Ninguém publicou uma curva de trade-off custo × qualidade (VRAM / latência / energia / US$ contra F1 ou VD-S ou acurácia pareada) para detecção de vulnerabilidade com LLMs sob avaliação descontaminada.*
→ Contraexemplo: qualquer trabalho que reporte custo de inferência **junto com** qualidade de detecção, incluindo relatórios industriais e benchmarks de eficiência.

**C3** *O comportamento de QLoRA com **cabeça de classificação** (não geração), em decoders de código, sob desbalanceamento realista, é pouco medido.*
→ Contraexemplo: papers de PEFT/LoRA/QLoRA aplicados a vulnerability detection; especialmente os que usam classification head em vez de prompting.

**C4** *Ninguém cruzou **robustez a perturbações que preservam a semântica** (protocolo de Risse & Böhme, ou SecLLMHolmes) com **modelos quantizados**.*
→ Contraexemplo: qualquer estudo sobre o efeito de compressão (quantização, poda, destilação) na robustez de modelos de código, mesmo em outra tarefa.

**C5 — [premissa, não contribuição]** *Sob avaliação pareada descontaminada, praticamente todos os modelos (inclusive ajustados) ficam perto do acaso (~25% de P-C), e o fine-tuning não fecha essa lacuna.*
→ **Esta é a alegação mais perigosa para o trabalho.** Se alguém já resolveu a detecção pareada — atingindo, digamos, P-C acima de 50–60% de forma reprodutível — o enquadramento inteiro ("todo mundo vai mal, então o valor está no custo") desaba. Busque com afinco qualquer resultado recente que quebre esse teto.

**C6** *PrimeVul (+ pareado + VD-S) continua sendo a escolha de benchmark defensável em setembro de 2026.*
→ Contraexemplo: um benchmark mais novo, mais limpo ou mais aceito que tenha tornado o PrimeVul obsoleto, ou que corrija problemas conhecidos dele (por exemplo, ruído de rótulo remanescente).

---

# O QUE EU **JÁ** CONHEÇO (não me devolva isso como novidade)

Se encontrar estes trabalhos, cite-os apenas para contextualizar. O que me interessa é o que **não** está nesta lista.

- **Benchmarks e contaminação:** PrimeVul (Ding et al., ICSE 2025) · Big-Vul · Devign/CodeXGLUE · DiverseVul · ReVeal (Chakraborty et al., TSE 2021) · CleanVul · SecVulEval (Ahmed et al., 2025) · MegaVul · CWE-Bench-Java
- **Limites dos LLMs em detecção:** Risse & Böhme (USENIX Security 2024) · SecLLMHolmes / Ullah et al. (IEEE S&P 2024) · Steenhoek et al. (2024) · TREAT / Gao, S. et al. (2025) · Huang et al. 2026 ("Semantic Trap") · Kaniewski, Schmidt & Heer (2026, reprodutibilidade do Vul-RAG)
- **Métodos que melhoram:** IRIS (Li, Dutta & Naik, ICLR 2025) · Vul-RAG (Du et al., 2024/2025; benchmark PairVul) · LineVul (MSR 2022) · VulDeePecker (NDSS 2018)
- **Quantização e PEFT:** QLoRA (Dettmers et al., NeurIPS 2023) · LLM.int8() (NeurIPS 2022) · GPTQ (ICLR 2023) · AWQ (MLSys 2024) · SmoothQuant · QA-LoRA · survey de LoRA (Mao et al., FCS 2024) · survey de quantização (Gholami et al.) · Wu et al. (robustez sob quantização em encoders, regime W4A4)
- **Eficiência/energia:** TokenPowerBench (Niu et al., 2025) · Zeus (NSDI 2022) · Wei et al. (ESEC/FSE 2023, modelo de 6B em laptop) · Ouchebara & Dupont (2025, QLoRA com dados balanceados)

---

# COMO BUSCAR

## Fontes a varrer (não se limite ao Google Scholar)

arXiv (cs.SE, cs.CR, cs.LG, cs.CL) · Google Scholar · Semantic Scholar · DBLP · ACM Digital Library · IEEE Xplore · USENIX · NDSS · OpenReview (ICLR/NeurIPS — inclua os **rejeitados**, um paper rejeitado ainda escoopa) · Papers With Code · Hugging Face (model cards, datasets, blog) · GitHub (READMEs de repositórios de pesquisa) · teses e dissertações (ProQuest, repositórios institucionais, bibliotecas de universidades europeias e asiáticas, BDTD no Brasil) · blogs técnicos de empresas de segurança e de MLOps · relatórios industriais (Snyk, Semgrep, GitHub Security Lab, Veracode, Google/DeepMind, Meta, NVIDIA) · workshops (MSR, SCAM, ICSE-SEIP, DIMVA, WOOT, AIware, LLM4Code, Deep Learning for Code) · Zenodo/OSF.

## Consultas sugeridas (rode variações, em inglês e também em português e chinês)

**Eixo quantização × detecção de vulnerabilidade:**

- "quantization" + "vulnerability detection" + LLM
- "AWQ" OR "GPTQ" OR "bitsandbytes" OR "NF4" + "vulnerability detection"
- "quantized LLM" + "code security" / "static analysis" / "bug detection"
- "4-bit" + "code model" + "classification" + performance degradation
- "efficient" + "vulnerability detection" + "resource-constrained" / "edge" / "on-premise"
- "impact of quantization on downstream task" + code

**Eixo custo × qualidade:**

- "cost-effectiveness" OR "cost-quality trade-off" + "LLM" + "vulnerability detection"
- "energy consumption" + "code LLM" + inference + security task
- "inference cost" + "security" + "large language model" + benchmark
- "green AI" + "software security" / "vulnerability"
- "dollars per" OR "cost per detection" + LLM + security

**Eixo PEFT/QLoRA para classificação:**

- "QLoRA" + "vulnerability detection"
- "LoRA" + "sequence classification" + "code" + "imbalanced"
- "parameter-efficient fine-tuning" + "vulnerability" + "class imbalance"
- "classification head" + "decoder" + "code" + vulnerability

**Eixo avaliação pareada / descontaminada (verificar se alguém quebrou o teto — C5):**

- "PrimeVul" (busque **todos** os papers que citam PrimeVul e varra-os)
- "paired accuracy" OR "pairwise" + "vulnerability" + "patch"
- "VD-S" + vulnerability detection score
- "vulnerable" "patched" "distinguish" + LLM
- state of the art PrimeVul 2026 leaderboard

**Eixo robustez × compressão:**

- "quantization" + "robustness" + "code model" / "semantic-preserving transformations"
- "compressed model" + "adversarial robustness" + "source code"
- "pruning" OR "distillation" + "vulnerability detection"

**Busca reversa (procure o *resultado*, não o método):** procure por qualquer tabela publicada que contenha, ao mesmo tempo, uma coluna de qualidade de detecção e uma coluna de VRAM/latência/energia/custo.

## Rastreamento de citações (faça isso — é onde mora o risco real)

1. Liste os trabalhos que **citam o PrimeVul** (ICSE 2025) e varra-os procurando quantização, eficiência ou custo.
2. Faça o mesmo para **Risse & Böhme (2024)**, **SecLLMHolmes (2024)** e **Vul-RAG**.
3. Faça o caminho inverso: pegue papers recentes de **quantização aplicada a modelos de código** e veja se algum deles avalia tarefa de segurança.
4. Verifique se existe **survey de 2025–2026** sobre "efficient LLMs for software engineering" ou "LLMs for vulnerability detection". Um survey recente é o lugar mais provável onde essa interseção já estaria mapeada. Se existir, leia a seção de lacunas dele e me diga se ela coincide com as minhas ou as contradiz.

---

# REGRAS DE HONESTIDADE (obrigatórias)

1. **Nunca invente uma referência.** Cada trabalho citado precisa vir com **URL funcional** que você efetivamente abriu. Se não conseguiu abrir, marque `[NÃO VERIFICADO]`.
2. **Não invente IDs de arXiv, DOIs, números de página ou métricas.** Se um número não estiver no texto que você leu, escreva "não reportado".
3. Se a busca não retornar nada para um eixo, **diga isso explicitamente** e liste as consultas que rodou, para que a ausência seja auditável.
4. Distinga com clareza **o que você leu** (paper inteiro? só o abstract? só o título no resultado de busca?) de **o que você inferiu**.
5. Marque cada item como **revisado por pares** ou **preprint/não revisado**.
6. Não confunda tarefas: um paper sobre *geração* de código quantizada, ou sobre *reparo* de vulnerabilidade, **não** é o mesmo que *classificação* de vulnerabilidade — mas ainda assim me interessa, desde que classificado corretamente como adjacente.

---

# FORMATO DA RESPOSTA

## Parte 1 — Veredito executivo (máximo 10 linhas)

Responda direto: **a alegação de originalidade se sustenta em setembro de 2026?** Use uma destas etiquetas e justifique em uma frase:
`ORIGINALIDADE INTACTA` · `ORIGINALIDADE ERODIDA` (alguém chegou perto) · `PARCIALMENTE ESCOOPADO` · `ESCOOPADO` (alguém já fez).

## Parte 2 — Tabela de candidatos

Para cada trabalho relevante encontrado:

| Trabalho (autores, ano) | Venue / status | Link | O que faz | Sobreposição com C1–C6 | Veredito | O que AINDA fica livre |
|---|---|---|---|---|---|---|

Vereditos possíveis: `ESCOOPA` · `SOBREPÕE PARCIALMENTE` · `ADJACENTE` · `SÓ CONTEXTO`.
Ordene do mais ameaçador para o menos ameaçador.

## Parte 3 — Veredito por alegação

Para **cada uma** de C1 a C6, separadamente:

- Veredito: `SUSTENTA` / `ENFRAQUECIDA` / `REFUTADA`
- Evidência (com links)
- Confiança: alta / média / baixa — e **por quê** (baseado na qualidade da cobertura da busca, não em achismo)

## Parte 4 — O ataque mais forte

Responda em texto corrido: **"Se eu fosse um membro de banca determinado a rejeitar este trabalho por falta de originalidade, qual seria o meu melhor argumento, e qual referência eu usaria?"** Seja duro. Se o melhor ataque disponível for fraco, diga que é fraco e explique por quê.

## Parte 5 — Riscos adjacentes

- Algum benchmark, modelo ou técnica **tornou esta proposta desatualizada** entre 2025 e set/2026? (ex.: PrimeVul superado; modelos de raciocínio que mudaram o patamar; novo formato de quantização dominante)
- Há **problemas conhecidos com o PrimeVul** (versões v0.1 vs. v1.0, ruído de rótulo, espelhos no Hugging Face com contagens divergentes do artigo original) que eu deveria saber?
- A premissa C5 ainda vale, ou 2026 produziu algum resultado que quebrou o teto da avaliação pareada?

## Parte 6 — Oportunidades

Se, durante a busca, você identificar uma **lacuna melhor ou mais defensável** vizinha a esta proposta, descreva-a em até 5 linhas, com a referência que a sustenta. Não invente lacunas para agradar; só liste se encontrou evidência.

## Parte 7 — Rastro de auditoria

Liste **todas** as consultas que você efetivamente rodou e as bases que consultou, para eu poder repetir e conferir. Diga explicitamente o que você **não conseguiu** acessar (paywall, fora do índice, etc.).

===== FIM DO PROMPT =====
