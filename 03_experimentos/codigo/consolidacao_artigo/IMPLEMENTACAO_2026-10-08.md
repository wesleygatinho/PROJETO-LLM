# Consolidação implementada em 08/10/2026

O README anterior é a especificação histórica e foi preservado. A implementação atual contém `comum.py`, `01_inventariar.py`, `02_consolidar_metricas.py`, `03_estatistica.py`, `04_exportar_artigo.py`, `tests_cientificos.py` e auxiliares para recuperar dados públicos/tokenizers e inspecionar commits. Não houve treinamento, inferência, recuperação de pesos ou uso do RunPod.

As saídas novas estão em `03_experimentos/resultados/artigo_seminarios_2026/consolidacao_2026-10-08`. Dados e fontes públicas recuperados ficam em `03_experimentos/dados/artigo_seminarios_2026`. Dependências CPU isoladas em `.runtime_artigo_2026`: NumPy 2.5.3, tokenizers 0.23.2, Matplotlib 3.11.2. O runtime Python usado é 3.12.14.

O bloco inclui 14 avaliações, 33 arquivos de previsão e seis receitas oficiais de treinamento preexistentes. Cobertura e identidade foram conferidas contra a release original. Os resultados principais reproduziram a precisão publicada, sem divergências. As categorias recalibradas e a estatística são análises derivadas dos scores registrados, cuja precisão interna não é recuperável.

O bootstrap implementado utiliza 10.000 réplicas alinhadas, seed 20261008, com reamostragem primária por projeto/commit e sensibilidade por par. Não foram feitos testes adicionais de hipótese; o McNemar da especificação ficou fora do artigo. Três seeds não permitem caracterizar robustamente futuros treinamentos.

As sensibilidades distinguem os 465 pares sem truncamento, os 559 sem cinco correspondências inadequadas documentadas e sua interseção de 460. Os 564 pares oficiais permanecem na análise principal. Os cinco casos foram confrontados com arquivos públicos do commit e do pai; a auditoria não certifica todos os rótulos.

Para repetir 01–04 em CPU, utilizar o Python com acesso às dependências locais e `--destino` apontando a uma pasta nova dentro do projeto, na ordem 01, 02, 03, 04. Os scripts atuais utilizam a raiz do projeto determinada a partir do arquivo; não se garante portabilidade do argumento `--raiz` para todas as etapas. Não repetir sobre o destino congelado da revisão. Os oito testes científicos passaram. Não executar scripts históricos de treinamento/avaliação como parte desta reprodução.

O suplemento editorial em `04_escrita/artigo/seminarios_2026/revisao/artigo_completo_2026-10-08/SUPLEMENTO.md` registra fontes, limites, proveniência e duas diferenças de hashes de scripts auxiliares ocorridas após a exportação e antes do congelamento editorial. Os dados e tabelas exportados permaneceram inalterados.
