# Parecer original do Claude — não substitui a decisão integrada

Modelo efetivo: claude-opus-5-5.

Sugestões e constatações abaixo devem ser lidas junto com o README deste registro e os documentos finais.

---

# Revisão crítica final dos documentos preliminares

Li os quatro documentos inteiros e conferi três pontos no código e no CSV com Grep. Não executei nada nem modifiquei arquivos.

## (a) Seus seis contrapontos

1. **Aceito.** O `resultados_etapa3.csv` tem 11 linhas não vazias: 10 de dados e o cabeçalho. Eu tinha contado o cabeçalho junto. A redação "os totais registrados não indicam perda de cobertura; a integridade ainda requer auditoria" está correta, porque eu só vi totais, não os pares.

2. **Aceito.** Se os logs concordam entre si, isso só mostra que todos usaram a mesma junção, inclusive se ela estiver errada. Falta um ponto no plano: o que fazer se a release não for recuperada ou se o hash divergir. Hoje isso "bloqueia" a análise sem dar saída. Ver item (b)2.

3. **A escolha é consistente, com uma condição.** O P-C é um evento binário por par, fica fixado antes dos p-valores e ficaria separado do McNemar histórico rotulado. Isso está correto e não deve ser requisito de entrega. A condição: "limiar escolhido no dev" é ambíguo. Existem dois limiares de validação: `limiar_decisao`, o de melhor F1 (`07:171`), e `limiar_vds`, o de FPR ≤ 0,5% (`07:150`). Escolha o de F1 e escreva isso. Registre também dois cuidados:
   - NF4 e BF16 têm limiares calibrados separadamente, então os pares discordantes misturam mudança de nota e mudança de limiar.
   - Com um limiar de F1 numa base de ~4% de prevalência, pode haver poucos casos de P-C e poucos discordantes. O teste terá pouco poder, e isso deve ser dito no texto, não usado como argumento.

4. **Aceito.** "Controle de tamanho" com resultados descritivos é a formulação correta. Retiro também a ideia de antecipar "não observamos diferença".

5. **Aceito.** Eu não tinha verificado que o `08` acrescenta linhas à planilha histórica, então minha sugestão de rodar de novo era imprudente. Recalcular em CPU gravando apenas saídas novas é a solução certa.

6. **Aceito.**

## (b) Correções indispensáveis nos documentos

1. **`CRONOGRAMA_CHECKLIST.md` §1–2 ainda mostra 48h (faixa de 40–65h) em blocos de 10h/semana.** Isso contradiz as duas trilhas que você anunciou. Além disso, as 10h para "escrita do manuscrito completo" e as 4h de leitura não incluem o Huang 2026. Esse artigo precisa entrar explicitamente na leitura obrigatória antes da Introdução, por causa do risco de sobreposição com o achado central.

2. **P1 não tem um critério de pareamento verificável nem uma saída se a release não for recuperada.** Até onde vi no código, o arquivo pareado não traz um ID de par, então "correspondência oficial" precisa virar uma regra concreta. Proposta:
   - posições consecutivas, com mesmo `project` e mesmo `commit_id`;
   - alvos {1,0};
   - mesmo nome ou assinatura de função extraído do código;
   - nenhum membro reutilizado em outro par;
   - regra conferida contra o PDF do PrimeVul.

   Também falta uma data limite (por exemplo, 13/10). Depois dela, o artigo usaria a reconstrução pelos logs, rotulada como preliminar, e a limitação seria declarada.

3. **Falta registrar a troca do critério de seleção de época.** A versão com meio crédito para empates só foi introduzida depois dos resultados. O §3 trata o caráter exploratório de forma genérica. Este caso precisa ser listado pelo nome no Método, junto com a constatação de que a melhor época não mudou. Essa constatação ainda depende de reprodução em P2.

4. **O teto do VD-S do baseline não aparece em nenhum lugar.** Com `limiar_vds = 2048` no corte em 2.048 tokens, o VD-S = 1,000 é um artefato do truncamento. Isso deve entrar em P2/§5 como restrição de leitura obrigatória da tabela central.

5. **O ponto (a)3 precisa ser escrito nos dois documentos.** Em `PLANO_EXECUCAO.md` P3 e no README §6 da consolidação, troque "P-C no limiar escolhido no dev" por "P-C no `limiar_decisao` (F1, validação)". Acrescente a ressalva de que os limiares diferem entre NF4 e BF16.

O resto me parece adequado: `pos`/`i`, a regra de desempate, a não reutilização da tolerância de `formar_pares`, o oráculo separado e o bootstrap por par alinhado.

## (c) Cronograma de 72h/50h

As duas trilhas servem como **ordem de grandeza**, não como medida. As 72h e as 50h são estimativas minhas, sem base na produtividade histórica do pesquisador. Limites:

- A maior variância está em P0/P1, porque recuperar a release é uma dependência externa, e na escrita, porque o padrão editorial ainda não foi definido.
- A trilha essencial de 50h a 10h/semana preenche exatamente as 5 semanas, sem folga. Qualquer bloqueio em P0/P1 vai consumir a margem.
- Recomendo medir as horas reais da primeira semana e replanejar em 13/10. Os pontos de decisão de 13/10 e 27/10 que você já previu são o mecanismo certo para isso.

Nenhuma das trilhas garante o cumprimento do prazo.

**Limites desta revisão:**
- Não li `PLANO_ESCRITA.md` nem `MATRIZ_EVIDENCIAS.md`; você avisou que ainda estão ausentes.
- Não conferi a afirmação do README de que o baseline já grava o F1 calibrado na coluna antiga.
- Não verifiquei no PDF como o PrimeVul define o limiar do VD-S.
