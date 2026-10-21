# Análise crítica do próximo passo (08/10/2026)

## Documentos examinados e limites

Examinei apenas o conteúdo dos seis documentos colados na solicitação:
- `PLANO_EXECUCAO.md`
- `CRONOGRAMA_CHECKLIST.md`
- `PLANO_ESCRITA.md`
- `revisao/introducao_2026-10-07/FECHAMENTO.md`
- `consolidacao_artigo/README.md`
- `MATRIZ_INTRODUCAO.md`

Não abri nenhum arquivo do repositório. Não executei comandos nem conferi o estado real do disco. A informação de que `03_experimentos/dados/` contém só `.gitkeep` vem do Codex e dos próprios planos; não a confirmei por conta própria. Também não li o texto da introdução, o código, os logs, os CSVs nem os PDFs. O que segue confere coerência entre planos, não faz verificação científica. Minha concordância com o Codex em alguns pontos não prova nada sobre os resultados.

---

## 1. Veredito sobre a resposta anterior: **parcial**

**Pontos corretos:**
- **P0 está no caminho crítico técnico.** Recuperar a release tem duração externa variável (`CRONOGRAMA` §1). P1 depende dela (`PLANO_EXECUCAO` §4 P1). Há uma contingência com data marcada para 13/10 (P1 "Contingência"; `CRONOGRAMA` §4).
- A ordem P0 → P1 → P2 respeita as dependências declaradas (`README` §2).
- A exclusão de treino novo e de RunPod está de acordo com `PLANO_EXECUCAO` §3 e §5.
- O relatório de inventário bate com o marco da semana 07–13/10 (`CRONOGRAMA` §2).

**Problemas:**
1. **A escrita aparece como bloqueada, e o plano diz o contrário.** `PLANO_EXECUCAO` §4 P5 manda "começar problema, fundamentação e método enquanto P0–P2 avançam". `PLANO_ESCRITA` §6 prevê "redigir método […] registrando lacunas" em paralelo a P0/P1. A frase "a consolidação dará sustentação a Materiais e Métodos" junta três coisas diferentes: redigir o método, que pode começar agora; revisar o método; e fechá-lo, que depende de P0–P2. (O nome da seção no plano também é "Método", não "Materiais e Métodos".)
2. **A resposta mistura ordem de redação com caminho crítico.** O que limita a entrega de 11/11 é a disponibilidade da release e, depois, as tabelas congeladas até 27/10 (`CRONOGRAMA` §2 e §4). A prosa não limita. Ainda assim, ela atrasa se for toda empurrada para depois de P2.
3. **Ela omite a dependência humana que destrava P0.** O item "Identificar como obter a release exata já utilizada" está aberto no checklist (`CRONOGRAMA` §3) e só o pesquisador pode resolver. A dedicação semanal também não foi confirmada, e a escolha entre trilha essencial e completa depende dela.
4. **Ela omite que os scripts não existem.** `01_inventariar.py` está apenas especificado (`README`, "Estado: planejado"). O entregável proposto não diz se o inventário será um script versionado ou um levantamento manual, nem quais são os critérios de aceite.
5. **"Fechar as contribuições" depende de mais que a consolidação.** Depende dos resultados e da reavaliação do posicionamento (`FECHAMENTO`, "Artigo completo"; `PLANO_ESCRITA` §2 e §6). A introdução v003 não é a versão final dessas contribuições.

---

## 2. Próxima ação recomendada

### Comparação das alternativas

| Alternativa | A favor | Contra |
|---|---|---|
| **P0–P2 em sequência** | É o caminho crítico. P0 resolve a maior incerteza: release recuperável ou não até 13/10 | Seguir rígido até P2 sem escrever contraria P5. P2 depende de P1, que depende dos dados |
| **Fundamentação / Trabalhos Relacionados** | Fontes já lidas e verificadas (`MATRIZ` linhas Ding, Risse, Huang, Qwen/LoRA/QLoRA). Não tem dependência | Não está no caminho crítico e não reduz incerteza nenhuma. Trabalhos Relacionados deve ser revisado depois dos resultados (`PLANO_ESCRITA` §6) |
| **Método documentado com lacunas** | Os itens do método (`PLANO_ESCRITA` §4, 1–8) coincidem com os campos do manifesto P0. Escrever o método mostra quais metadados faltam: revisão do tokenizer, conjunto de calibração por avaliação, janela de memória | Risco de copiar números das notas. Só pode fechar depois de P0–P2 |
| **Combinação** | — | Só se justifica se uma frente alimentar a outra |

### Recomendação

**Prioridade única agora: P0.** O primeiro passo é a decisão do pesquisador sobre a origem da release. Em seguida vem o inventário dos artefatos que já estão no disco (CSVs, logs, receitas). Esse inventário não depende dos dados.

**Próximo trecho do artigo: o Método, não a Fundamentação.** Nesta semana ele entra só como **mapa de lacunas**, um subproduto do P0 e não uma segunda frente. Cada item de `PLANO_ESCRITA` §4 recebe a fonte disponível ou a lacuna e o P# que a destrava. Isso não disputa prioridade com o P0, porque usa as mesmas leituras de receitas e código.

**Prosa do Método:** começa depois do relatório P0. Os primeiros trechos são os que dependem só de código e receitas (configurações, política de prompting, definição das métricas, operador `>`, cronologia exploratória).

**Fundamentação:** fica como trabalho de reserva para quando a recuperação externa travar. Ela não deve tomar o lugar do P0.

**Sobre P2 sem P1:** as métricas globais poderiam ser reconstruídas dos logs de escores antes da auditoria de pares, porque os logs têm `target`, `nota` e `pos` (`README` §1). Isso só deveria ser feito se a contingência de 13/10 for acionada, e com o rótulo de "não certificado" (P1 "Contingência"). Antes disso, seria dispersão.

---

## 3. O que já pode ser escrito e o que depende dos dados

**Pode ser redigido agora (fontes existentes):**
- **Fundamentação:** PrimeVul, LoRA, QLoRA/NF4, Qwen. Fontes primárias já verificadas pelo Codex (`MATRIZ`).
- **Trabalhos relacionados, versão inicial:** diferenças de desenho em relação a Ding, Risse e Huang, já estabelecidas na introdução (`FECHAMENTO`, "Ciclo realizado").
- **Método, itens que dependem de código e receitas:**
  - braços e configurações (§4 item 2);
  - definições de P-C/P-V/P-B/P-R, ordenação com meio crédito e a regra `>` (`README` §5);
  - políticas de limiar como regras;
  - plano estatístico em formato de protocolo (`README` §6);
  - caráter exploratório e acesso ao teste (`PLANO_EXECUCAO` §3);
  - registro de que a correção dos empates foi feita em 06/10.
- **Ameaças à validade conhecidas antes dos resultados:** poucas seeds, pilotos com uma seed, família única, NF4/BF16 sem isolar os bits, contaminação do pré-treino não descartada.

**Pode ser revisado depois de P0:** release, revisões de modelo e tokenizer, hashes, paths, quais rodadas são oficiais, origem do log de calibração de cada avaliação (a checagem 699/2.796 frente à validação de 562 pares, `README` §4).

**Fechar o Método depende de:**
- identidade da release (P0);
- integridade dos pares, denominadores e exclusões (P1);
- confirmação de que as melhores épocas não mudaram com o meio crédito, e precisão dos limiares (P2);
- calibração do baseline de tamanho, que precisa dos dados de validação e do tokenizer (P2);
- janela efetiva de medição de memória e tempo (P4).

**Depende inteiramente da consolidação:** Resultados, Discussão, números do Resumo, título definitivo, versão final das contribuições e a afirmação "melhores épocas mantidas" (`PLANO_EXECUCAO` §3).

---

## 4. Entregáveis imediatos e critérios de aceite

**E1 — Registro da origem da release (decisão do pesquisador)**
- Aceite: lista das cópias candidatas (cópia local já usada ou fonte registrada em `00_baixar_primevul.py`).
- Aceite: impressões digitais históricas disponíveis, separando hash abreviado de hash completo (`PLANO_EXECUCAO` P0).
- Aceite: decisão registrada sobre quem obtém a release e por qual via.
- Nenhum agente faz download sem essa decisão.

**E2 — Inventário P0 dos artefatos existentes**
- Finalidade: diagnóstico, delimitado a decidir se P1 pode começar e quais lacunas o método tem. Não é auditoria.
- Aceite: cada uma das 10 linhas do CSV da etapa 3, e os resultados de prompting e do baseline, apontam para log, receita e path.
- Aceite: as rodadas oficiais estão separadas de `v01/`, `descartados/` e depuração, com justificativa.
- Aceite: as ausências estão enumeradas, e nada ausente vira zero.
- Aceite: os hashes atuais são marcados como calculados agora, não como históricos.
- Aceite: as fontes históricas ficam intactas, com hash antes e depois igual (`README` §8).
- **Fora do escopo:** auditoria de pares, recálculo de métricas, estatística.
- Decisão a tomar: implementar `01_inventariar.py` conforme a especificação ou fazer um levantamento manual. Recomendo o script mínimo, porque os hashes e o manifesto serão reaproveitados em P1–P4. Isso não autoriza implementar 02–04 agora.

**E3 — Mapa de lacunas do Método**
- Aceite: os 8 itens de `PLANO_ESCRITA` §4 aparecem, cada um com estado (fonte disponível / lacuna / desbloqueador P#).
- Aceite: nenhum número vem das notas.

**E4 — Ponto de decisão em 13/10**
- Aceite: horas reais registradas e trilha escolhida (essencial ou completa).
- Aceite: se a release não estiver acessível, a contingência P1 é registrada, com a distinção entre divergência de serialização e de conteúdo, e o estreitamento das alegações é discutido com o pesquisador.

---

## 5. Alterar o plano, atualizar o estado ou corrigir a interpretação?

- **O plano não precisa mudar.** P0–P5 e a regra de escrita em paralelo já estão certos.
- **Atualizar o estado:**
  - marcar a introdução v003 como aprovada só como seção;
  - registrar que parte das horas de leitura e posicionamento já foi gasta com as seis fontes primárias; o `CRONOGRAMA` §2 ainda reserva leitura na semana 1 e precisa ser reajustado em 13/10;
  - registrar a compilação SBC como pendência de ambiente, não de TeX.
- **Corrigir a interpretação do Codex:** a escrita não espera P2. O Método se redige agora com lacunas, revisa-se depois de P0 e fecha-se depois de P0–P2. As contribuições só fecham com os resultados.
- **Pendências reais:**
  - origem da release (pesquisador);
  - dedicação semanal e trilha;
  - limite de páginas e regras da disciplina, que afetam o tamanho da Fundamentação e de Trabalhos Relacionados;
  - os scripts de consolidação, que não existem.
- **Discordância residual:** se a dedicação real for de 10h por semana, a trilha essencial não prevê escrita na semana 1. Nesse caso o E3 deve continuar sendo um mapa curto, não prosa, para não atrasar o P0.