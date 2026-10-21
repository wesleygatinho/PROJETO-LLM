# Material Suplementar

Este material reúne a evidência documental e os detalhes de reprodutibilidade migrados do corpo do artigo. Os arquivos citados estão em `03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08/`, salvo indicação contrária. Nenhum treinamento, inferência, recuperação de pesos ou nova medição em GPU foi realizado na análise retrospectiva; os cálculos usaram exclusivamente os registros históricos e processamento em CPU. Os links abaixo são evidência documental, e não referências científicas do artigo.

## S1. Natureza retrospectiva e materiais

`manifesto.json` identifica as 14 avaliações incluídas e suas receitas e registros: quatro avaliações por instrução (3B e 7B Instruct, cada uma no teste global e no pareado), três configurações 3B, seis avaliações dos três checkpoints 7B (cada um em NF4 e BF16) e a heurística de comprimento. Somam-se 33 arquivos de previsão: 4 de instrução, 27 dos nove classificadores e 2 da heurística. Linhas de depuração, a revisão v0.1 do PrimeVul e execuções descartadas ficaram fora da análise.

Foi usada a distribuição original do PrimeVul, recuperada da pasta pública indicada pelo repositório oficial e guardada em `03_experimentos/dados/artigo_seminarios_2026/release_original`. `recuperacao_dados.json` registra tamanhos, contagens e hashes SHA-256 completos. Esses hashes coincidiram com os prefixos históricos de 12 caracteres disponíveis para treino, teste global e teste pareado. A coincidência reforça a identidade dos dados, mas não significa que hashes completos tenham sido registrados nas execuções originais.

No artigo, o acesso prévio ao teste é declarado nas Seções 1, 3.1 e 6.

## S2. Alinhamento das previsões

Cada registro de previsão foi alinhado à partição oficial por posição original, identificador `idx`, projeto, commit e rótulo (`auditoria_integridade.json`, `divergencias.json`). O campo `i` dos registros de instrução indica a ordem de processamento e não foi usado como identidade. O campo `func_hash` nulo não foi usado como prova de identidade. Houve cobertura integral, posições únicas e nenhuma divergência nos campos conferidos, e nenhum CSV ou registro histórico foi alterado.

Os pares foram reconstruídos pela ordem da distribuição oficial, exigindo duas posições consecutivas, classes opostas e projeto/commit coincidentes. O teste pareado tem 1.128 posições e 1.126 identidades `idx` distintas, porque duas funções corrigidas são reutilizadas em pares diferentes; na validação pareada, uma identidade aparece em cinco pares (`reutilizacoes_release_oficial.json`). As reutilizações foram preservadas por posição, sem junções que multiplicassem ou descartassem linhas, e os denominadores oficiais foram mantidos.

## S3. Inspeção da correspondência dos pares

`pares_inspecao.json` registra os 15 pares de teste cujas versões diferem no cabeçalho ou na assinatura. Diferenças de assinatura ou renomeação não bastam, isoladamente, para declarar uma correspondência incorreta, e dez desses casos não foram excluídos. Nos cinco casos abaixo, os arquivos do commit e de seu pai confirmaram que o membro rotulado como corrigido já existia antes da correção e corresponde a outra função (`inspecao_correspondencia_commits.json`; cópias em `03_experimentos/dados/artigo_seminarios_2026/commits_inspecao`). As posições são baseadas em zero.

| Projeto | Posições no teste pareado | Função vulnerável | Membro rotulado como corrigido | Commit | Ano |
| --- | --- | --- | --- | --- | --- |
| libjpeg | 348/349 | PrepareForDecoding | PrepareForEncoding | 187035b9726710b4fe11d565c7808975c930895d | 2022 |
| PHP | 750/751 | openssl_encrypt | openssl_decrypt | 095cbc48a8f0090f3b0abc6155f2b61943c9eafb | 2011 |
| rizin | 784/785 | relocs | maps | 58926dffbe819fe9ebf5062f7130e026351cae01 | 2022 |
| Linux | 1056/1057 | sctp_sf_violation_paramlen | sctp_sf_violation_chunklen | ba0166708ef4da7eeb61dd92bbba4d5a749d6561 | 2008 |
| drogon | 280/281 | save | saveAs | 3c785326c63a34aa1799a639ae185bc9453cb447 | 2022 |

Fontes documentais:

- libjpeg: https://github.com/thorfdbg/libjpeg/commit/187035b9726710b4fe11d565c7808975c930895d
- PHP: https://github.com/php/php-src/commit/095cbc48a8f0090f3b0abc6155f2b61943c9eafb
- rizin: https://github.com/rizinorg/rizin/commit/58926dffbe819fe9ebf5062f7130e026351cae01
- Linux: https://github.com/torvalds/linux/commit/ba0166708ef4da7eeb61dd92bbba4d5a749d6561
- drogon: https://github.com/drogonframework/drogon/commit/3c785326c63a34aa1799a639ae185bc9453cb447

A comparação textual normalizou espaços para localizar as funções, e o julgamento considerou também o diff. A presença prévia de uma função, sozinha, não provaria que ela não foi alterada. Os 564 pares permanecem na análise principal; o recorte de 559 está em `sensibilidade_correspondencia.csv`, e sua interseção com os pares sem truncamento tem 460. Nenhum membro foi substituído por funções sem previsões históricas.

## S4. Classificação por instrução

As rodadas usaram Qwen2.5-Coder-3B-Instruct e 7B-Instruct em FP16, instrução sem exemplos pedindo YES ou NO, decodificação determinística e até cinco novos tokens. O limite de 8.192 tokens para o código consta dos registros históricos dessas rodadas; a análise retrospectiva não reconstruiu a chamada de linha de comando. O analisador aceita a primeira palavra de decisão reconhecida e, quando necessário, termos de decisão nos primeiros 60 caracteres; respostas indefinidas recebem rótulo não vulnerável e são contadas. Nenhuma resposta indefinida ocorreu nos quatro registros. O texto integral da instrução e o analisador estão no código histórico identificado em `manifesto.json`. Os tempos de geração, obtidos sequencialmente e em outro contexto, não foram comparados aos dos classificadores.

## S5. Configurações de ajuste e custo das rodadas

Correspondência entre os rótulos do artigo e os da tabela congelada (`tabelas_artigo.md`): 3B 1:1 = 3B 1:1; 3B proporção original = 3B real; 3B 1:1 + tamanho = 3B 1:1 tamanho; 7B 1:1 + tamanho, semente n = 7B 1:1 tamanho sn; heurística de comprimento = Tamanho.

Coluna migrada da Tabela 2 do artigo. O custo inclui o tempo total registrado da rodada, ao preço histórico de US$ 0,50/h, e não corresponde a faturamento.

Tabela S2. Custo total registrado por rodada de ajuste.

| Configuração | Treino (h) | Custo total (US$) |
| --- | --- | --- |
| 3B 1:1 | 3,37 | 1,85 |
| 3B proporção original | 10,16 | 5,14 |
| 3B 1:1 + tamanho | 4,98 | 2,65 |
| 7B 1:1 + tamanho, semente 1 | 7,89 | 4,21 |
| 7B 1:1 + tamanho, semente 2 | 7,89 | 4,21 |
| 7B 1:1 + tamanho, semente 3 | 7,91 | 4,23 |

As configurações 3B usaram a semente 1. Hiperparâmetros: base NF4 com dupla quantização, computação BF16, cabeça em precisão plena e treinável; LoRA em q, k, v, o, gate, up e down, com r = 16, α = 32 e dropout de 0,05; AdamW convencional, taxa de 2 × 10⁻⁴, sem decaimento de pesos, aquecimento de 3% e decaimento linear; lote efetivo de 16 funções com divisão por orçamento de tokens; checkpointing de gradientes; corte da norma em 1,0; entropia cruzada sem peso de classe. Os demais argumentos estão nas receitas indicadas em `manifesto.json`.

## S6. Seleção de época

`selecao_epocas.json` registra, por época, a ordenação estrita nos pares de validação (empates contados como erro), a AUC na amostra da validação global (699 vulneráveis e 2.796 não vulneráveis) e, quando disponível, o número de empates. A AUC serviu de critério de desempate. Exemplo: na configuração 3B 1:1, a época 1 teve ordenação estrita de 38,43% e AUC de 0,7554, e a época 2 teve 31,85% e 0,8116; a época 1 foi selecionada. Essa amostra não é a validação global completa usada nos limiares.

Após a adoção do meio crédito para empates, a seleção foi reconstruída nos quatro treinos com controle de tamanho (3B e as três sementes 7B), cujos registros incluem empates por época, e a época escolhida permaneceu a mesma. Nas configurações 3B 1:1 e de proporção original, os empates por época não foram registrados (campo `empates` nulo); os checkpoints históricos foram mantidos, sem afirmar que o critério ajustado escolheria a mesma época.

## S7. Detalhes de implementação dos limiares

Limiar de maior F1: os escores da validação global foram ordenados e os cortes foram avaliados entre valores distintos, incluindo o grupo empatado acima do corte; em empate de F1 máximo, a implementação escolhe o primeiro corte encontrado em ordem decrescente. Numericamente, o limiar é o valor representável imediatamente inferior ao último escore incluído.

Limiar de FPR ≤ 0,5%: o limiar é o escore da função não vulnerável que delimita o número máximo de alarmes, dado pelo piso de 0,005 vezes o número de não vulneráveis da validação; a regra estrita exclui escores empatados nesse valor. No caso da heurística, o limiar coincidiu com o teto de 2.048 tokens.

Os escores históricos foram gravados com cinco casas decimais. A reconstrução usou essa precisão, sem criar casas ausentes ou ajustar tolerâncias, e os limiares derivados foram guardados sem novo arredondamento. Contagens globais, categorias no limiar histórico, AUC, F1 calibrado e FNR/FPR reproduziram os registros na precisão publicada, o que não garante a recuperação da precisão interna de todas as operações. A implementação oficial do VD-Score escolhe um ponto da curva ROC no conjunto fornecido com regra inclusiva; o procedimento local separa calibração e teste e usa s > t. Valores históricos com limiar escolhido no teste não foram usados.

As categorias pareadas no limiar histórico zero dos classificadores estão em `metricas_pareadas.csv`. Nesse limiar, as 564 decisões da configuração 3B de proporção original foram P-B.

## S8. Estatística

O bootstrap (`estatistica.json`, `intervalos.csv`, `comparacoes.csv`) usou 10.000 réplicas e a semente 20261008. Em cada réplica, os 550 grupos projeto/commit foram sorteados com reposição, mantendo todos os pares de cada grupo e os mesmos índices para todas as configurações e sementes. Cada réplica estima a média ponderada pelos pares efetivamente reamostrados, preservando o vetor das três sementes; a média não é um ensemble nem uma amostra triplicada. Foram calculados intervalos por modelo, para a média das sementes e para as diferenças NF4 − BF16 dentro de cada semente e na média. A comparação dos limites entre 5.000 e 10.000 réplicas variou no máximo 0,10 ponto percentual por modelo. Uma reamostragem por par foi preservada como sensibilidade. Não foram transportados p-valores das notas históricas nem realizados testes de hipótese.

## S9. Sensibilidades

Tabela S1. Ordenação no conjunto oficial (564), sem as cinco correspondências incompatíveis (559) e, entre esses, sem truncamento (460). Recortes retrospectivos que não certificam a correção dos pares restantes.

| Configuração | Ord. 564 (%) | Ord. 559 (%) | Ord. 460 (%) |
| --- | --- | --- | --- |
| Heurística de comprimento | 21,10 | 20,57 | 14,46 |
| 3B 1:1 | 42,38 | 42,40 | 39,02 |
| 3B proporção original | 37,50 | 37,30 | 33,80 |
| 3B 1:1 + tamanho | 49,20 | 49,02 | 48,48 |
| 7B NF4 s1 | 55,23 | 55,19 | 54,02 |
| 7B BF16 s1 | 53,28 | 53,22 | 51,85 |
| 7B NF4 s2 | 45,04 | 45,26 | 42,61 |
| 7B BF16 s2 | 44,68 | 44,90 | 42,17 |
| 7B NF4 s3 | 51,60 | 51,52 | 51,52 |
| 7B BF16 s3 | 51,95 | 51,88 | 51,96 |

A comparação das sequências tokenizadas encontrou 32 pares com entradas idênticas após o corte em 2.048 tokens (`tokenizacao_proveniencia.json`, campo `pares_tokens_identicos_2048`). Os arquivos `sensibilidade_truncamento.csv` e `sensibilidade_correspondencia.csv` contêm os valores por configuração.

## S10. Proveniência do tokenizador

A revisão do tokenizador não foi registrada separadamente para a heurística. Foi recuperado o artefato da revisão do modelo 3B registrada nos classificadores, e todos os comprimentos do teste e dos pares coincidiram com os registros. Os arquivos `tokenizer.json` das revisões recuperadas de 3B e 7B são idênticos. A validação da heurística foi recontada em CPU, e seus valores de calibração e teste reproduziram os números registrados (`tokenizacao_proveniencia.json`). A rastreabilidade histórica registra prefixos de revisões e hashes, sem revisão de código identificada por execução em todas as rodadas.

## S11. Ambiente e recursos

Execuções originais em NVIDIA A40, com PyTorch 2.8.0+cu128, CUDA 12.8, Transformers 5.17.0, tokenizers 0.23.2, PEFT 0.21.0 e bitsandbytes 0.50.2, conforme os registros. A memória após a carga é a memória CUDA alocada, em GB decimais, e não a memória reservada ou a capacidade da GPU. O pico foi reiniciado após a carga e a mesclagem e observado na janela de validação, teste e pares; pode não incluir o pico transitório da mesclagem. O tempo por função é o tempo de pontuação do teste dividido pelo número de funções, em lotes de até 32.768 tokens incluindo preenchimento. O custo estimado usa esse tempo e o preço histórico de US$ 0,50/h. As reduções de cerca de 67% (após carga) e 40% (pico) citadas no artigo correspondem às razões entre os valores da Tabela 7.

## S12. Reprodução local

Os scripts da análise retrospectiva estão em `03_experimentos/codigo/consolidacao_artigo`; os módulos 01 a 04 inventariam, consolidam, calculam a estatística e exportam tabelas e figura, e `tests_cientificos.py` verifica métricas e rejeita alinhamentos incorretos. Para repetir a análise, recomenda-se um novo destino de resultados, preservando os produtos congelados. As diferenças de hash entre versões do exportador e do recuperador de tokenizador estão explicitadas em `proveniencia_exports.json` e em `04_escrita/artigo/seminarios_2026/revisao/artigo_completo_2026-10-08/auditoria_final.json`; elas não alteram fórmulas ou resultados. O suplemento anterior (`04_escrita/artigo/seminarios_2026/revisao/artigo_completo_2026-10-08/SUPLEMENTO.md`) permanece como registro da rodada editorial anterior.
