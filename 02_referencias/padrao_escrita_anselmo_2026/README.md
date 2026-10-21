# Referências do padrão de escrita

Origem solicitada pelo pesquisador: `D:\UFMA UNIVERSIDADE\MESTRADO - PLN\trabalho final\artigos anselmo`. Foram extraídos os **12 PDFs, totalizando 133 páginas**. Os PDFs originais não foram alterados nem duplicados neste projeto.

- [Análise e evidências do corpus](ANALISE_CORPUS.md).
- `inventario_fontes.json`: paths originais, hashes completos, páginas, fontes tipográficas detectadas e primeira página extraída.
- `textos_extraidos/A01.txt` a `A12.txt`: extrações completas com marcadores de página física do PDF.
- `textos_extraidos/A12_colunas.txt`: extração auxiliar por coluna para o artigo de duas colunas.
- `textos_extraidos/SBC_PDF.txt`: extração do documento genérico de instruções do template indicado.
- [Guia adotado para o manuscrito](../../04_escrita/artigo/seminarios_2026/PADRAO_ESCRITA.md).

Extração feita com pdfplumber, sem OCR adicional. Há ligaturas/acentos separados, espaços ausentes, hifenização e interferência de figuras/equações. A12 na extração linear intercala colunas; a extração auxiliar melhora a ordem, mas também requer conferência do PDF. Esses fenômenos não são padrões linguísticos do autor.

O campo `words` do inventário é uma contagem mecânica aproximada de tokens por expressão regular, afetada pelos espaços ausentes: não serve para medir extensão linguística, comparar densidade textual ou definir tamanho de parágrafo. Não foi feita análise estilométrica de autoria.

O Codex conferiu visualmente as primeiras páginas dos 12 artigos, páginas internas de A01/A08/A12 e a primeira página do template. O Claude informou leitura integral das extrações dos 12 artigos; não abriu os PDFs originais. A comparação usa textos com coautoria e variação de veículo, não uma identificação da voz individual de uma pessoa.

Referências de estilo não se tornam automaticamente referências científicas do artigo sobre vulnerabilidades. Apenas uma fonte pertinente ao problema poderá entrar na bibliografia científica, após leitura e justificativa próprias.
