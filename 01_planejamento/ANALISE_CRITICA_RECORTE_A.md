# Análise crítica e verificação de fontes — RECORTE A (dossiê completo)

Documento de trabalho gerado pela leitura integral do dossiê `RECORTE_A_dossie_completo.md`
e verificação, uma a uma, contra os 41 papers em markdown em `pdf_to_markdown/markdown_output`.

Legenda de status de verificação:
- ✅ CONFIRMADO — a afirmação do dossiê bate com a fonte (número/fato conferido).
- 🟡 IMPRECISO — a ideia geral está certa, mas há erro de detalhe, simplificação enganosa ou atribuição frouxa.
- 🔴 DISCREPANTE / A CORRIGIR — número, autoria, ano ou afirmação em conflito com a fonte.
- ⚠️ NÃO VERIFICÁVEL AQUI — a fonte não traz o dado no markdown extraído (checar PDF/arXiv).

---

## PARTE I — Verificação das afirmações numéricas centrais

### 1. PrimeVul (Ding, Y. et al., 2024/2025) — arquivo `Datasets e benchmarks/Ding, Y - 2024.md`

Fonte confere quase perfeitamente com o dossiê. É o pilar factual do "gancho científico".

| Afirmação no dossiê | Fonte (PrimeVul) | Status |
|---|---|---|
| StarCoder2 7B: 68,26% F1 no Big-Vul → 3,09% no PrimeVul | Abstract e §V: "68.26% F1 on BigVul but only 3.09% F1 on PRIMEVUL" (StarCoder2 7B) | ✅ CONFIRMADO (número exato) |
| VD-S = FNR sob FPR ≤ 0,5% | §IV-B1: "VD-S ... FNR @ (FPR ≤ r), r = 0.5%" | ✅ CONFIRMADO |
| Avaliação pareada com 4 desfechos (ambos corretos, ambos vuln., ambos benignos, invertido) | Tabela V: colunas P-C, P-V, P-B, P-R (Pair-Correct/Vuln/Benign/Reversed) | ✅ CONFIRMADO |
| DiverseVul ~60% de acurácia de rótulo após dedup | Tabela I: DiverseVul 60,0% | ✅ CONFIRMADO |
| Big-Vul rótulos imprecisos "parcela expressiva" | Tabela I: BigVul 25,0% correto | ✅ CONFIRMADO (bem pior que "expressiva": só 25% correto) |
| Devign/CodeXGLUE herda problemas | Tabela I: CodeXGLUE 24,0% correto | ✅ CONFIRMADO |
| Modelos proprietários (GPT-4) ~ palpite aleatório sob avaliação pareada | §V-D / abstract: "GPT-4 com CoT não supera o palpite aleatório" na avaliação pareada | ✅ CONFIRMADO |
| Divisão temporal (cronológica) | §IV-A: split cronológico 80/10/10 por data de commit | ✅ CONFIRMADO |

Dados adicionais úteis à dissertação (não estavam no dossiê, valem citar):
- Escala do PrimeVul: **6.968 vulneráveis + 228.800 benignas, 140 CWEs, 755 projetos, 6.827 commits**.
- Split de teste: 695 vuln / 25.216 benignas (all); 564/564 (paired). Razão vuln:benigno ≈ **1:32**.
- Duas técnicas de rotulagem: PRIMEVUL-ONEFUNC (86% correto) e PRIMEVUL-NVDCHECK (92%), ~ SVEN (94%, manual).
- Técnicas avançadas (class weights, contrastive learning) dão ganho **marginal**: VD-S/FNR oscila ~90%.
- **Nuance importante:** o próprio PrimeVul defende que **F1 também engana** (não só a acurácia) por ser insensível à assimetria FP/FN. O dossiê (seção 3 e 7.3) trata F1 como "métrica principal" na Etapa 1 mas depois relativiza — coerente, mas convém deixar explícito que a fonte primária critica F1, reforçando VD-S.

### 2. Ouchebara & Dupont (2025) — arquivo `Deteccao.../Ouchebara, M - 2025.md`

É a fonte que mais sustenta a hipótese central (QLoRA + cabeça de classificação). Verificação detalhada:

| Afirmação no dossiê (linhas 160-162) | Fonte | Status |
|---|---|---|
| QLoRA c/ cabeça de classificação iguala codificadores em conjuntos fáceis (F1 alto no Big-Vul) | F1 classe vuln. 0,95 vs UniXcoder 0,94 no BigVul (Double FT); "slightly better" | ✅ CONFIRMADO |
| No PrimeVul apenas empata com os codificadores | Double FT: F1 médio 0,77 = UniXcoder (0,77); vuln-F1 0,79 vs 0,77; AUC 0,842 = UniXcoder | ✅ CONFIRMADO |
| Classificação supera geração | "classifier fashion ... more effective than the generative fashion" | ✅ CONFIRMADO |
| Preprint com split único e sem IC | "all metrics ... based on one dataset split ... will include confidence intervals in future" | ✅ CONFIRMADO (ressalva do dossiê é literalmente correta) |
| "Em dados realistas desbalanceados, a F1 do QLoRA por classificação pode despencar" | O paper **balanceou** os dados (undersampling). A queda no PrimeVul (0,74) é da cabeça de classificação; a fashion **generativa** é que despenca (0,57) | 🟡 IMPRECISO |

**Observações críticas para a dissertação:**
1. **O "modelo pequeno" de Ouchebara é Llama-3.1 8B**, e os baselines são encoders de **125M** (CodeBERT/UniXcoder). Ou seja, o LLM "pequeno" é ~64× MAIOR que o encoder que ele apenas empata. Isso *fortalece* o argumento do dossiê de que UniXcoder é baseline forte, mas o enquadramento "modelo pequeno especializado alcança modelo grande" precisa de cuidado: aqui é "LLM de 8B empata encoder de 125M", o oposto de economia de parâmetros.
2. A afirmação de "despencar em desbalanceado" (linha 162) **não é testada por Ouchebara** (que balanceou). Se o dossiê quer sustentar isso, precisa de outra fonte ou de experimento próprio. Marcar como lacuna, não como achado.
3. Hiperparâmetros QLoRA úteis (replicáveis): 4-bit, r=16, alpha=8, target q/k/v/o_proj, lr 2e-4, 4 épocas, batch 16, GPU RTX 6000 Ada 40GB. Bom ponto de partida para a Etapa 3.
4. Título confere. **arXiv:2512.09006 do dossiê ⚠️ NÃO VERIFICÁVEL** no markdown — conferir (dez/2025 é plausível).

### 3. IRIS (Li, Z.; Dutta; Naik — ICLR 2025) — arquivo `Deteccao.../Li, Z - 2025.md`

Todas as afirmações do dossiê (seção 7.2) conferem exatamente:

| Afirmação no dossiê | Fonte (IRIS) | Status |
|---|---|---|
| CWE-Bench-Java: 120 vulnerabilidades em Java | Fig.5: 120 vuln (CWE-22:55, 78:13, 79:31, 94:21) | ✅ CONFIRMADO |
| GPT-4 detecta 55, análise estática (CodeQL) detecta 27 | Tabela 1: CodeQL 27, IRIS+GPT-4 55 (+28) | ✅ CONFIRMADO |
| Melhora a taxa média de falsas descobertas | AvgFDR 90,03% → 84,82% (−5,21 pts com GPT-4) | ✅ CONFIRMADO |
| Bom desempenho com modelo aberto de 7B, detectando 52 | Tabela 1: DeepSeekCoder 7B = 52 detectadas | ✅ CONFIRMADO |
| Descobriu vulnerabilidades antes desconhecidas | §5.3: 4 novas (3 CWE-22, 1 CWE-94) | ✅ CONFIRMADO |

Observações: (a) IRIS é neuro-simbólico (LLM + CodeQL/análise de taint), a nível de **repositório inteiro** e em **Java** — fora do escopo C/C++/função do Recorte A, mas é o "plano B" citado no limiar do Estágio 2 (linha 192). (b) Nuance para citar com cuidado: mesmo IRIS+GPT-4 tem **AvgF1 baixíssima (0,177)** e AvgFDR ainda ~85% — "detecta mais" mas com muito ruído. Reforça o argumento de dificuldade. (c) Ano coerente (arXiv 2405.17238 de 2024, publicado ICLR 2025).

### 4. Vul-RAG (Du, X. et al., 2024/2025) — arquivo `Deteccao.../Du, X - 2025.md`

| Afirmação no dossiê (linha 129) | Fonte (Vul-RAG) | Status |
|---|---|---|
| "eleva a acurácia pareada em cerca de 16 a 24% **relativos**" | Abstract/§RQ3: +16–24 de pair accuracy em **pontos percentuais absolutos** (GPT-4o 0,08→0,32; Claude 0,06→0,27; Qwen 0,07→0,26; DeepSeek 0,14→0,30) | 🔴 A CORRIGIR: são **pontos percentuais absolutos**, não "relativos". Em termos relativos o ganho é bem MAIOR (2–4×). |
| LLMs mal distinguem vulnerável de corrigido | Tabela 1: pair acc. 0,06–0,14 (86%–94% de erro) | ✅ CONFIRMADO |

Dados de apoio: benchmark próprio **PairVul** (586 pares, Top-10 CWEs, Linux kernel); acaso pareado = 0,25; detecção manual 60%→77%; 10 bugs inéditos no kernel (6 CVEs). Base de conhecimento com GPT-3.5, retrieval BM25 + RRF.
**Atenção metodológica:** PairVul e a base de conhecimento vêm do mesmo domínio (CVEs do Linux kernel) — risco de sobreposição de distribuição, exatamente o que Kaniewski 2026 questiona.

### 5. SecLLMHolmes (Ullah, S. et al., IEEE S&P 2024) — arquivo `Deteccao.../Ullah, S - 2024.md`

| Afirmação no dossiê (linha 132) | Fonte | Status |
|---|---|---|
| Renomear função/variável → erro em ~26% dos casos | Abstract: "changing function or variable names ... incorrect answers in 26% ... of cases" | ✅ CONFIRMADO (exato) |
| Adição de funções de biblioteca → ~17% | Abstract: "addition of library functions ... 17%" | ✅ CONFIRMADO (exato) |
| Respostas não-determinísticas e raciocínio infiel | §4.1 (não-determinismo em todos os modelos) e §4.4 (faithful reasoning) | ✅ CONFIRMADO |

Dados de apoio: framework SecLLMHolmes, **228 cenários** (48 hand-crafted + 30 CVEs reais de 2023 + 150 aumentados), 8 LLMs, 8 CWEs críticos, C e Python. Melhor acurácia (GPT-4) 89,5% no conjunto hand-crafted, mas alto FPR e falha em CVEs reais. Publicado IEEE S&P 2024 (meta-review confirma). Nota do próprio comitê: dataset de CVEs reais pequeno (15 CVEs) e 150/228 são aumentações — limitação a mencionar. Atribuição e ano ✅.

### 6. Estudo de reprodutibilidade Vul-RAG (Kaniewski, S.; Schmidt; Heer — 2026) — arquivo `Deteccao.../Sabrina Kaniewski - 2026.md`

Mapeia a referência do dossiê "Revisiting Vul-RAG" (arXiv:2606.04739). **Autores ausentes no dossiê — adicionar: Kaniewski, S.; Schmidt, F.; Heer, T. (Esslingen University, Alemanha).**

| Afirmação no dossiê (linha 129) | Fonte | Status |
|---|---|---|
| Platô ~0,30 de acurácia pareada com modelos abertos | Abstract: "performance plateau at approximately 0.30 pairwise accuracy" | ✅ CONFIRMADO |
| Pouco acima do acaso (0,25) | acaso pareado = 0,25; modelos ficam 0,22–0,30 | ✅ CONFIRMADO |
| Modelo de 4B igualando um de 30B | RQ5: "Smaller models (4B-8B) achieve results comparable to larger 30B-32B models, and in some cases even outperform them" (Qwen3-4B 0,25 ≈ Qwen3-Coder-30B 0,28) | ✅ CONFIRMADO |

Nota: só reproduzível para Qwen2.5-Coder; DeepSeek-Coder-V2 NÃO reproduziu (limite de memória). Reforça a ressalva do dossiê sobre reprodutibilidade. Modelos de raciocínio (QwQ-32B, R1-32B) chegam a 0,29 mas com custo de tokens 2,6× maior — útil para o eixo custo×qualidade do Recorte A.

### 7. Semantic Trap (Huang, Feiyang et al., 2026) — arquivo `Deteccao.../Feiyang Huang - 2026.md`

Mapeia "Do Fine-Tuned LLMs Understand Vulnerabilities? An Investigation into the Semantic Trap" (arXiv:2601.22655). **Autores: Huang, F.; Sun, Y.; Zhang, F.; Yang, Z.; Liu, H.; Liu, Y.**

| Afirmação no dossiê (linha 134) | Fonte | Status |
|---|---|---|
| Modelos ajustados atingem F1 alto sem entender a causa-raiz | Abstract: "deceptively high scores on unpaired data (V2N) while failing under all three symptoms"; "pattern discriminator" | ✅ CONFIRMADO |
| "associando **domínios funcionais (gestão de memória, protocolos de rede)** à probabilidade de vulnerabilidade" | O paper fala em "functional patterns / surface-level features shared across functionally similar code" e distância textual (CodeBLEU) — **não** cita "gestão de memória / protocolos de rede" | 🟡 IMPRECISO: os exemplos específicos ("gestão de memória, protocolos de rede") não estão na fonte; o mecanismo real é "padrão funcional/textual (CodeBLEU) V2P vs V2N". Reescrever sem os exemplos inventados. |

Contribuições reais (citáveis): três sintomas do "Semantic Trap" — (i) desempenho sensível ao pareamento (V2P vs V2N), (ii) decisão ditada pelo *gap* textual (CodeBLEU, Spearman |ρ|<0,1, p<0,05), (iii) fragilidade a perturbações que preservam a semântica. SFT com CoT reduz os sintomas mas custa revocação. 5 LLMs (Qwen, Llama, DeepSeek). É a fonte mais forte para a lacuna 5 do dossiê (robustez).

### 8. TREAT (Gao, Shuzheng et al., 2025) — arquivo `Deteccao.../Shuzheng Gao - 2025.md`

Mapeia "TREAT: A Code LLMs Trustworthiness/Reliability Evaluation and Testing Framework" (arXiv:2510.17163). **Autores ausentes no dossiê — adicionar: Gao, S.; Li, E. J.; Lam, M. H. et al. (CUHK).**

| Afirmação no dossiê (linha 135) | Fonte | Status |
|---|---|---|
| Viés conservador: alta precisão mas revocação muito baixa | §C.7: "trade-off between high precision and low recall in several models" | ✅ CONFIRMADO (observação qualitativa; o paper diz "several models", não especificamente "abertos grandes" — suavizar o "abertos grandes") |

Nota: TREAT usa **PrimeVul e PrimeVul-Paired** (amostra de 200 funções/200 pares, balanceada), zero-shot. Melhor em VD: Claude-Sonnet-4 (69,5 single / 73,7 paired). Muitos modelos despencam no pareado (Qwen2.5-Coder-32B 51,7→20,8), reforçando a dificuldade da avaliação pareada. É um bom benchmark de "confiabilidade" multi-tarefa para referência.

### 9. SecVulEval (Ahmed, S. et al., 2025) — arquivo `Datasets.../Ahmed, S - 2025.md`

| Afirmação no dossiê (linha 133) | Fonte | Status |
|---|---|---|
| Em nível de instrução, o melhor modelo atinge ~24% de F1 | Abstract: "best-performing Claude-3.7-Sonnet achieves 23.83% F1-score for detecting vulnerable statements with correct reasoning" | ✅ CONFIRMADO |

Dados: 25.440 funções, 5.867 CVEs, C/C++ 1999–2024, anotação em nível de instrução (statement-level), avaliação multi-agente. GPT-4.1 logo atrás.

### 10. Yin, X.; Ni; Wang (2024) — arquivo `Deteccao.../Yin, X - 2024.md`

| Afirmação no dossiê (linhas 119, 133) | Fonte | Status |
|---|---|---|
| Métodos SOTA e modelos pré-treinados geralmente superam LLMs na detecção | Abstract: "existing SOTA approaches and pre-trained LMs are generally superior to LLMs in software vulnerability detection" | ✅ CONFIRMADO |
| "em especial o UniXcoder ... superando LLMs bem maiores" | O abstract do Yin não singulariza UniXcoder (usa Big-Vul, 4 tarefas). A força específica do UniXcoder é melhor sustentada por PrimeVul e Ouchebara | 🟡 ATRIBUIÇÃO FROUXA: manter Yin para "pré-treinados > LLMs"; para "UniXcoder forte", citar PrimeVul/Ouchebara junto. |

Nuance: Yin usa **Big-Vul** (dataset contaminado). Logo, a conclusão "pré-treinados > LLMs" vem de benchmark antigo — usar com a ressalva de contaminação que o próprio dossiê defende.

---

## PARTE II — Tabela de rastreabilidade (arquivo ↔ referência do dossiê)

Todos os 41 arquivos foram mapeados a uma entrada da seção 12 do dossiê. **Cinco arquivos correspondem a referências que o dossiê lista SEM autoria** (só título) — adicionar os autores:

| Arquivo | Título real | Ref. dossiê | Ajuste necessário |
|---|---|---|---|
| Syafiq Al - 2024 | From Generalist to Specialist: Exploring CWE-Specific Vulnerability Detection | 12.1 (arXiv:2408.02329) | Adicionar autoria: **Al Atiiq, S.; Gehrmann, C.; Dahlén, K.; Khalil, K.** (Lund Univ.) |
| Feiyang Huang - 2026 | Do Fine-Tuned LLMs Understand Vulnerabilities? (Semantic Trap) | 12.1 (arXiv:2601.22655) | Adicionar autoria: **Huang, F. et al.** |
| Sabrina Kaniewski - 2026 | Revisiting Vul-RAG | 12.1 (arXiv:2606.04739) | Adicionar autoria: **Kaniewski, S.; Schmidt, F.; Heer, T.** |
| Shuzheng Gao - 2025 | TREAT | 12.1 (arXiv:2510.17163) | Adicionar autoria: **Gao, S. et al.** (CUHK) |
| Chenxu Niu - 2025 | TokenPowerBench | 12.5 (arXiv:2512.03024) | Adicionar autoria: **Niu, C. et al.** (Texas Tech) |

---

## PARTE III — Papers de eficiência (quantização, PEFT, destilação)

### 11. Wu, X. et al. (INT4, ICML 2023) — arquivo `Eficiência.../Wu, X - 2023.md` — **peça-chave da tese**

| Afirmação no dossiê (linha 157) | Fonte | Status |
|---|---|---|
| Degradação desprezível em codificadores sob 4 bits, ao contrário de decodificadores de geração | Abstract: "W4A4 introduces no to negligible accuracy degradation for encoder-only and encoder-decoder models, but causes a significant accuracy drop for decoder-only models" | ✅ CONFIRMADO (exato) |

**⚠️ NUANCES CRÍTICAS que o dossiê PRECISA incorporar (fortalecem e ao mesmo tempo delimitam o argumento central):**
1. O resultado "robusto" de Wu é para **arquitetura encoder** (BERT em classificação). O Recorte A usa **decoders de código** (Qwen2.5-Coder, StarCoder2, DeepSeek-Coder) **com cabeça de classificação**. Ou seja: arquitetura decoder operando em modo classificação. Wu NÃO testa esse caso híbrido — o "salto" de "classificação tolera 4 bits" para "decoder-de-código com cabeça de classificação tolera 4 bits" é uma **hipótese**, não um resultado herdado. Isso é, na verdade, **parte da lacuna do próprio projeto** e deve ser dito explicitamente (o dossiê já reconhece "não isolado para código", mas falta reconhecer o eixo arquitetura decoder×tarefa classificação).
2. Wu testa **W4A4** (peso E ativação em 4 bits). O caminho principal do Recorte A (QLoRA/NF4, e AWQ/GPTQ) é majoritariamente **weight-only (W4A16)** — regime bem mais brando. Isso é BOM para o projeto (a "falha" dos decoders em Wu é do regime agressivo W4A4, não do 4-bit weight-only), mas significa que Wu não pode ser citado como prova de que "4 bits é seguro" no regime do projeto — os regimes diferem. Recomenda-se separar claramente na dissertação: quantização *weight-only* (NF4/AWQ/GPTQ) vs *weight+activation* (W4A4/W8A8).

### 12. QLoRA (Dettmers, T. et al., NeurIPS 2023) — `Eficiência.../Dettmers, T - 2023.md`
✅ CONFIRMADO exato (linha 159): "finetune a 65B parameter model on a single 48GB GPU while preserving full 16-bit finetuning task performance". NF4, Double Quantization, Paged Optimizers confirmados. **Nuance:** o resultado "sem perda" é em *instruction following/chatbot* (Guanaco/Vicuna), não em classificação de vulnerabilidade — a transferência para a tarefa do projeto é, de novo, hipótese a testar (é justamente a RQ do projeto).

### 13. GPTQ (Frantar, E. et al., ICLR 2023) — `Eficiência.../Frantar, E - 2023.md`
✅ CONFIRMADO (linha 157): quantização one-shot com informação de segunda ordem, 3–4 bits com degradação negligível; speedup ~3,25× (A100). Descrição do dossiê fiel.

### 14. AWQ (Lin, J. et al., MLSys 2024) — `Eficiência.../Lin, J - 2026.md`
✅ CONFIRMADO (linha 157): protege ~0,1–1% de pesos salientes via distribuição de ativações; weight-only; generaliza sem overfit ao conjunto de calibração (ponto forte vs GPTQ). **🔴 Erro de NOME DE ARQUIVO:** o arquivo diz "Lin, J - 2026", mas o paper é **MLSys 2024 (Best Paper Award)** — a referência 12.3 do dossiê está CERTA (2024); corrigir o nome do arquivo/registro para 2024 para evitar confusão.

### 15. SmoothQuant (Xiao, G. et al., ICML 2023) — `Eficiência.../Xiao, G - 2024.md`
✅ CONFIRMADO (linha 157): W8A8, migra a dificuldade de quantização das ativações para os pesos. Descrição "trata pesos e ativações em conjunto" fiel. **Nota:** arquivo diz "2024" mas é **ICML 2023** (a ref. 12.3 do dossiê já diz 2023, correto). **Relevância limitada ao projeto:** SmoothQuant é sobretudo W8A8 para geração; menos central que NF4/AWQ/GPTQ para o desenho weight-only do Recorte A.

### 16. LoRA (Hu, E. et al., ICLR 2022) — `Eficiência.../Hu, E - 2021.md`
✅ CONFIRMADO (linha 159): matrizes de baixo posto, pesos congelados, −10.000× parâmetros treináveis, −3× memória. Coerente.

### 17. Wei, X. et al. (Greener yet Powerful, ESEC/FSE 2023) — `Eficiência.../Wei, X - 2023.md`
| Afirmação no dossiê (linha 157) | Fonte | Status |
|---|---|---|
| "Para geração de código, a literatura mostra maior sensibilidade (Wei et al., 2023)" | Wei encontra uma *receita* de quantização que roda um modelo de 6B num laptop **sem degradação significativa** de acurácia/robustez (foco em INT8) | 🟡 IMPRECISO: Wei é, na verdade, **otimista** — mostra que geração de código PODE ser quantizada com receita cuidadosa. Sustenta "geração exige mais cuidado que classificação", mas não "geração é muito sensível". Reescrever para "geração de código requer receita cuidadosa de quantização (Wei et al., 2023)", e lembrar que Wei foca em INT8, não 4 bits. |

### 18. Avatar (Shi, J. et al., ICSE-SEIS **2024**) — `Eficiência.../Shi, J - 2024.md`
| Afirmação no dossiê (linha 164) | Fonte | Status |
|---|---|---|
| Avatar comprime codificadores de código em ordens de grandeza, mantendo desempenho em predição de vulnerabilidade, perda pequena | Abstract: modelos de 3 MB (160× menores), energia até 184× menor, latência até 76× menor, perda de só 1,67%, em CodeBERT/GraphCodeBERT para *vulnerability prediction* e clone detection | ✅ CONFIRMADO |
| "trade-off entre compressão e robustez adversarial" | Não aparece no abstract/intro | ⚠️ VERIFICAR no corpo do paper — pode ser conflação; se não estiver em Avatar, remover ou reatribuir |
| Status "[preprint]" na ref. 12.3 e ano "2023" | É **revisado por pares (ICSE-SEIS 2024)** | 🔴 A CORRIGIR: mudar de "[preprint] 2023" para "[revisado por pares], ICSE-SEIS 2024". |

### 19. PSO-KDVA (Gao, X./Chaoyang Gao et al., 2025) — `Eficiência.../Gao, X - 2025.md`
✅ Existe e é destilação (KD) + PSO para modelo compacto. **Distinção importante:** trata de **avaliação/assessment de vulnerabilidade (score CVSS)**, NÃO de detecção. Retém 89,3% do desempenho com 0,6% do tamanho, sobre MegaVul (12.071 CVSS v3). Útil como referência de destilação, mas o dossiê deve deixar claro que é *assessment*, tarefa distinta da detecção do Recorte A.

---

## PARTE IV — Datasets, modelos, infraestrutura e demais papers de detecção

**Datasets (seção 7.3 e 12.2) — todos confirmados:**
- **Big-Vul** (Fan 2020): 3.754 CVEs, 91 CWEs, 348 projetos, C/C++ ✅.
- **DiverseVul** (Chen 2023): consolida Devign/BigVul/ReVeal/CrossVul/CVEfixes; ~60% acurácia de rótulo (via Tab. I do PrimeVul) ✅.
- **MegaVul** (Ni 2024): 17.380 vulns, 992 repos, 169 CWEs, 2006–2023, C/C++, 4 representações ✅.
- **ReposVul** (Wang 2024): nível de repositório ✅.
- **CleanVul** (Li, Y. 2025): limpeza por heurística de LLM (VULSIFTER, F1 0,82); ruído de 40–75% nos datasets existentes ✅. (dossiê diz "preprint 2024"; arXiv nov/2024, publicação 2025 — ok).
- **CodeXGLUE** (Lu 2021): benchmark de compreensão/geração; defect detection usa Devign ✅.

**Infraestrutura (seção 10-11 e 12.5) — confirmados:**
- **vLLM/PagedAttention** (Kwon 2023): throughput 2–4× vs FasterTransformer/Orca ✅.
- **TokenPowerBench** (Niu 2025): 1º benchmark de **consumo de energia da inferência**; joules/token, separa prefill/decode, varia batch/contexto/paralelismo/**quantização**. ✅ Excelente base para a metodologia de eficiência da seção 10 (energia). Ausente de autoria no dossiê (Niu, C. et al.).

**Modelos de código (12.4):**
- **Qwen2.5-Coder** (Hui 2024) ✅; **StarCoder2** (Lozhkov 2024) ✅; **Granite Code** (Mishra 2024) ✅.
- **DeepSeek-Coder-V2** (Zhu, Guo, Shao et al., 2024) — arquivo `Modelos de código/DeepSeek-Coder-V2 - 2024.md` **[CORRIGIDO pelo autor em 06/set — agora contém o paper certo, 505 linhas, verificado ✅]**. Fatos: MoE de **16B (2,4B ativos)** e **236B (21B ativos)**; 338 linguagens (de 86); contexto 128K; comparável ao GPT-4-Turbo em código (HumanEval 90,2%, MBPP+ 76,2%, LiveCodeBench 43,4%; 1º open-source >10% no SWE-Bench). **⚠️ Nuance prática para o Estágio 2:** DeepSeek-Coder-V2 é **MoE** — o **total** de parâmetros (16B no Lite) é que define a memória de carga, não os 2,4B ativos. Um Lite de 16B **não cabe** em 24 GB em 16 bits (≈32 GB); exigiria quantização já na Etapa 1, ou usar o **DeepSeek-Coder (V1) 6.7B denso** para paridade justa com Qwen2.5-Coder-7B e StarCoder2-7B. Decidir isso explicitamente no desenho.
- *(Histórico: o arquivo antigo `DeepSeek-AI - 2024.md` continha por engano o paper Granite; foi corrigido/substituído pelo autor.)*

**Demais papers de detecção:**
- **Shestov (IEEE Access 2025)** — linha 161: LoRA em **WizardCoder 13B** (decoder) → 25M params treináveis (< CodeBERT 125M); supera baseline encoder **ContraBERT** (F1 0,71 vs 0,68; ROC AUC 0,69 vs 0,66). ✅ CONFIRMADO, com nuances: (a) é **Java**, não C/C++; (b) margem **pequena** sobre o encoder; (c) baseline é ContraBERT (CodeBERT aprimorado), não vanilla; (d) LoRA (não QLoRA). Bom precedente metodológico para o Estágio 2.
- **JITVUL (Yildiz 2025)** — linha 153: benchmark pareado JIT ligando função ao commit que introduz/corrige; **879 CVEs, 91 CWEs**; agentes ReAct > LLMs. ✅ existe e é pareado JIT. **⚠️ "construído sobre o PrimeVul": NÃO confirmado no abstract** (cita Devign/BigVul/ReposVul/VulEval, não PrimeVul). Verificar/remover essa atribuição.
- **From Generalist to Specialist (Al Atiiq et al., 2024)** — classificadores por CWE superam um único classificador binário; reporta DiverseVul/CodeBERT F1 só 11,94% em projetos não vistos. ✅ Relevante à tese de "especialização", mas o dossiê apenas lista sem citar no corpo — **oportunidade de integração** (sustenta tanto "especializar ajuda" quanto "generalização é fraca").
- **VulBench (Gao, Z. 2023)**, **Zhou, X. ICSE-NIER 2024**, **Sheng survey (ACM CSUR 2025)**, **Devign (Zhou, Y. 2019)**, **CodeBERT (Feng 2020)**, **GraphCodeBERT (Guo 2021)**, **UniXcoder (Guo 2022)**: títulos e papéis conferem com as referências; afirmações descritivas de baixo risco ✅.

---

## PARTE V — Análise da lacuna de pesquisa: ela é real? (à luz dos 41 papers)

**Veredito: a lacuna central é GENUÍNA e permanece aberta.** Nenhum dos 41 papers isola o efeito do *método* de quantização (AWQ, GPTQ, NF4, GGUF) sobre a **qualidade de classificação** de vulnerabilidade (não geração) sob **avaliação descontaminada** (PrimeVul + pareado + VD-S). Mapa do que existe e do que falta:

| Peça da lacuna | Quem chega perto | O que ainda falta (espaço do Recorte A) |
|---|---|---|
| Quantização isolada em classificação | Wu 2023 (encoders, NLP geral, W4A4) | Fazer em **decoders de código**, tarefa de **vulnerabilidade**, regime **weight-only** |
| QLoRA + cabeça de classificação em PrimeVul | Ouchebara 2025 (Llama-3.1 8B, NF4) | Ouchebara **não compara** AWQ/GPTQ/GGUF; usa dados **balanceados**, split único, sem VD-S/pareado |
| Comparação de métodos de quantização | GPTQ, AWQ, SmoothQuant (papers de método) | Nenhum avalia sob **VD-S/acurácia pareada** em vulnerabilidade |
| Destilação em código | Avatar 2024, PSO-KDVA 2025 | Não cobrem quantização×QLoRA; PSO-KDVA é *assessment* |
| Benchmark de eficiência (energia, tok/s, custo) | TokenPowerBench 2025 | **Usar** (não reinventar) e conectar à qualidade descontaminada |

**Três ressalvas honestas sobre a novidade (para calibrar as contribuições):**

1. **A demonstração de contaminação (Etapa 4) NÃO é a novidade** — já é bem estabelecida (PrimeVul 68→3%; Kaniewski confirma o platô; Feiyang Huang e TREAT mostram colapso no pareado). No Recorte A ela é **confirmatória/pedagógica**. A novidade real está no eixo **quantização × classificação × descontaminação**, e é aí que a redação deve concentrar a originalidade. Evitar vender "provar contaminação" como contribuição principal.

2. **A formulação "classificação > geração" já foi mostrada por Ouchebara.** Portanto a 1ª RQ ("modelo pequeno especializado por QLoRA recupera o desempenho do maior?") tem resposta parcial na literatura: **empata os encoders no PrimeVul, não os supera.** O Recorte A precisa ir além de Ouchebara em pelo menos três frentes para ser novo: (a) **comparar métodos de quantização** (ninguém fez para VD-classificação), (b) reportar **VD-S + acurácia pareada + FPR** (Ouchebara só reporta F1/acurácia/AUC), (c) **múltiplos seeds com intervalos de confiança** (Ouchebara é split único — o próprio dossiê critica isso; não repetir o erro).

3. **A literatura de 2026 aponta fortemente para o "ramo de reenquadramento" (linha 194).** Kaniewski (platô ~0,30, escala não ajuda), Feiyang Huang (Semantic Trap: SFT não ensina causa-raiz) e TREAT (colapso no pareado) convergem: **sob avaliação pareada descontaminada, quase tudo fica perto do acaso, e QLoRA provavelmente não fecha a lacuna.** Isso não enfraquece o projeto — ao contrário, o desenho já prevê o pivô (reenquadrar como estudo eficiência×qualidade, linha 194). **Recomendação:** assumir esse enquadramento como cenário-base desde a qualificação, não como plano B. A pergunta que quase certamente rende resultado robusto e publicável é: *"dado que o modelo grande também é ruim no pareado, quão mais barato (memória/energia/latência/custo) fica o modelo pequeno quantizado para a MESMA qualidade limitada?"* — contribuição de caracterização de baixo risco e alto valor prático.

**Lacunas 5, 6, 7 (robustez, robustez adversarial×compressão, multilíngue):** a 5 (robustez de quantizados a perturbações que preservam semântica) é bem sustentada e diferenciável (Feiyang Huang/SecLLMHolmes dão o protocolo de perturbação; ninguém cruzou com **quantização**). A 6 (compressão×robustez adversarial) é mencionada mas **sem fonte forte no corpus** (o trade-off atribuído ao Avatar precisa ser verificado). A 7 (multilíngue) é aspiracional — o corpus é majoritariamente C/C++ (+ Java em IRIS/Shestov); manter como trabalho futuro.

---

## PARTE VI — Análise crítica da metodologia proposta

**Pontos fortes (bem embasados na literatura):**
- Adotar **PrimeVul + pareado + VD-S** como padrão — é o estado da arte de rigor (Ding 2024) e evita a armadilha do F1 no Big-Vul.
- **Cabeça de classificação** em vez de geração — corretamente justificada por Ouchebara (classificação > geração) e por Wu (compreensão tolera melhor baixa precisão).
- **Métricas de custo** (VRAM pico, TTFT/TPOT, tok/s, energia via nvidia-smi/pynvml, custo/hora) — alinhadas a TokenPowerBench; o proxy custo/hora do RunPod é reprodutível e honesto.
- Baseline **UniXcoder totalmente ajustado** — é o baseline forte recorrente (PrimeVul, Ouchebara, Yin).

**Riscos e ajustes recomendados (ordenados por importância):**

1. **VD-S exige probabilidade calibrada → só vale para o caminho com cabeça de classificação, NÃO para o baseline de prompting da Etapa 1.** VD-S = FNR sob FPR≤0,5% depende de varrer um limiar sobre um score contínuo. O prompt zero-shot (Etapa 1) devolve "sim/não" (sem probabilidade), então não produz VD-S de forma legítima. **Corrigir a expectativa:** na Etapa 1, reportar F1/precisão/revocação/FPR do baseline prompt; VD-S e curva ROC entram a partir da Etapa 3 (cabeça de classificação com logit). Isso afeta a tabela de "métricas obrigatórias" da linha 185.

2. **GGUF confunde o eixo de custo.** GGUF/llama.cpp é orientado a CPU/edge; AWQ/GPTQ/NF4 rodam em GPU (vLLM/HF). Comparar latência/energia de GGUF (llama.cpp) com AWQ/GPTQ (vLLM) é **cross-engine** e confunde "efeito do método de quantização" com "efeito do motor de inferência". **Recomendação:** fixar um único motor por eixo e reportar separadamente, ou tratar GGUF como estudo de implantação à parte (edge/CPU), fora da mesma curva de trade-off.

3. **Separar explicitamente dois regimes de quantização:** *weight-only* (NF4/AWQ/GPTQ — caminho principal, mais brando) vs *weight+activation* (W4A4/W8A8 — Wu/SmoothQuant). Misturá-los ao citar Wu como justificativa gera imprecisão (Parte III, item 11). A dissertação fica mais forte deixando claro que o núcleo é **W4A16 weight-only**, e que a "falha dos decoders" de Wu é do regime agressivo W4A4.

4. **Intervalos de confiança e múltiplos seeds são obrigatórios** — é o principal diferencial em relação aos preprints citados (Ouchebara etc., todos com split único). O PrimeVul-test tem só ~695 vulneráveis; VD-S calibrado a FPR≤0,5% é sensível a essa amostra pequena. Rodar ≥3 seeds, reportar média ± desvio/IC. Responde diretamente à ressalva 13.1 do próprio dossiê.

5. **Calibração da quantização em decoder+cabeça de classificação é território pouco explorado** (parte da lacuna). AWQ/GPTQ calibram em dados de *geração*; ao usá-los com cabeça de classificação, documentar o conjunto de calibração e se a quantização é aplicada antes/depois do QLoRA. Ordem a testar: (a) quantizar base → QLoRA (NF4) → avaliar; (b) QLoRA em 16b → PTQ (AWQ/GPTQ) do modelo mesclado → avaliar. Perguntas distintas, ambas interessantes.

6. **Precisão do enquadramento "pequeno vs grande".** Definir os eixos numericamente para não repetir a confusão de Ouchebara (LLM 8B "pequeno" empatando encoder de 125M). No Recorte A o contraste economicamente interessante é: **Qwen2.5-Coder-7B (4-bit, QLoRA) vs 7B (16-bit) vs UniXcoder-125M (full-FT)** — em qualidade descontaminada E em custo. Deixar os três eixos explícitos.

7. **Fonte do DeepSeek-Coder ausente no corpus** (Parte IV): reconverter o PDF correto antes de citar especificações do modelo.

---

## PARTE VII — Correções bibliográficas consolidadas e recomendações finais

### 7.1 Correções bibliográficas a aplicar no dossiê

| # | Item | Correção |
|---|---|---|
| 1 | Vul-RAG (linha 129) | "16 a 24% **relativos**" → "16 a 24 **pontos percentuais absolutos** de acurácia pareada" |
| 2 | Avatar (12.3) | "[preprint], 2023" → "**[revisado por pares], ICSE-SEIS 2024**" |
| 3 | Semantic Trap (linha 134) | Remover exemplos não-fontados "gestão de memória, protocolos de rede"; descrever como "padrões funcionais/superficiais (V2P vs V2N; gap CodeBLEU)" |
| 4 | JITVUL (linha 153) | Verificar/remover "construído sobre o PrimeVul" (não confirmado; é JIT sobre 879 CVEs) |
| 5 | QLoRA-classificação (linha 162) | "F1 despenca em desbalanceado" não é testado por Ouchebara (balanceado) — remover ou fundamentar com outra fonte/experimento |
| 6 | Yin (linha 119) | "em especial o UniXcoder... superando LLMs" — atribuir "UniXcoder forte" a PrimeVul/Ouchebara; manter Yin para "pré-treinados > LLMs" |
| 7 | 5 referências sem autoria | Adicionar: Al Atiiq et al.; Huang et al.; Kaniewski, Schmidt & Heer; Gao, S. et al. (TREAT); Niu, C. et al. (TokenPowerBench) |
| 8 | Corpus DeepSeek | `DeepSeek-AI - 2024.md` contém o Granite — reconverter o DeepSeek-Coder-V2 (arXiv:2406.11931) |
| 9 | Nomes de arquivo | AWQ (Lin) = **2024** (não 2026); SmoothQuant (Xiao) = **2023** (não 2024) — as refs do dossiê já estão certas; corrigir só os nomes de arquivo |
| 10 | arXiv a conferir | Confirmar IDs 2025/2026 coletados automaticamente: 2512.09006 (Ouchebara), 2601.22655 (Semantic Trap), 2606.04739 (Kaniewski), 2510.17163 (TREAT), 2512.03024 (Niu), 2503.03586 (JITVUL) |

### 7.2 Veredito global sobre o dossiê

**O dossiê é uma síntese de alta qualidade e, em sua esmagadora maioria, fiel às fontes.** Todas as afirmações numéricas *centrais* — PrimeVul (68,26%→3,09%), IRIS (55/27/52, −5 pts FDR, 4 inéditas), SecLLMHolmes (26%/17%), Vul-RAG (magnitudes), Kaniewski (platô 0,30; 4B≈30B), SecVulEval (~24%), Wu (encoder×decoder), QLoRA (65B/48GB), Shestov (WizardCoder), TREAT (alta precisão/baixa revocação) — **conferem com as fontes primárias**. Os problemas são de **detalhe** (um erro real: "relativos"↔"absolutos" no Vul-RAG; um erro de status: Avatar preprint↔peer-reviewed; um erro de corpus: DeepSeek↔Granite) e de **atribuição/embelezamento** (Semantic Trap, JITVUL, "despenca em desbalanceado"), não de substância. A tese e a lacuna se sustentam.

### 7.3 Recomendações estratégicas para a dissertação

1. **Posicionar a contribuição no eixo "método de quantização × classificação de vulnerabilidade × avaliação descontaminada"** — é o que ninguém fez. Não vender a demonstração de contaminação como novidade.
2. **Assumir o cenário de reenquadramento (eficiência×qualidade) desde a qualificação.** A convergência dos preprints de 2026 torna provável que QLoRA não feche a lacuna de qualidade; a caracterização de custo para qualidade limitada é a contribuição robusta e de baixo risco.
3. **Ir além de Ouchebara em três frentes obrigatórias:** comparar métodos de quantização; reportar VD-S + pareado + FPR; usar múltiplos seeds com IC.
4. **Tratar VD-S como métrica dos estágios com cabeça de classificação**, não do baseline de prompting.
5. **Separar os regimes weight-only vs weight+activation** e isolar o motor de inferência ao medir custo (GGUF à parte).
6. **Integrar duas fontes hoje subutilizadas:** "From Generalist to Specialist" (Al Atiiq) para a tese de especialização, e TokenPowerBench (Niu) como espinha dorsal da medição de energia.
7. **Reconverter o PDF do DeepSeek-Coder-V2** antes de fixar os modelos do Estágio 2.
8. **Robustez (lacuna 5) é o diferencial mais limpo e barato:** cruzar as perturbações que preservam semântica (protocolo de SecLLMHolmes/Feiyang Huang) com os modelos **quantizados** — ninguém fez, e responde à pergunta "quantização degrada a robustez?".

---

## Apêndice — Cobertura da verificação

41/41 arquivos markdown lidos e mapeados a referências do dossiê. Papers com afirmações numéricas centrais foram lidos integralmente ou até a seção de resultados; papers descritivos (relatórios de modelo, datasets, surveys) foram verificados por abstract/introdução e tabela. Conversão dos PDFs feita por `page/ollama:qwen2.5vl:7b` (registrada no cabeçalho de cada arquivo) — pequenos ruídos de OCR em tabelas são possíveis; os números centrais foram conferidos contra o texto corrido, não só contra tabelas.
