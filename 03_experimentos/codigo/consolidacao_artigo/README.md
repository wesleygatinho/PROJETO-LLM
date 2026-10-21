# Especificação da implementação futura — consolidação do artigo

**Estado: planejado, ainda não implementado.** Este diretório contém a especificação; os scripts abaixo são entregáveis futuros. A etapa atual não executa downloads, inferência, treinamento nem análise estatística dos logs completos.

Referência: [plano de execução](../../../01_planejamento/artigo_seminarios_2026/PLANO_EXECUCAO.md). Implementar um fluxo em CPU que leia fontes históricas e escreva exclusivamente saídas derivadas novas. Não importar `classificador.py` diretamente para depender de torch/modelos; extrair ou reimplementar funções numéricas leves, verificando sua equivalência com casos controlados.

## 1. Contratos de entrada

- CSVs: `resultados_etapa1.csv`, `resultados_pareado.csv`, `treinos_etapa3.csv`, `resultados_etapa3.csv` em `03_experimentos/resultados/`.
- Logs: JSONL de prompting e scores; receitas JSON de treino em `03_experimentos/logs/`.
- Dados: arquivos da release original recuperados em `03_experimentos/dados/`. Hoje estão ausentes localmente.
- Tokenizer: apenas quando contagem/reconstrução das entradas exigir, usando revisão compatível documentada. Não carregar pesos do modelo para contar tokens.
- Configuração futura: lista explícita de rodadas incluídas, paths relativos à raiz, políticas de decisão, comparações, semente da reamostragem e número de réplicas.

Na inspeção inicial, logs de scores contêm `pos`, `idx`, `project`, `commit_id`, `func_hash`, `target`, `nota`, `pred`, além de `truncada`/`n_tokens` quando gravados. Logs de prompting usam `i` para ordem de execução e `pos` para a posição no conjunto; ambos não são intercambiáveis. `func_hash` pode ser nulo. O baseline não registra todos os extras dos classificadores e não foi localizado log de validação correspondente: prever reconstrução em CPU.

## 2. Scripts e dependências

| Script futuro | Função | Entrada principal | Saída planejada |
|---|---|---|---|
| `01_inventariar.py` | Manifesto, schemas, contagens, hashes e fontes ausentes | Configuração + CSVs/logs/dados | `manifesto.json`, `inventario.csv`, `fontes_ausentes.md` |
| `02_consolidar_metricas.py` | Junção auditada, pares, limiares e métricas; diagnósticos de truncamento | Manifesto + JSONL + dados | `auditoria_integridade.json`, `pares_auditados.csv`, `metricas_por_execucao.csv`, `divergencias.csv`, `sensibilidade_truncamento.csv` |
| `03_estatistica.py` | Agregações por seed, bootstrap alinhado e McNemar especificado | Saídas auditadas + previsões alinhadas | `estatistica.json`, `intervalos.csv`, `comparacoes.csv` |
| `04_exportar_artigo.py` | Tabelas e figuras a partir de saídas validadas | Métricas + estatística + metadados de recursos | `tabelas/*.csv`, figuras finais e `proveniencia_exports.json` |
| `tests/` | Casos pequenos de falha e invariantes científicos | Fixtures sintéticas mínimas | Resultado de verificações, sem dados/modelos grandes |

Ordem: 01 → 02 → 03 → 04. Inventário pode emitir relatório incompleto, mas exportação final deve bloquear resultados sem integridade suficiente. Scripts devem receber raiz e destino por argumentos, evitando dependência de diretório corrente. Não fornecer comandos como executáveis existentes antes de implementar esses arquivos.

Dependências esperadas: biblioteca padrão Python, NumPy, scikit-learn, SciPy e biblioteca de gráficos. Registrar versões do ambiente efetivamente utilizado; não presumir que o ambiente CPU precise reproduzir toda a instalação CUDA do treinamento. Manter os requisitos históricos atuais preservados.

## 3. Manifesto e rastreabilidade

Identificador estável de avaliação deve distinguir treino, seed, época, variante e split; uma linha de avaliação não equivale a um treino novo. Registrar caminho e hash das entradas, instante da consolidação, versão dos scripts, parâmetros estatísticos e lista de exclusões. Recalcular hashes completos agora sem tratá-los como metadados que existiam na execução histórica.

Rodadas oficiais são selecionadas explicitamente: não usar somente glob de arquivos por data. Linhas de depuração e releases antigas continuam acessíveis, porém não entram no agregado principal. Um arquivo/resultado ausente não deve virar zero nem ser omitido silenciosamente.

## 4. Junção e pares

Chave de função: split/release + posição verificada + identificadores disponíveis. Construir uma tabela de correspondência com os dados oficiais. Rejeitar duplicatas, posições fora do conjunto, divergência de alvo, commit/projeto incompatível e logs incompletos em comparações com denominador integral.

Chave de par deve preservar as duas identidades oficiais; não usar apenas projeto/commit. Verificar que um membro não foi reutilizado em pares diferentes de forma indevida. Conferir o esquema de emparelhamento oficial contra os arquivos e documentar a validação. Ausência de metadado deve ser registrada, não preenchida por heurística.

Verificar consecutividade, alvos opostos, mesmo projeto/commit, IDs/posições únicos e ausência de reutilização. Conferir nomes/assinaturas, caminho e diff onde disponíveis, com revisão manual de mudanças legítimas ou ambiguidades; não tratar nome igual como certificado de identidade nem renomeação como exclusão automática. Se dados oficiais não forem recuperados, a reconstrução pelos logs deve ser rotulada preliminar, sem certificado de pareamento real. A contingência e sua data estão no plano P1.

Contagens de referência da release usada: teste global 25.911 (695 vulneráveis/25.216 benignas), teste pareado 1.128/564, validação pareada 1.124/562. Conferir também validação global e a amostra de validação efetivamente usada nas receitas; elas não precisam ser o mesmo conjunto. A receita 7B registra checagem global com 699 vulneráveis e 2.796 benignas: identificar quais dados geraram o log de calibração de cada avaliação, sem confundir treino, checagem e avaliação completa.

Não reutilizar a tolerância de `formar_pares` como política de integridade. No código atual, `len(dados)//20` conta funções e pode tolerar cerca de 10% dos pares; essa observação é um risco do procedimento, não evidência de erro nas rodadas já executadas.

## 5. Métricas e precisão numérica

Para scores contínuos:

- Calibrar F1 no log de validação apropriado, reproduzindo algoritmo e operador `nota > limiar`; aplicar o mesmo limiar ao teste global e, em tabela derivada, ao pareado.
- Gravar scores/limiares de trabalho sem novo arredondamento; usar arredondamento apenas na apresentação. Explicar a precisão disponível nos registros históricos.
- Reconstruir FNR/FPR no limiar calibrado para FPR≤0,5% no dev; reportar FPR realmente observado no teste. Resultado de oráculo fica separado.
- Calcular AUC somente com duas classes; caso contrário, registrar indisponibilidade.
- Manter métricas no limiar zero como históricas/diagnósticas, com coluna `politica_decisao` distinta.

Para prompting: reproduzir classificação e tratamento de indefinidos registrados; não gerar AUC ou ordenação de scores inexistentes. Para o baseline, recalcular tamanho e calibração em CPU se a validação não estiver registrada. Registrar truncamento da medida, revisão do tokenizer e janela de contexto.

Conferir as definições contra PrimeVul e declarar diferenças da implementação própria. O limiar VD-S do baseline no teto de 2.048, com operador `>`, não dispara previsões: explicitar o efeito do clipping. Não executar o script histórico 08 para essa reconstrução sem controlar saídas, pois ele escreve na planilha histórica. Conferir por época o efeito retrospectivo da correção de empates na seleção, sem assumir metadados históricos completos.

Por par: P-C=(1,0), P-V=(1,1), P-B=(0,0), P-R=(0,1), orientando vulnerável primeiro. Ordenação ajustada = `(n_estritamente_ordenados + 0,5*n_empates)/n_pares`. Empate é igualdade no score disponível; não adicionar epsilon ajustado ao teste. Se outro critério de empate for necessário pela precisão histórica, justificá-lo como sensibilidade, sem redefinir silenciosamente a métrica.

P-C tem referência de acaso dependente da política. A referência 25% pressupõe respostas independentes e equiprováveis; não é universal. Ordenação com meio crédito tem referência 50% sob simetria. Nenhuma dessas referências prova ausência/presença de compreensão sem análise dos pressupostos.

Conferir divergências: valor original, valor reconstruído, fonte, regra, diferença, causa e decisão. O arredondamento publicado permite tolerância na representação, mas divergência em contagens ou identidade sempre exige diagnóstico.

## 6. Estatística

Proposta inicial: 2.000 réplicas de bootstrap com semente fixa e registrada, verificando estabilidade dos endpoints antes de exportar. Aumentar réplicas somente se a estabilidade/comparação exigir e houver tempo de CPU; registrar número final e método de intervalo. Não escolher número ou método porque favorece a conclusão.

- Pares: unidade de reamostragem é o par completo. Comparações usam o mesmo vetor de índices. Para média das três seeds, preservar as três avaliações por par; IC é condicional aos modelos treinados.
- Global: funções alinhadas entre configurações; preservar estratos de classe quando essa for a política escolhida. Reportar dependência por projeto/commit como limitação; sensibilidade por agrupamento é opcional. Se uma métrica ficar indefinida numa réplica, registrar política e frequência, sem descarte silencioso.
- Seeds: fornecer valores individuais, média e dispersão observada. Não usar previsões de três seeds como três vezes mais dados de teste, nem vender bootstrap de três seeds como precisão alta da variabilidade de treino.
- McNemar exato: evento complementar definido neste plano é P-C no limiar de maior F1 da validação, NF4/BF16 da mesma seed. Guardar a tabela 2×2 e discordâncias; Holm na família de três testes caso apresentada. Se evento histórico das notas for outro, reconstruí-lo e rotular como análise separada, ou retirar o p-valor.
- Especificar esse evento como P-C no `limiar_decisao` de maior F1 na validação, nunca no `limiar_vds`. NF4/BF16 possuem calibrações separadas; discordâncias incluem efeitos do score e do limiar. Poucos eventos/discordâncias limitam o poder. McNemar/Holm são análises complementares opcionais no percurso essencial; bootstrap da ordenação ajustada permanece a análise principal.
- Ordenação com meio empate: estimar diferença e IC por bootstrap de pares; não aplicar McNemar diretamente aos valores 0/0,5/1.
- Não usar ausência de significância como teste de equivalência. Um teste de equivalência exigiria margem e desenho próprios; não faz parte do percurso obrigatório.

## 7. Truncamento, tamanho e recursos

Auditar sinalizadores de truncamento por configuração, split e par. Recalcular métricas no subconjunto em que ambas as versões não foram truncadas, mantendo limiares originais. Informar que isso muda a composição da amostra e não resolve generalização para funções longas.

Para afirmar entradas idênticas após corte, recuperar código e tokenizer correto e comparar sequências; scores iguais isoladamente não bastam. Análise por faixas de tamanho deve registrar limites, cobertura e faixas sem duas classes; evitar tratá-la como isolamento causal de todos os atalhos.

Recursos: importar metadados históricos, separar alocado após carga, pico da janela instrumentada, tempo de pontuação do teste, tempo total avaliado, tempo de treino e custo computacional estimado. Verificar a janela do pico no código. Não fabricar medições de energia, TTFT/TPOT ou repetição independente. Não unificar métricas de prompting e classificação numa curva que pressupõe motores, batching e contextos iguais.

## 8. Verificações necessárias

- Log reordenado deve produzir a mesma junção; `i` não deve substituir `pos`.
- Duplicata, falta de membro e mesmo commit com múltiplas funções devem falhar ou gerar exclusão explícita, sem formar par arbitrário.
- Rótulos, soma das categorias e tamanho do denominador devem fechar.
- Todos os scores empatados resultam em ordenação ajustada 0,5; par invertido modifica o sinal corretamente.
- Valor exatamente no limiar deve obedecer `>`; limiar calibrado não consulta o teste.
- McNemar sem discordâncias retorna p=1; fixture com discordâncias conhecidas verifica o teste exato.
- Bootstrap mantém pares e alinhamento entre variantes/seeds; não concatena seeds como unidades independentes.
- Fontes históricas permanecem intactas; hashes anteriores/depois são iguais para entradas.

Não escrever testes que apenas repitam fórmulas do próprio script: usar casos adversos, valores esperados independentes e invariantes acima. Uma implementação que roda sem erro não satisfaz, por si só, os critérios científicos.

## 9. Percurso essencial versus completo

No percurso essencial, implementar as mesmas garantias de leitura/junção/métricas, resultados por seed, bootstrap pareado da ordenação e sensibilidade de truncamento. Exportar somente tabelas/figuras usadas nas alegações. Não exigir McNemar, correlações adicionais, quartis, AUC por faixas, ensembles ou bootstrap recalibrando validação; retirar as respectivas alegações se essas análises não forem executadas. Se uma conclusão global exigir um IC específico, incluí-lo ou limitar a conclusão, sem conservar o texto sem sua evidência.

No percurso completo, acrescentar as análises de sensibilidade/estatística que tenham utilidade para perguntas e conclusões. A existência desta especificação não autoriza novos treinamentos nem implica necessidade de executar toda análise possível.
