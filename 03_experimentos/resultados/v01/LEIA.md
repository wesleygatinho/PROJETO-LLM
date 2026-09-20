# Resultados feitos na release v0.1 do PrimeVul (arquivados em 19/set/2026)

Tudo nesta pasta — e os logs em `../../logs/v01/` — foi calculado na **PrimeVul-v0.1**, e **não** entra
nas tabelas da dissertação. Nada aqui está errado; é outro conjunto de dados.

## O que aconteceu

Até 19/set/2026 os dados vinham do espelho `colin/PrimeVul` no Hugging Face, que é a release **v0.1**
(set/2024). O README oficial do PrimeVul descreve essa release assim:

> "In PrimeVul-v0.1, we only include vulnerabilities that we successfully retrieved their metadata.
> For the full set of samples that we originally used in the paper, please refer to the original release."

Ou seja, a v0.1 acrescenta metadados (CVE, commit, arquivo) e, em troca, **descarta** as vulnerabilidades
cujos metadados os autores não conseguiram recuperar. Ela é um subconjunto da release do artigo:

| | Release do artigo (Tabela III) | v0.1 | Diferença |
|---|---|---|---|
| Teste | 25.911 (695 vulneráveis) | 24.788 (549) | −21% das vulneráveis |
| Teste pareado | 564 pares | 435 pares | −23% dos pares |
| Validação | 25.430 (699) | 23.948 (593) | −15% |
| Validação pareada | 562 pares | 480 pares | −15% |
| Treino | 184.427 (5.574) | 175.797 (4.862) | −13% |

Por que trocamos: (1) os números do artigo e da literatura são da release original, então só nela dá para
comparar; (2) o descarte não é aleatório — sobram as vulnerabilidades com CVE/CWE recuperável; (3) os nossos
scripts leem apenas `func` e `target`, então os metadados da v0.1 não nos servem para nada. Ficar na v0.1
seria pagar o viés sem receber o benefício.

## O que está guardado aqui

| Arquivo | Conteúdo |
|---|---|
| `resultados_etapa1.csv` | Etapa 1 (prompting YES/NO), 3B e 7B, 16 bits |
| `resultados_pareado.csv` | P-C/P-V/P-B/P-R das rodadas da Etapa 1 |
| `treinos_etapa3.csv` | o treino de depuração do QLoRA (400 funções) |
| `resultados_etapa3.csv` | a avaliação desse adaptador de depuração |
| `../../logs/v01/*.jsonl` | as respostas e notas função a função de todas essas rodadas |

## O que continua valendo destas rodadas

Os **números** não, mas as **conclusões de método** sim, e elas estão em `../NOTAS_etapa1.md`:

- zero-shot fica no nível do acaso, e o modelo maior só multiplica alarmes falsos;
- a mesma rodada em GPUs diferentes muda ~1% das respostas (por isso toda comparação é na mesma placa);
- mesma placa + versões travadas reproduzem o resultado exatamente;
- no PrimeVul, o tamanho da função sozinho dá AUC 0,82 no teste e desmorona no pareado.

Essas rodadas também podem voltar como **conferência de robustez** ("os achados se repetem na v0.1?"),
já que o código aceita as duas releases (`00_baixar_primevul.py --release v01`).

## Como não misturar de novo

Desde 19/set/2026 cada linha das planilhas traz a coluna `release_dados` (`original`, `v01` ou
`desconhecida`, deduzida do tamanho do arquivo), e o `00_baixar_primevul.py` para com erro se o que está
em `../dados/` não for a release pedida.
