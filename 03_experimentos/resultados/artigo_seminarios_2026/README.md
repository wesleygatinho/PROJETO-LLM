# Saídas derivadas do artigo de Seminários

**Estado: reservado para saídas futuras.** Nenhuma tabela ou estatística nova foi produzida pela criação do plano.

Fontes históricas continuam no diretório pai e em `03_experimentos/logs/`. Não copiar esses arquivos para cá nem sobrescrevê-los. Os scripts planejados em `03_experimentos/codigo/consolidacao_artigo/` produzirão:

- `manifesto.json`, `inventario.csv` e `fontes_ausentes.md`;
- `auditoria_integridade.json`, `pares_auditados.csv` e `divergencias.csv`;
- `metricas_por_execucao.csv` e `sensibilidade_truncamento.csv`;
- `estatistica.json`, `intervalos.csv` e `comparacoes.csv`;
- `tabelas/`: CSVs canônicos das tabelas do artigo;
- `proveniencia_exports.json`: versão das entradas, scripts, parâmetros e exports.

Detalhes de cada saída estão na [especificação](../../codigo/consolidacao_artigo/README.md). Dados por função adicionais, se necessários, devem ter política explícita de armazenamento/tamanho; não duplicar centenas de milhares de linhas sem necessidade.

Toda saída deve distinguir resultado validado, incompleto e excluído. O diretório do manuscrito poderá referenciar estas tabelas canônicas e receber exports no formato editorial escolhido; não manter duas versões manuais independentes dos mesmos números.

Figuras finais pertencem a `04_escrita/artigo/seminarios_2026/figuras/`. Inputs científicos e relatórios de cálculo pertencem aqui. A versão congelada será identificada por manifesto e revisão, sem nome genérico que esconda alterações posteriores.
