# Conferência crítica do parecer de 08/10/2026

**Modelo e limites.** Esta resposta é do Claude Opus 5.5 (`claude-opus-5-5`). Ela usa apenas os seis documentos colados e o meu parecer anterior. Não abri arquivos nem executei comandos ou ferramentas. Não conferi o disco, os logs, os scripts nem o texto da introdução. A minha concordância ou discordância com o Codex não prova nada sobre os resultados.

---

## 1. Origem da release: é inferência minha, corrijo

Há uma base documental parcial. O item "Identificar como obter a release exata já utilizada" está sob o título **"Preparação e decisões humanas"** (`CRONOGRAMA` §3). Os documentos, porém, não dizem que só o pesquisador pode identificar a origem nem que a decisão dele precede todo download. `PLANO_EXECUCAO` P0 indica duas vias, nesta ordem: a cópia já usada ou a fonte oficial registrada em `00_baixar_primevul.py`. `CRONOGRAMA` §5 atribui ao Codex a implementação e as verificações quando a etapa for solicitada.

**Correções:**
- Retiro "só o pesquisador pode identificar" e "nenhum agente faz download sem essa decisão".
- Mantenho uma hipótese plausível, mas não documentada: se for preciso localizar a cópia histórica, o pesquisador provavelmente terá de dizer onde ela está.
- Uma etapa futura pedida explicitamente pode incluir busca documental (script 00, impressões digitais nos registros) sem nova decisão humana a cada ação. O download segue o escopo autorizado para a etapa, não uma regra adicional que inventei.
- O E1 passa a ser "Registro das vias candidatas e das impressões digitais", executável por um agente quando for solicitado.

## 2. Capacidade limitada não é bloqueio P0

Na sua forma original, o parecer trocou um bloqueio P2 inventado por um bloqueio P0 também inventado. "Prosa do Método começa depois do relatório P0" contraria P5 e `PLANO_ESCRITA` §6, que mandam redigir o método a partir das receitas e das decisões verificadas, registrando as lacunas. Além disso, o P0 completo inclui dados recuperados que precisam bater com as impressões digitais históricas. Essa recuperação tem duração externa variável e pode travar.

A distinção correta é esta:
- **Preferência operacional, condicionada:** se a dedicação real for de cerca de 10h/semana, a trilha essencial não reserva escrita para 07–13/10 (`CRONOGRAMA` §2). Nesse caso, é razoável dar prioridade ao P0 e manter o texto curto. Isso é uma alocação de horas, não uma dependência.
- **Dependência real:** só a revisão e o fechamento dos itens afetados dependem de P0 e das etapas seguintes. Redigir não depende. O inventário documental inicial (fontes, receitas, mapeamento dos CSVs aos logs, ausências) já basta para apoiar a redação, sem esperar os dados.

## 3. Extensão correta para fechar o Método

O contrato de `PLANO_ESCRITA` §3 exige **P0–P3 e o código atual**. O item 7 do §4 (recursos, janelas de memória e tempo) depende de **P4**. O parecer citou P0–P2 e P4 em lugares diferentes, mas omitiu P3 e o código no fechamento. Fica corrigido.

O que vale para os procedimentos estatísticos:
- Agora, eles entram no texto como **protocolo planejado**, não como análises executadas.
- O Método final descreve apenas o que foi efetivamente executado e usado no texto.
- No percurso essencial, McNemar, Holm, faixas de tamanho e recalibração são opcionais (`README` §9; `CRONOGRAMA` §3). Se não forem executados, as alegações correspondentes saem do texto. Não é preciso executar tudo.

## 4. Logs globais antes da validação de identidade

- **Exigência de integridade (documentada):**
  - Um recálculo feito antes de P1 não certifica nada.
  - Ele deve ser rotulado como não certificado.
  - Não sustenta p-valores nem ICs como pares verdadeiros (P1 "Contingência").
  - Precisa gravar só saídas novas, sem tocar nas fontes (`README` §3 e §8).
- **Preferência operacional (minha):** "só se a contingência for acionada; antes disso, seria dispersão" não é proibição documental. A data de 13/10 orienta o replanejamento e não veta diagnósticos. Uma conferência inicial de consistência entre o CSV e os logs, por exemplo, pode antecipar divergências úteis a P2. Rebaixo minha frase a recomendação de prioridade sob pouca disponibilidade.

## 5. Próxima etapa concreta e a contradição

**A contradição.** Prevalece "o Método se redige agora com lacunas". A frase "prosa começa depois do relatório P0" fica retirada. A sequência correta é: redigir agora, revisar depois de P0–P1, fechar depois de P0–P3 com código e P4 no item 7.

**Prioridade técnica, a ser solicitada explicitamente.** A primeira parte do P0 é o **inventário documental**, sem recuperar dados. Ele entrega:
- as vias candidatas da release e as impressões digitais históricas, separando hashes abreviados de hashes completos;
- o mapeamento das 10 linhas do CSV da etapa 3, mais prompting e baseline, para log, receita e path;
- as rodadas oficiais separadas de `v01/`, `descartados/` e depuração;
- as ausências enumeradas.

A recuperação e a conferência dos dados vêm logo em seguida e não condicionam a redação.

**Seção a redigir.** O **Método**, itens 2, 4 e 5 de `PLANO_ESCRITA` §4:
- configurações;
- calibração e operador `>`;
- métricas global e pareada, com meio crédito.

Esses itens dependem do código e das receitas já existentes. O item 3 (cronologia) também entra, marcando como pendente de P2 a afirmação de que as épocas foram mantidas. Os itens 1, 6, 7 e 8 ficam como lacunas explícitas, com o P# que as destrava. A Fundamentação continua como reserva, não como prioridade.

**O que muda no parecer inicial:**
- **E1:** reformular, sem exclusividade do pesquisador.
- **E3:** passa de "mapa de lacunas" a prosa parcial do Método com lacunas.
- **Fechamento do Método:** passa a ser P0–P3, código e P4.
- **Logs globais:** a recomendação é reclassificada como preferência operacional.

**O plano não muda.** P5 e `PLANO_ESCRITA` §6 já estão corretos; o erro foi meu, na interpretação. Continuam válidas as atualizações de estado do parecer anterior:
- introdução aprovada só como seção;
- horas de leitura já consumidas;
- falha da compilação SBC atribuída ao ambiente;
- confirmação pendente da dedicação real e da escolha da trilha em 13/10.

Nada foi implementado nem executado nesta consulta.