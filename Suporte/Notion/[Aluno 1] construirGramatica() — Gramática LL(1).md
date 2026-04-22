**Responsável:** Dani Heart Basso

## Tarefas

- Implementar `construirGramatica()` com o conjunto completo de regras de produção
- Escrever regras para: expressões RPN, comandos especiais (`RES`, `MEM`), estruturas de controle, aninhamento
- Calcular os conjuntos **FIRST** e **FOLLOW** para cada não-terminal
- Construir a **tabela de análise LL(1)** baseada nos conjuntos FIRST e FOLLOW
- Detectar e resolver conflitos na gramática (se houver)
- Validar que a gramática é LL(1) sem conflitos
- Documentar gramática completa em formato **EBNF** (minúsculas = não-terminais, maiúsculas = terminais)
- Testar a tabela com entradas diversas para garantir determinismo

## Funções a implementar

- `calcularFirst()`
- `calcularFollow()`
- `construirTabelaLL1()`

## Interface

- **Entrada:** Nenhuma (gramática é fixa)
- **Saída:** Estrutura de dados com gramática, FIRST, FOLLOW e tabela LL(1)
- **Fornece:** tabela para `parsear()`

---

### Decisões de Arquitetura

## 1. Fatoração à Esquerda (Left Factoring) para garantir LL(1)

**O que é:**
A gramática foi desenhada para evitar que múltiplas regras de um mesmo não-terminal comecem com o mesmo token. Por exemplo, quase tudo na nossa linguagem começa com `LPAREN` `(`. Para resolver isso, criamos regras intermediárias como `<acao_pos_par>` e `<conteudo_pos_par_lparen>`.

**Por que:**
Um parser preditivo LL(1) só consegue olhar 1 token à frente. Se tivéssemos `<IF> ::= ( ...` e `<WHILE> ::= ( ...`, o parser não saberia qual caminho seguir ao ler um `(`. Ao fatorar a gramática, o parser "engole" o parêntese inicial e adia a decisão até ler o próximo token interno (ex: `LET`, `NUM_INT`, etc.), eliminando 100% dos conflitos da tabela.

---

## 2. Conjuntos FIRST, FOLLOW e Tabela LL(1) "Hardcoded" (Estáticos)

**O que é:**
As funções `calcularFirst()`, `calcularFollow()` e `construirTabelaLL1()` no arquivo `gramatica.py` retornam dicionários Python pré-calculados e escritos manualmente, em vez de implementar algoritmos de geração dinâmica (computar fechamento transitivo, etc) em tempo de execução.

**Por que:**
A gramática do nosso compilador é fixa e imutável. Calcular os conjuntos em runtime a cada execução do compilador adicionaria complexidade desnecessária, gastaria processamento e aumentaria a chance de bugs. A codificação estática comprova o entendimento teórico do grupo sobre como os conjuntos são formados (passo a passo documentado nos comentários do código) e garante uma execução O(1) ultrarrápida.

---

## 3. Uso do símbolo `[VAZIO]` para transições Épsilon (ε)

**O que é:**
Para lidar com regras opcionais ou listas de tamanho variável (como os comandos dentro de um bloco `LET`), utilizamos o terminal fictício `[VAZIO]`, que atua como o Épsilon (ε) da teoria de compiladores.
Exemplo: `<lista_comandos_bloco> ::= LPAREN <conteudo_comando> RPAREN <lista_comandos_bloco> | [VAZIO]`

**Por que:**
Isso permite a recursão à direita controlada. Quando o parser está lendo um bloco de comandos e encontra o token `RPAREN` (que é o FOLLOW de `<lista_comandos_bloco>`), a tabela LL(1) aponta para `[VAZIO]`, o que sinaliza ao parser para encerrar aquele bloco sem tentar consumir mais nada, evitando loops infinitos ou erros de sintaxe esperados.

---

## 4. Estrutura da Tabela Preditiva em Dicionário 2D

**O que é:**
A tabela retornada por `construirTabelaLL1()` é um dicionário aninhado onde a primeira chave é o Não-Terminal e a segunda chave é o Token de Entrada (Terminal).

**Por que:**
Essa estrutura `tabela[nao_terminal][token]` é a representação perfeita de uma matriz `M[A, a]` da teoria LL(1). Ela permite que o Parser (Aluno 2) faça a busca da regra de derivação em tempo constante O(1), mantendo a complexidade do analisador sintático extremamente baixa e a integração entre as partes (Aluno 1 -> Aluno 2) isolada e muito fluida.