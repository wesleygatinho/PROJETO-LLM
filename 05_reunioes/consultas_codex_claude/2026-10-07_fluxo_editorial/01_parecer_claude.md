# Parecer bruto sobre o desenho

Retorno literal do Claude. Recomendações não são decisões automaticamente adotadas; consulte o README integrado.

# Parecer sobre o mecanismo redator → revisor → corretor

**O que li:** os quatro documentos pedidos e a listagem de `04_escrita/artigo/seminarios_2026/` e de `05_reunioes/consultas_codex_claude/`. Não abri a amostra, o plano de escrita, os pareceres anteriores nem o código. Não editei arquivos nem executei comandos.

**Fatos que afetam o desenho:**
- `revisao/` só tem `.gitkeep` e o manuscrito não foi iniciado (README:3).
- O registro de decisões da matriz ainda está "A preencher" (MATRIZ_EVIDENCIAS:61). Por isso, ainda não existe identificador de alegação que um apontamento de evidência possa citar.
- O guia diz que itens numéricos só fecham após P2–P4 (PADRAO_ESCRITA:125).
- Nesses diretórios, não encontrei o script da "ponte já existente". Só vi pastas de consultas com `solicitacao.txt`, `parecer_claude.md` e `resposta.json`. Não confirmei onde a ponte está nem como funciona.

## 1. Distribuição realista dos papéis

Recomendo **não** usar Claude como corretor por padrão. Se Claude corrige e outra chamada do Claude revisa, o mesmo modelo avalia a própria correção. Contextos separados reduzem esse viés, mas não criam independência. A conferência do Codex também não é uma revisão independente, porque o Codex integra o texto.

| Papel | Quem | Observação |
|---|---|---|
| Redator | Codex | Escreve a partir do briefing, do guia e da matriz |
| Corretor | Codex (padrão) | Responde a cada ID do parecer |
| Revisor | Claude Opus 5.5, uma chamada nova por versão | Recebe a versão, o parecer anterior e as respostas, mas não o histórico da conversa |
| Corretor alternativo | Claude, só para reescritas pontuais pedidas pelo pesquisador | A versão gerada exige revisão em outra chamada; o registro marca "corretor e revisor = mesmo modelo" |
| Árbitro | Pesquisador | Decide contestações, apontamentos de decisão editorial e a integração final |

O campo `modelo` do registro deve ser preenchido pelo controlador com o que a CLI informa. Não deve vir de autodeclaração dentro do JSON gerado pelo modelo.

## 2. Contrato JSON mínimo

**Parecer (`parecer/1`)**
```json
{
  "schema": "parecer/1",
  "rodada": "R003",
  "versao_id": "v2",
  "sha256_texto": "…",
  "sha256_contexto": {"briefing": "…", "padrao": "…", "matriz": "…", "checklist": "…"},
  "escopo": "Seção 3, parágrafos 1–4",
  "verificacoes_anteriores": [
    {"id": "R002-03", "estado": "resolvido|nao_resolvido|regressao|aceito_contestacao"}
  ],
  "apontamentos": [{
    "id": "R003-01",
    "severidade": "critica|maior|menor|sugestao",
    "tipo": "editorial|terminologia|citacao|evidencia|decisao_pesquisador",
    "trecho": "citação literal exata da versão",
    "problema": "…",
    "acao_sugerida": "…",
    "alegacao_ref": "A-07 ou null"
  }]
}
```

**Resposta do corretor (`resposta/1`)**
```json
{
  "schema": "resposta/1",
  "versao_origem": "v2",
  "sha256_origem": "…",
  "sha256_parecer": "…",
  "sha256_versao_nova": "…",
  "respostas": [{
    "id": "R003-01",
    "acao": "reescrito|limitado|retirado|contestado|pendente_fonte",
    "justificativa": "…",
    "evidencia": "A-07@sha256 ou null"
  }]
}
```

**Regras de validação, sem reparo silencioso: um JSON inválido é rejeitado.**
- O `trecho` precisa existir literalmente na versão com aquele hash. Isso barra apontamentos sobre texto inexistente ou de outra versão e é barato de checar.
- A resposta precisa cobrir **exatamente** os IDs do parecer: sem faltantes, duplicados ou extras.
- O corretor não pode rebaixar severidade nem mudar o tipo de um apontamento.
- O controlador **calcula** a aptidão a partir dos apontamentos e das verificações. Não há campo "veredito" a confiar; se existir, deve ser consistente com o cálculo ou o parecer é rejeitado.

## 3. Mudança editorial e resolução científica

Esta é a principal falha da proposta: "evidência não se resolve só por reescrita" ainda não tem mecanismo concreto.

- **`editorial` / `terminologia`:** a reescrita resolve, desde que confirmada por `verificacoes_anteriores` na revisão seguinte. Um "reescrito" declarado pelo corretor nunca basta.
- **`evidencia`:** só se resolve de duas formas:
  - **(a)** apontando uma linha da matriz com decisão "manter" ou "limitar", fonte exata e hash do arquivo de resultado;
  - **(b)** retirando ou enfraquecendo a alegação no texto, confirmado pelo revisor seguinte.

  A saída (b) é legítima e coerente com o plano (PLANO_EXECUCAO:127). Ela deve ficar registrada como "retirada", não como "corrigida".
- **`citacao`:** exige registro da fonte com página, conforme MATRIZ_EVIDENCIAS seção 3. Um trecho de OCR não basta.
- **`decisao_pesquisador`:** só o pesquisador fecha.

**Pré-requisito antes do script:** a matriz precisa ganhar IDs de alegação (A-01…) com uma tabela legível por máquina, por exemplo `alegacoes.json` dentro do artigo. A matriz em Markdown continua sendo a versão para leitura humana. Sem esses IDs, "bloqueio de evidência" vira um estado sem saída.

**Verificação numérica leve:** o script extrai números do texto e marca os que não estão associados a nenhuma `alegacao_ref`. Enquanto P2–P4 não terminarem, todo número fica em `bloqueio_evidencia`. Isso não certifica valores, só impede que entrem sem vínculo.

## 4. Pareceres antigos, versões e contexto

- **Hash só do texto é insuficiente.** Uma aprovação vale para o par (texto, contexto). Se a matriz, o guia, o briefing ou um CSV de resultados citado mudar, o parecer vira `obsoleto`, mesmo com o texto idêntico. Por isso existe `sha256_contexto`. A mudança no guia em 07/10 mostra que isso acontece.
- **Cuidado com CRLF no Windows.** Calcule o hash sobre a cópia guardada na pasta da rodada, em bytes, e não sobre o arquivo de trabalho. Esse arquivo pode ser alterado por `autocrlf` ou pelo editor e gerar falsos "texto alterado".
- **Versão-fonte:** declarada explicitamente no manifesto (`origem: v2@sha`), nunca inferida do nome do arquivo, como já está na proposta.
- **Aprovação parcial:** a aprovação dos parágrafos 1–4 não cobre a seção. Ao integrar trechos aprovados, as transições e a coerência mudam. É preciso uma **revisão de integração** do texto já montado em `texto/`, com escopo próprio.
- **Edições diretas no manuscrito:** o status `integrado` guarda o hash do trecho. Se o manuscrito tiver sido editado fora do fluxo, a checagem detecta a divergência e o trecho volta a `rascunho`.

## 5. Conflitos e limite de rodadas

- O corretor pode responder `contestado`, mas a contestação fica pendente até o revisor aceitá-la na rodada seguinte (`aceito_contestacao`) ou o pesquisador decidir.
- Se o parecer conflitar com o PADRAO_ESCRITA, vale o guia. Mudar o guia é decisão do pesquisador e invalida os pareceres que dependem dele (pelo hash).
- **Limite de rodadas:** proponho 3 por trecho. Depois disso, o caso sobe ao pesquisador. Isso evita ciclos caros de reescrita entre modelos e respeita a regra de uma chamada explícita por vez.
- Sugestões (`sugestao`) não bloqueiam e podem ser recusadas com uma linha de justificativa.

## 6. Critério de incorporação

O status `apto_para_integrar` exige, ao mesmo tempo:
1. um parecer da versão **exata** com o contexto vigente;
2. zero `critica` ou `maior` abertos;
3. zero `evidencia` sem fechamento por (a) ou (b);
4. todos os IDs anteriores verificados pelo revisor, e não só declarados pelo corretor;
5. contestações decididas;
6. confirmação explícita do pesquisador, registrada como evento.

A aprovação refere-se ao escopo revisado. Ela não certifica números, leitura de literatura nem autoria.

## 7. Outras falhas e ajustes

- **Log de eventos:** um `eventos.jsonl` só com acréscimos é útil, mas não é à prova de adulteração e não deve ser apresentado como auditoria. O Git é o registro efetivo.
- **Demonstração na AMOSTRA_REDACAO:** marcar a rodada como `demonstracao`, numa pasta separada, para não aparentar artigo iniciado. A amostra é explicitamente ilustrativa (PADRAO_ESCRITA:123).
- **Testes offline que faltam na lista:**
  - `trecho` inexistente na versão;
  - contexto alterado com texto igual, que deve tornar o parecer obsoleto;
  - corretor rebaixando severidade;
  - `retirado` sem confirmação do revisor;
  - número sem `alegacao_ref`;
  - integração com a pesquisadora ou o pesquisador ainda sem confirmar;
  - quarta rodada, que deve escalar ao pesquisador.
- **Pedido ao revisor:** incluir a instrução de citar literalmente e de não avaliar números contra memória ou literatura não fornecida, só contra a matriz e as fontes indicadas.
- **Gravação confinada:** valide os caminhos resolvidos com `resolve()` comparado à raiz `04_escrita/artigo/seminarios_2026/revisao/`, incluindo links simbólicos e junções do Windows. Não use comparação de strings.

## Limites desta verificação

- Não confirmei a ponte existente nem o orçamento da CLI.
- Não li a AMOSTRA_REDACAO, o PLANO_ESCRITA nem os pareceres anteriores.
- Não avaliei código.