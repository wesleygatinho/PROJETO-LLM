# Cronograma e acompanhamento — entrega em 11/11/2026

Data-base: 07/10/2026. Horários e datas de referência: America/Sao_Paulo. Este é um planejamento, não um agendamento automático. A dedicação de **10h/semana** vem do cronograma geral e ainda precisa ser confirmada para esta entrega.

## 1. Duas trilhas de carga de trabalho

| Bloco | Completa | Essencial | Dependência |
|---|---:|---:|---|
| Inventário e recuperação da release | 3h | 4h | Fontes acessíveis; localizar cópia histórica se necessário |
| Auditoria de identidade e pares | 4h | 4h | Inventário + dados |
| Métricas e limiares | 5h | 4h | Logs, receitas e auditoria |
| Estatística | 5h | 3h | Métricas consistentes; essencial prioriza bootstrap da ordenação e valores por seed |
| Sensibilidades/descritivas adicionais | 4h | Incluídas acima apenas as essenciais | Truncamento essencial; demais alegações dependem das análises executadas |
| Recursos, tabelas e figuras | 3h | 2h | Metadados e resultados auditados |
| Leitura e posicionamento | 10h | 6h | Núcleo primário, incluindo Huang antes de fechar contribuições |
| Escrita do manuscrito completo | 20h | 16h | Padrão SBC adotado; resultados para fechar seção empírica |
| Bibliografia | 2h | Incluída na leitura/escrita | Metadados primários verificados |
| Revisão técnica e formatação | 6h | 3h | Rascunho completo |
| Apresentação e ensaio | 6h | 4h | Narrativa estabilizada |
| Margem para imprevistos | 4h | 4h | — |
| **Total de referência** | **72h** | **50h** | Trabalho ativo, não duração de GPU |

A versão completa corresponde a aproximadamente **14–15h/semana**; a essencial ocupa as cinco semanas a **10h/semana**, incluindo somente 4h internas de margem. Ambas resultam em um artigo com todas as partes científicas; diferem em aprofundamento, análises suplementares e quantidade de peças visuais. A essencial não reduz os requisitos de integridade e transparência.

As horas são ordens de grandeza acordadas na revisão Codex–Claude, sem base na produtividade histórica do pesquisador. Downloads, execução em CPU, recuperação externa e feedback têm duração variável, além do trabalho ativo. O padrão editorial foi definido; limite de páginas e regras específicas da disciplina ainda podem afetar o esforço. Medir horas reais na primeira semana e replanejar em **13/10**; não tratar 72h/50h como garantia. Se disponibilidade for próxima de 10h/semana, começar pela essencial e acrescentar análises apenas depois de fechar o núcleo.

## 2. Marcos por semana

| Período | Completa | Essencial | Marco verificável |
|---|---|---|---|
| **07–13/10** | Inventário 3h, pares 4h, leitura 6h, escrita 2h = **15h** | Inventário 4h, pares 4h, leitura 2h = **10h** | Fontes identificadas e primeiro relatório de integridade; padrão editorial decidido em 07/10; revisão do esforço real |
| **14–20/10** | Métricas 5h, estatística 4h, leitura 3h, escrita 3h = **15h** | Métricas 4h, estatística 3h, leitura 2h, escrita 1h = **10h** | Métricas reconstruídas, incerteza essencial e início do texto apoiado em fontes |
| **21–27/10** | Estatística 1h, sensibilidades 4h, exports 3h, leitura 1h, escrita 6h = **15h** | Exports 2h, leitura 2h, escrita 6h = **10h** | Resultados essenciais congelados; leitura focalizada concluída |
| **28/10–03/11** | Escrita 9h, bibliografia 2h, revisão 4h = **15h** | Escrita 9h, revisão 1h = **10h** | Rascunho integral até 03/11; revisão docente solicitada quando viável |
| **04–10/11** | Revisão 2h, apresentação/ensaio 6h, margem 4h = **12h** | Revisão 2h, apresentação/ensaio 4h, margem 4h = **10h** | Versão final alvo em 06/11; arquivos conferidos até 09/11; ensaio até 10/11 |
| **11/11** | Entrega e apresentação | Conforme disciplina | Arquivo final e material de apresentação disponíveis |

O esboço da apresentação pode ser preparado durante a escrita, ainda que as horas reservadas ao material final/ensaio estejam na última semana. O pesquisador pode antecipar o pedido de revisão docente enviando método e tabelas verificadas antes do texto completo. O plano não pressupõe reunião marcada nem retorno em uma data específica. Não aguardar feedback externo indefinidamente para concluir a revisão interna.

## 3. Checklist de execução

**Preparação e decisões humanas**

- [x] Delimitar o artigo ao bloco Qwen existente, sem exigir novos treinamentos.
- [x] Criar o plano e a organização de pastas.
- [x] Definir padrão de redação, português acadêmico, template SBC local, Resumo/Abstract e referências autor–ano.
- [ ] Confirmar limite de páginas, autoria/afiliação, bibliografia científica própria e regras específicas da disciplina.
- [ ] Confirmar dedicação disponível e duração/formato da apresentação.
- [ ] Escolher a trilha essencial/completa conforme disponibilidade, medindo o esforço real em 13/10.
- [ ] Identificar como obter a release exata já utilizada.

**Consolidação técnica**

- [ ] P0: manifesto, hashes e lista de fontes ausentes.
- [ ] P1: identidade/cobertura dos conjuntos e 564 pares de teste auditados.
- [ ] P2: limiares, F1, FPR, FNR, AUC e categorias pareadas reconstruídos com política explícita.
- [ ] P2: verificar precisão de scores e arredondamentos de limiares.
- [ ] P3: resultados por seed, bootstrap pareado e diferenças de implantação reproduzíveis.
- [ ] P3 opcional: McNemar no P-C no limiar de maior F1 do dev e Holm, se essas análises forem utilizadas no texto.
- [ ] P3: truncamento e empates descritos com denominadores.
- [ ] P4: memória, tempo e custo histórico classificados por janela de medição.
- [ ] P4: tabelas/figuras vinculadas às fontes e divergências resolvidas ou documentadas.

**Escrita e entrega**

- [ ] Fontes primárias conferidas e matriz de evidências preenchida.
- [ ] Método descreve cronologia exploratória, seleção e diferenças entre configurações.
- [ ] Rascunho contém todas as partes previstas no plano de escrita.
- [ ] Revisão científica verifica números, inferências, citações e limites.
- [ ] Documento final atende ao padrão SBC e à redação adotados, além das regras específicas confirmadas da disciplina.
- [ ] Coesão, coerência, verbos, pessoa narrativa e terminologia conferidos com o guia adotado.
- [ ] Figuras e tabelas do texto coincidem com a versão congelada.
- [ ] Apresentação contém apenas resultados e conclusões sustentados pelo artigo.
- [ ] Ensaio e conferência dos arquivos de entrega concluídos.

Cada conclusão de tarefa deve ser acompanhada do caminho da evidência e da data, no registro de execução futuro. Não marcar como concluída uma tarefa apenas porque o script foi criado ou porque um agente declarou concordância.

## 4. Alternativa caso o esforço ultrapasse a disponibilidade

Manter: rastreabilidade dos resultados, integridade dos pares, regras de limiar, resultados por seed, análise principal, limitações, artigo completo e apresentação. Remover primeiro:

1. Novas medidas de tamanho, novas faixas ou figuras adicionais.
2. Sensibilidade por projeto/commit além da verificação de dependência e de sua limitação explicitada.
3. Intervalos que reamostram também a validação e recalibram os limiares.
4. Ensembles e análises de correlação entre seeds.
5. Testes adicionais de hipótese: se McNemar não sustentar uma alegação central, manter diferenças/intervalos e retirar p-valores históricos sem reprodução.

Reduzir quantidade de tabelas/figuras e extensão da revisão relacionada, preservando a fundamentação necessária. Retirar uma afirmação que dependa de evidência ausente. Não reduzir integridade, esconder divergências nem preencher lacunas com números das notas sem conferência.

Se P0/P1 ainda estiverem bloqueados em 13/10, priorizar recuperação e diagnóstico antes de análises opcionais. Se resultados essenciais não estiverem estáveis em 27/10, rever a disponibilidade e estreitar as afirmações da comparação afetada; novos treinamentos não são a solução padrão para o atraso.

## 5. Coordenação Codex–Claude

O Codex integra arquivos, implementa consolidação quando essa etapa for solicitada e executa verificações. O Claude revisa premissas, estatística, coerência entre resultado e texto e versões concretas. O pesquisador decide escopo, autoria, padrão, interpretação final e entrega. Nenhum agente deve editar o mesmo arquivo simultaneamente.

Para cada revisão, enviar um pacote definido: documento/versão, tabelas ou logs necessários, perguntas específicas e limitações conhecidas. Preservar solicitação, resposta, modelo efetivo, data e decisão tomada em `05_reunioes/consultas_codex_claude/`. Pareceres divergentes devem ser resolvidos pela evidência; concordância não substitui verificação. As consultas ocorrerão durante sessões de trabalho solicitadas, sem monitoramento automático implícito.
