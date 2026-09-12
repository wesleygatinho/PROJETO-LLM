# RECORTE A — Protocolo experimental (decisões travadas)

Documento operacional derivado do dossiê v3. Consolida as 9 pendências em decisões executáveis.
Decisões estratégicas definidas em conversa (set/2026): **enquadramento = custo×qualidade**; **compute = médio**; **orientador já alinhado** (validar os pontos da §12 com ele(a)).

---

## 0. Enquadramento e critério de sucesso

**Contribuição principal:** caracterização empírica do **trade-off custo × qualidade** da detecção de vulnerabilidade por LLMs de código, sob avaliação **descontaminada** (PrimeVul + pareado + VD-S), isolando o efeito do **método de quantização** e do **QLoRA com cabeça de classificação**.

**Critério de sucesso (importante):** o sucesso **NÃO depende** de o modelo pequeno superar o grande em qualidade. Sucesso =
1. uma **curva de trade-off** qualidade×custo rigorosa (com o "joelho" identificado) e uma **recomendação prática** de implantação;
2. a **comparação inédita** entre métodos de quantização (AWQ/GPTQ/NF4) sob VD-S/pareado;
3. (bônus) evidência sobre **robustez** dos modelos quantizados.
Se o QLoRA não melhorar a qualidade (cenário provável pela literatura de 2026), isso vira **resultado publicável**, não fracasso.

**Perguntas de pesquisa (reformuladas):**
- RQ1: Sob avaliação descontaminada, quanto de **custo** (memória/energia/latência/US$) se economiza ao especializar um modelo pequeno por QLoRA e quantizá-lo, para uma **dada** qualidade?
- RQ2: **Qual método de quantização** (AWQ, GPTQ, NF4) melhor preserva a qualidade de classificação (VD-S e acurácia pareada)?
- RQ3 (secundária): A quantização **degrada a robustez** a perturbações que preservam a semântica?

---

## 1. As 9 pendências — decisões travadas

| # | Pendência | Decisão travada |
|---|---|---|
| 1 | Enquadramento | **Custo×qualidade** (base). Recuperação de desempenho vira RQ secundária, não a aposta. |
| 2 | Pipeline de inferência | QLoRA(NF4) treina o adapter → **mesclar (merge) → PTQ (AWQ/GPTQ/INT8) do modelo final** para medir custo real. **QA-LoRA** como variante comparativa. Nunca reportar custo do QLoRA "cru". |
| 3 | Estatística | **3 seeds** por configuração de treino; média ± **IC95%**; **McNemar** para acurácia pareada. |
| 4 | Motor de inferência | **vLLM** para FP16/INT8/AWQ/GPTQ/NF4 (GPU). **GGUF/llama.cpp reportado à parte** (estudo edge/CPU), fora da curva principal. |
| 5 | Robustez | Subconjunto das **11 transformações de Risse & Böhme** + renomeação/biblioteca de **SecLLMHolmes**, aplicadas **aos modelos quantizados**. |
| 6 | Roster | **Qwen2.5-Coder-7B, StarCoder2-7B, DeepSeek-Coder-6.7B (denso)** + **UniXcoder-125M (full-FT)**. DeepSeek-Coder-V2 (MoE) fora por memória. |
| 7 | Não-objetivos | Fora: multi-linguagem (só C/C++), nível de repositório/inter-procedural, geração de código, localização statement-level, inventar algoritmo novo. |
| 8 | Orientador | Já alinhado → validar §12 (enquadramento, escopo, encaixe na linha) antes da qualificação. |
| 9 | Orçamento | **Médio** (~US$300–800). Estimativa detalhada na §9. |

---

## 2. Roster de modelos e datasets

**Modelos de código (decoders, versão Instruct para prompting; Base para cabeça de classificação):**
- Qwen2.5-Coder-7B · StarCoder2-7B · DeepSeek-Coder-6.7B.
**Baseline forte:** UniXcoder-125M, *fully fine-tuned* (é o baseline recorrente e difícil de bater no PrimeVul).

**Datasets:**
- **Primário:** PrimeVul (all + **paired**), split temporal oficial.
- **Contraste de contaminação:** Big-Vul (ou Devign/CodeXGLUE) — só para a Etapa 4 (demonstrar a queda).
- (Opcional/controle temporal: um benchmark pós-corte, ex. amostra do MegaVul/SecVulEval recente.)

---

## 3. Métricas

**Qualidade (sempre em conjunto):** F1 da classe vulnerável · **FPR** · **VD-S** (FNR@FPR≤0,5%) · **acurácia pareada** (P-C/P-V/P-B/P-R). *VD-S e ROC só nas etapas com cabeça de classificação (score contínuo); o baseline de prompting reporta F1/precisão/revocação/FPR.*
**Custo:** VRAM de carga + pico · TTFT · TPOT · tokens/s · **J/token e W médio** (pynvml/nvidia-smi) · **US$ = preço/h da instância × tempo** (registrar GPU e tier exatos).

---

## 4. Matriz de experimentos (nível médio)

Para **cada** um dos 3 decoders:
1. **QLoRA (NF4) + cabeça de classificação** treinado no PrimeVul-train → **modelo especializado** (×3 seeds).
2. Do modelo especializado, gerar variantes de inferência: **{FP16, INT8, NF4-4bit, AWQ-4bit, GPTQ-4bit}**.
3. Avaliar cada variante em PrimeVul-test (all + paired): **qualidade + custo**.

→ 3 decoders × 5 precisões × 3 seeds = **45 avaliações** + 9 treinos QLoRA.
**Baselines:** UniXcoder-125M full-FT {FP16, INT8, 4bit} (×3 seeds) · prompting 16-bit dos 3 decoders (Etapa 1).
**Contaminação (Etapa 4):** 1 modelo em Big-Vul vs PrimeVul.
**Robustez (RQ3):** aplicar perturbações a um subconjunto do teste e reavaliar as variantes FP16 e 4-bit de cada decoder.
**GGUF:** à parte, 1–2 modelos, medindo custo em CPU/edge (não entra na curva GPU).

---

## 5. Ordem QLoRA × quantização (pipeline do Estágio 3)

Testar as duas ordens e comparar (é parte da lacuna):
- **(a) NF4→QLoRA→merge→PTQ(AWQ/GPTQ):** treina sobre base 4-bit, mescla, re-quantiza para inferência.
- **(b) QLoRA em 16-bit→merge→PTQ:** treina em precisão cheia, depois quantiza.
- **(c) QA-LoRA:** adapter já na precisão do modelo quantizado (inferência sem desquantizar).
Documentar o **conjunto de calibração** do AWQ/GPTQ (usar amostra do PrimeVul-train, não só texto genérico).

---

## 6. Protocolo estatístico

- Temperatura 0 (determinístico) no prompting; logits na cabeça de classificação.
- 3 seeds de treino QLoRA; reportar média ± IC95% (bootstrap).
- Acurácia pareada: **McNemar** entre configurações (ex.: 4-bit vs 16-bit).
- VD-S: calibrar o limiar no **dev** (não no teste) para FPR≤0,5%; reportar IC (amostra de vulneráveis é pequena, ~695).

---

## 7. Protocolo de robustez (RQ3)

- Perturbações que preservam a semântica: renomeação de variável/função, inserção de código morto, comentários, reordenação de statements não relacionados (subconjunto de Risse); + adição de função de biblioteca perigosa usada de forma segura (SecLLMHolmes).
- Métrica: **queda de acurácia/F1** e **taxa de troca de predição** entre original e perturbado, **por nível de bits**. Hipótese: a quantização amplia (ou não) a fragilidade.

---

## 8. Não-objetivos (escopo explícito)

Fora do Recorte A: multi-linguagem (só C/C++); detecção a nível de repositório/inter-procedural; formulação por geração; localização statement-level; proposta de arquitetura/algoritmo novo; modelos proprietários como contribuição (só como referência opcional).

---

## 9. Estimativa de compute/custo (RunPod, nível médio)

Estimativa grosseira (buffer de depuração incluído; varia com tier Community/Secure e GPU):

| Bloco | Runs | ~GPU-h | ~US$ (A100 80GB @1,39) |
|---|---|---|---|
| Treinos QLoRA (3 modelos × 3 seeds) | 9 | ~30 | ~40 |
| Calibração AWQ/GPTQ | ~6 | ~5 | ~7 |
| Avaliações (45 configs, paired + amostra do full) | 45 | ~45 | ~65 |
| Baselines (UniXcoder full-FT + prompting) | ~15 | ~20 | ~28 |
| Robustez (subconjunto) | — | ~15 | ~21 |
| **Subtotal** | | ~115 | **~160** |
| **+ buffer 2–3× (depuração, falhas, repetições de medição de energia)** | | | **~320–560** |

→ dentro do envelope **médio (US$300–800)**. Começar pelo modelo 3B/menor e por ~50 funções para depurar o *parsing* antes de gastar. Preferir RTX 4090 24GB (mais barata) para os 7B e A100 só quando necessário.

---

## 10. Reprodutibilidade

- Fixar e registrar: modelo exato, precisão, método de quantização, prompt, seed, GPU/tier, versão das libs.
- Usar o **script oficial de avaliação pareada do PrimeVul**; publicar código + splits + configs.
- Guardar os *checkpoints* dos adapters QLoRA e os modelos quantizados (ou receitas).

---

## 11. Critérios de decisão (limiares que mudam a recomendação)

- 4-bit degrada a acurácia pareada **> 3 pts** vs 16-bit → recomendar **8-bit** como padrão de implantação.
- QLoRA-7B fica **> 5 pts de VD-S** abaixo do UniXcoder-FT → registrar como resultado de caracterização (e citar neuro-simbólico/RAG como direção futura — **não** é pivô, dado o enquadramento custo×qualidade).
- Acurácia pareada perto do acaso mesmo após QLoRA → **cenário esperado**; a contribuição vira a curva de custo para qualidade limitada (já é o plano).

---

## 12. Pontos para validar com o orientador (já que está alinhado)

1. Confirmar o **enquadramento custo×qualidade** como contribuição principal (título/qualificação).
2. Confirmar os **não-objetivos** (§8) — sobretudo ficar só em C/C++ e função.
3. Confirmar o encaixe do **ângulo de eficiência/benchmark** (TokenPowerBench, energia) na linha de Modelagem Computacional.
4. Aprovar o **orçamento** e o acesso a GPU (RunPod) para o nível médio.
5. Definir o **veículo de publicação** alvo (workshop/conferência) para calibrar a profundidade.
