# Suplemento do artigo de Seminários

Este suplemento acompanha a consolidação retrospectiva do bloco Qwen2.5-Coder/PrimeVul. Os arquivos derivados ficam em `03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08`. As receitas, logs e CSVs anteriores foram preservados; os novos arquivos não substituem os resultados históricos. Nenhum treinamento, inferência em modelo, recuperação de pesos ou acesso ao RunPod foi realizado.

## Dados e identidade

A release original foi recuperada da pasta pública indicada pelo repositório oficial, sem utilizar a release v0.1. Os seis JSONL estão em `03_experimentos/dados/artigo_seminarios_2026/release_original`. `recuperacao_dados.json` registra URLs, tamanhos, contagens e hashes completos atuais. A concordância com os prefixos históricos disponíveis está documentada na auditoria; não se afirma que esses hashes completos tenham sido registrados nas execuções passadas.

`manifesto.json` identifica 14 avaliações e os respectivos arquivos e receitas. `auditoria_integridade.json` e `divergencias.json` documentam a conferência de alinhamento. Os quatro logs de prompting, os 27 logs dos nove classificadores e os dois logs da referência de tamanho totalizam 33 arquivos de previsão. O identificador `i` do prompting é ordem de processamento; a identidade usa posição na fonte, idx, projeto, commit e rótulo. Reutilizações oficiais são preservadas por posição, sem junções silenciosas que multipliquem ou descartem linhas.

## Correspondência pareada

`pares_inspecao.json` registra os 15 pares de teste com diferença de cabeçalho. Diferenças de assinatura ou renomeação não bastam, isoladamente, para declarar uma correspondência incorreta. A inspeção dos diffs foi focalizada; dez desses casos não foram excluídos por esse critério. Não se certificou a validade semântica dos demais pares.

Nos cinco casos excluídos apenas na análise de sensibilidade, os arquivos do commit e de seu pai confirmam que o membro benigno já existia antes da correção e corresponde a outra função:

| Projeto | Posições no teste pareado | Função vulnerável | Membro rotulado como corrigido |
| --- | --- | --- | --- |
| libjpeg | 348/349 | PrepareForDecoding | PrepareForEncoding |
| PHP | 750/751 | openssl_encrypt | openssl_decrypt |
| rizin | 784/785 | relocs | maps |
| Linux | 1056/1057 | sctp_sf_violation_paramlen | sctp_sf_violation_chunklen |
| drogon | 280/281 | save | saveAs |

As posições são baseadas em zero. `inspecao_correspondencia_commits.json` registra URLs, hashes e identificadores. As cópias primárias, incluindo os arquivos do pai, ficam em `03_experimentos/dados/artigo_seminarios_2026/commits_inspecao`. As fontes são os commits públicos dos projetos, citados no artigo. A comparação textual normaliza espaços para localizar as funções; o julgamento de correspondência também considera o diff. A presença prévia de uma função, sozinha, não provaria que ela não foi alterada.

Os 564 pares oficiais permanecem na análise principal. `sensibilidade_correspondencia.csv` apresenta o recorte de 559, e sua interseção com os pares sem truncamento contém 460. Não se substituíram membros por funções que não possuem previsões históricas.

## Métricas, incerteza e recursos

`metricas_por_execucao.csv`, `metricas_pareadas.csv` e `sensibilidade_truncamento.csv` separam calibração na validação, categorias no limiar histórico, ordenação com meio crédito para empates e subconjunto sem truncamento. Scores disponíveis têm cinco casas decimais; a reconstrução não recupera precisão interna ausente. O ponto de FNR usa restrição de FPR na validação, não garante essa restrição no teste e não é apresentado como reprodução do VD-Score oficial.

`estatistica.json`, `intervalos.csv` e `comparacoes.csv` contêm bootstrap percentil de 10.000 réplicas, seed 20261008, por 550 grupos projeto/commit. O alinhamento entre configurações e seeds é mantido em cada réplica. Os intervalos são condicionais aos modelos existentes. Não constituem incerteza de futuros treinos nem teste de equivalência. A hipótese de independência dos commits pode falhar entre commits do mesmo projeto.

As tabelas exportadas e a figura `figuras/ordenacao_7b.png`/`.svg` são artefatos derivados. A figura foi inspecionada visualmente. As unidades e janelas de recursos seguem os registros: memória CUDA alocada, pico após reinicialização, tempo amortizado em lotes e custo estimado pelo preço histórico. Não são medições de energia, faturamento ou latência individual.

## Reprodução local em CPU

Os scripts novos ficam em `03_experimentos/codigo/consolidacao_artigo`. Os módulos 01 a 04 inventariam, consolidam, calculam a estatística e exportam tabelas/figura. `tests_cientificos.py` verifica métricas e rejeições de alinhamentos incorretos; oito testes passaram. As dependências de tokenização e plotagem ficam isoladas em `.runtime_artigo_2026`. Os scripts de recuperação acessam apenas artefatos públicos; não recuperam pesos.

Para repetir a consolidação, usar um novo destino de resultados na mesma raiz do projeto com `--destino`, mantendo os produtos congelados desta revisão. Não executar scripts históricos de treinamento ou avaliação de modelos. O exportador recebeu uma mudança posterior à exportação para fixar `MPLCONFIGDIR` na pasta local; o hash do código em `proveniencia_exports.json` corresponde à versão anterior a essa mudança de cache. O recuperador de tokenizer também recebeu a inclusão posterior dos artefatos 7B e da verificação de igualdade com 3B, com proveniência própria. O código congelado na rodada editorial contém essas mudanças. Elas não alteram fórmulas ou resultados, mas as diferenças de hash são explicitadas em `auditoria_final.json` e não apagadas retrospectivamente.

## Redação e revisão

Versões, prompts, respostas brutas e pareceres estão em `revisao/fluxo_editorial/rodadas/artigo_completo_01` e `artigo_completo_02`. A conferência primária adicional e a resposta P1 ficam neste diretório de revisão. O contrato utiliza Codex como redator/corretor e uma sessão nova do Claude para cada revisão. Uma aprovação textual não comprova compilação ou inspeção de PDF. Identificação de autores, afiliação completa, regras de extensão e decisão acadêmica final pertencem ao pesquisador.
