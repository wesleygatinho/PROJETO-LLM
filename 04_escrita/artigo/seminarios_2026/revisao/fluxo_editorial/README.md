# Fluxo editorial Codex–Claude

Um único projeto de artigo, com três papéis e registros separados. Criado a pedido do pesquisador e discutido com Claude Opus 5.5. O controlador local é [gerenciar.py](gerenciar.py), sem dependências externas. A ponte de execução está em [consultar_claude.py](consultar_claude.py), que usa o Claude Code já instalado e a autenticação existente.

## Distribuição adotada

| Papel | Executor padrão | Entrega |
|---|---|---|
| Redator | Codex | Rascunho a partir do briefing, fontes e padrão de escrita |
| Revisor | Claude Opus, chamada nova por versão | Parecer com trecho literal, problema, gravidade e ação por ID |
| Corretor | Codex, em etapa separada | Nova versão e resposta a todos os IDs |
| Conferência após correção | Claude, nova chamada; Codex confere fontes e incorporação | Confirmação de resolução de cada apontamento e busca de regressões |
| Decisão acadêmica/editorial final | Pesquisador | Resolve conflitos e responde pelo artigo e pela entrega |

O mecanismo permite Claude como redator ou corretor em chamadas próprias. Essa alternativa exige explicitar a troca de executor e mantém a nova revisão obrigatória. Três papéis não significam três modelos independentes. Codex redator/corretor também não oferece independência entre esses dois papéis; a crítica entre modelos reduz alguns pontos cegos, sem garantir ausência de erro.

## Ciclo por trecho

1. Registrar briefing com objetivo, escopo do trecho, fontes permitidas e estado das análises. Selecionar finalidade artigo ou demonstração.
2. Produzir e registrar o rascunho. A versão armazenada recebe SHA256 sobre seus bytes.
3. Gerar o pacote do revisor e consultar Claude. Importar o retorno validado, preservando resposta bruta e modelo real da CLI.
4. Corrigir os apontamentos, com resposta por ID. Nova versão é um novo artefato; a anterior permanece preservada.
5. Submeter a versão corrigida a nova revisão. O revisor verifica cada ID anterior e procura novos problemas.
6. Após aprovação científica/editorial e conferência documentada das afirmações, incorporar explicitamente o trecho em `texto/secoes/`. Aprovação só editorial não libera essa incorporação.
7. Revisar também o artigo montado: coerência entre seções, transições, bibliografia, tabelas/figuras, Resumo/Abstract e PDF SBC. Aprovar trechos isolados não aprova o artigo inteiro.

Há uma demonstração em [rodadas/demo_editorial_01/manifesto.json](rodadas/demo_editorial_01/manifesto.json). Seu briefing inclui uma preferência de concisão para exercitar uma correção; não se inventou erro científico. Ela não pode entrar no manuscrito.

## Comandos

Executar na raiz do projeto com Python 3.11 ou superior. Exemplo usando o runtime disponível neste computador:

```powershell
$pyArtigo = 'C:\Users\santo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$fluxoArtigo = '.\04_escrita\artigo\seminarios_2026\revisao\fluxo_editorial'
& $pyArtigo -B "$fluxoArtigo\gerenciar.py" status demo_editorial_01
```

Para um novo trecho, primeiro salvar um briefing dentro do projeto. Os nomes abaixo são exemplos; não representam seções já escritas. Cada comando é uma ação explícita:

```powershell
& $pyArtigo -B "$fluxoArtigo\gerenciar.py" iniciar introducao_01 --briefing '04_escrita/artigo/seminarios_2026/revisao/briefing_introducao.md' --finalidade artigo --fonte 'CAMINHO_RELATIVO_DA_FONTE_CONFERIDA'
& $pyArtigo -B "$fluxoArtigo\gerenciar.py" rascunho introducao_01 --texto 'CAMINHO_DO_RASCUNHO_DENTRO_DO_PROJETO' --autor 'Codex — redator'
& $pyArtigo -B "$fluxoArtigo\consultar_claude.py" introducao_01 revisar --modelo opus
& $pyArtigo -B "$fluxoArtigo\gerenciar.py" parecer introducao_01 --entrada 'CAMINHO_DA_RESPOSTA_JSON_IMPRESSO_PELA_PONTE'
```

Para corrigir com Codex: `pedido introducao_01 corrigir` imprime o pacote; o Codex lê o pacote e salva JSON conforme [prompt do corretor](prompts/corrigir.md). Importar com `correcao introducao_01 --entrada CAMINHO_JSON`, depois consultar `revisar` e importar novo `parecer`.

Para Claude redigir: criar rodada sem rascunho, executar a ponte com papel `redigir` e importar usando `redacao ... --entrada ...`. Para Claude corrigir: executar a ponte com papel `corrigir` e importar usando `correcao ... --entrada ...`. **A ponte não importa ou aprova automaticamente.**

Também é possível usar `pedido ... revisar` e a ponte histórica externa, preservada. O controlador aceita tanto o JSON do papel quanto o envelope JSON da CLI. Arquivo com texto livre, hash errado ou contrato inválido é rejeitado; não é corrigido silenciosamente.

Para incorporação final de um trecho, `integrar ID --verificacao CAMINHO_JSON` requer:

```json
{
  "versao": 2,
  "sha256": "hash real da versão aprovada",
  "verificador": "executor da conferência final",
  "pendencias": [],
  "checagens": [{
    "alegacao": "afirmação exata conferida",
    "fonte": "caminho relativo de fonte já registrada",
    "localizador": "página/linha/chave/registro preciso",
    "verificacao": "o que foi verificado e quais condições limitam a afirmação"
  }]
}
```

A cobertura de todas as afirmações materiais é responsabilidade do verificador; o script valida campos, vínculos e integridade, não entende nem reproduz resultados científicos. Campos preenchidos sem verificação real não tornam o artigo válido. Não há integração automática, sobrescrita de seção existente ou entrega/publicação automática.

## Estados e impedimentos

| Estado | Significado |
|---|---|
| aguarda_redacao | Briefing registrado; nenhum texto produzido |
| rascunho | Versão inicial sem parecer |
| aguarda_correcao | Parecer com problemas abertos |
| bloqueado_evidencia | Falta fonte/conferência/decisão para resolver o parecer |
| aguarda_nova_revisao | Corretor declarou atendimento; falta revisão da nova versão |
| apto_editorial | Aprovação apenas da redação; não certifica afirmações |
| apto_integrar | Revisor declarou aprovação científica/editorial; falta conferência de integração |
| integrado | Trecho copiado explicitamente; não equivale ao artigo final aprovado |

Fontes, guia, briefing, prompts e arquivos registrados têm hashes. Uma mudança torna o pacote incompatível e impede continuar: iniciar nova rodada com contexto atualizado. Apontamento precisa citar trecho literal da versão. Pareceres de outra versão/contexto, IDs duplicados/faltantes e aprovação com pendências são rejeitados. Correção científica exige fonte/localizador/verificação ou retirada explícita da alegação, novamente conferida pelo revisor.

O contrato é conservador: qualquer item aberto bloqueia aprovação; sugestões opcionais vão em limites como recomendações. Não há adjudicação automática de contestações. Se um parecer contrariar evidência ou o guia, preservar o parecer e registrar a discussão em documento próprio; o Codex confronta as fontes e consulta novamente ou encaminha ao pesquisador uma decisão concreta. Não é necessário pedir autorização para cada correção rotineira já solicitada.

Pendências declaradas pelo redator em uma resposta de redação também impedem integração. Para encerrá-las, resolver a fonte ou retirar a alegação e abrir nova rodada com o texto/contexto atualizado; uma aprovação posterior não apaga essa declaração silenciosamente.

Após três ciclos sem convergência, revisar escopo e divergência antes de outra chamada; limite recomendado, não temporizador ou bloqueio automático. Não consumir chamadas repetidas para obter aprovação a qualquer custo.

## Integridade e limites de implementação

- Apenas biblioteca padrão; Python local, sem GPU/RunPod. Gerenciar não acessa rede. Consultar chama explicitamente Claude, podendo consumir limites do plano existente.
- Uma sessão nova por consulta, Read/Glob/Grep, safe/restricted, sem MCP, edição, shell do agente ou persistência de sessão. Modelo real vem do retorno modelUsage, não da autodeclaração do texto. Nenhum ajuste global.
- Consulta limitada a 15 minutos e `--max-budget-usd 3`. Estimativa da CLI não comprova cobrança avulsa. Sem repetição automática após erro.
- Gravação limitada às rodadas e à cópia explícita em `texto/secoes/`; leituras de fontes são dentro do projeto, excluindo caminhos ocultos/credenciais comuns. Isso é uma restrição auxiliar de caminhos, não um detector universal de segredos.
- Operações **sequenciais**, um controlador por rodada. Não há trava entre processos: não executar duas operações simultâneas na mesma rodada. Gravação do manifesto usa arquivo temporário; versões e retornos não são sobrescritos.
- Hashes detectam mudanças acidentais; manifesto/eventos locais não são registro inviolável nem assinatura. Git pode registrar versões por decisão posterior do pesquisador; nenhum commit foi criado aqui.
- A conferência dos guias não substitui leitura primária. A matriz científica continua com verificações pendentes. Revisão de texto não conclui P2–P4.

Os contratos completos estão nos [prompts do redator](prompts/redigir.md), [revisor](prompts/revisar.md) e [corretor](prompts/corrigir.md). Os [testes offline](test_gerenciar.py) exercitam rejeições e o ciclo com dados fictícios em pastas temporárias do projeto.
