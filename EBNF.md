# Gramática e Análise Sintática - Fase 2 (RPN)

## 1. O Alfabeto da Linguagem (Terminais)

Este é o conjunto de tokens gerados pelo Analisador Léxico (Fase 1) que o nosso Parser consome:
- **Estrutura:** `LPAREN` `(`, `RPAREN` `)`, `START`, `END`
- **Tipos e Memória:** `NUM_INT`, `NUM_REAL`, `MEM` (Variáveis em maiúsculo)
- **Comandos e Controle:** `KEYWORD_RES`, `LET`, `IF`, `WHILE`
- **Matemática:** `OP_SOMA` `+`, `OP_SUB` `-`, `OP_MULT` `*`, `OP_DIV_REAL` `|`, `OP_DIV_INT` `/`, `OP_MOD` `%`, `OP_POT` `^`
- **Lógica:** `OP_MAIOR`, `OP_MENOR`, `OP_IGUAL`, `OP_DIF`, `OP_MAIOR_IGUAL`, `OP_MENOR_IGUAL`

## 2. Metodologia: Fatoração à Esquerda

Para que o nosso parser preditivo LL(1) funcione sem "voltar atrás" (*backtracking*), aplicamos a **fatoração à esquerda**.
Como a linguagem exige parênteses ao redor de tudo, o parser não sabe qual regra escolher só de ver um `(`. Para resolver isso, fazemos a regra consumir o `LPAREN` inicial e delegamos a decisão para o conteúdo interno. Ele espia o *próximo* token e decide o caminho correto, eliminando a ambiguidade.

---

## 3. Regras de Produção EBNF

> **Nota sobre o formato:** Utilizamos `[VAZIO]` no lugar do tradicional `ε` (épsilon) para representar produções vazias (onde o escopo se encerra sem consumir novos tokens).

```ebnf
<programa> ::= LPAREN START RPAREN <lista_comandos_globais>

<lista_comandos_globais> ::= LPAREN <conteudo_global>

<conteudo_global> ::= END RPAREN
                   | <conteudo_comando> RPAREN <lista_comandos_globais>

<lista_comandos_bloco> ::= LPAREN <conteudo_comando> RPAREN <lista_comandos_bloco> 
                       | [VAZIO]

<conteudo_comando> ::= NUM_INT <acao_numero>
                    | NUM_REAL <acao_numero>
                    | MEM                            # Ler Memória: (EULER)
                    | LPAREN <conteudo_par> RPAREN <acao_pos_par>

<acao_numero> ::= KEYWORD_RES                                    # Ex: (10 KEYWORD_RES)
               | MEM                                 # Ex: (10 EULER)
               | <operando> <operador>                  # Ex: (10 20 +)

<conteudo_par> ::= <expressao>                           # Pode ser conta ou condição (A B >)

<acao_pos_par> ::= NUM_INT <operador>                     # Era uma conta aninhada
               | NUM_REAL <operador>                    # Era uma conta aninhada
               | LPAREN <conteudo_pos_par_lparen>          # Conta ou Bloco de Controle

<conteudo_pos_par_lparen> ::= LET <lista_comandos_bloco> RPAREN <controle>
                         | <conteudo_operando> RPAREN <operador>

<controle> ::= IF | WHILE

<expressao> ::= <operando> <operando> <operador>

<operando> ::= NUM_INT
             | NUM_REAL
             | LPAREN <conteudo_operando> RPAREN

<conteudo_operando> ::= MEM                           # Memória no meio da conta
                     | <expressao>                      # Conta dentro da conta

<operador> ::= OP_SOMA | OP_SUB | OP_MULT | OP_DIV_INT | OP_DIV_REAL | OP_MOD | OP_POT
             | OP_MAIOR | OP_MENOR | OP_IGUAL | OP_DIF | OP_MAIOR_IGUAL | OP_MENOR_IGUAL
```

---

## 4. Conjuntos FIRST

* **`FIRST(<programa>)`** = `{ LPAREN }` -> Inicia obrigatoriamente com o '(' do (START)
* **`FIRST(<lista_comandos_globais>)`** = `{ LPAREN }` -> Laço principal do programa
* **`FIRST(<conteudo_global>)`** = `{ END, NUM_INT, NUM_REAL, MEM, LPAREN }` -> Trata o encerramento ou conteúdo
* **`FIRST(<lista_comandos_bloco>)`** = `{ LPAREN, [VAZIO] }` -> Pode iniciar um novo comando ou ser vazio
* **`FIRST(<conteudo_comando>)`** = `{ NUM_INT, NUM_REAL, MEM, LPAREN }` -> Opções de execução
* **`FIRST(<acao_numero>)`** = `{ KEYWORD_RES, MEM, NUM_INT, NUM_REAL, LPAREN }` -> Ação após um número primário
* **`FIRST(<conteudo_par>)`** = `{ NUM_INT, NUM_REAL, LPAREN }` -> Expressão matemática aninhada
* **`FIRST(<acao_pos_par>)`** = `{ NUM_INT, NUM_REAL, LPAREN }` -> Resolve o que acontece após fechar um parêntese
* **`FIRST(<conteudo_pos_par_lparen>)`** = `{ LET, MEM, NUM_INT, NUM_REAL, LPAREN }` -> Bloco vs Operando
* **`FIRST(<controle>)`** = `{ IF, WHILE }` -> Keywords das estruturas condicionais
* **`FIRST(<expressao>)`** = `{ NUM_INT, NUM_REAL, LPAREN }` -> O que inicia uma conta
* **`FIRST(<operando>)`** = `{ NUM_INT, NUM_REAL, LPAREN }` -> Os termos da conta
* **`FIRST(<conteudo_operando>)`** = `{ MEM, NUM_INT, NUM_REAL, LPAREN }`
* **`FIRST(<operador>)`** = `{ OP_SOMA, OP_SUB, OP_MULT, OP_DIV_INT, OP_DIV_REAL, OP_MOD, OP_POT, OP_MAIOR, ... }`

## 5. Conjuntos FOLLOW

* **`FOLLOW(<programa>)`** = `{ $ }` -> EOF
* **`FOLLOW(<lista_comandos_globais>)`** = `{ $ }`
* **`FOLLOW(<conteudo_global>)`** = `{ $ }`
* **`FOLLOW(<lista_comandos_bloco>)`** = `{ RPAREN }` -> O miolo de um bloco condicional fecha com ')'
* **`FOLLOW(<conteudo_comando>)`** = `{ RPAREN }`
* **`FOLLOW(<acao_numero>)`** = `{ RPAREN }`
* **`FOLLOW(<conteudo_par>)`** = `{ RPAREN }`
* **`FOLLOW(<acao_pos_par>)`** = `{ RPAREN }`
* **`FOLLOW(<conteudo_pos_par_lparen>)`** = `{ RPAREN }`
* **`FOLLOW(<controle>)`** = `{ RPAREN }` -> As keywords finalizam o comando de controle
* **`FOLLOW(<expressao>)`** = `{ RPAREN }`
* **`FOLLOW(<operando>)`** = `{ NUM_INT, NUM_REAL, LPAREN, OP_SOMA, ... }` -> Após um operando vem outro operando ou operador
* **`FOLLOW(<conteudo_operando>)`** = `{ RPAREN }`
* **`FOLLOW(<operador>)`** = `{ RPAREN }` -> Em RPN o operador é sempre o termo final da expressão

---

## 6. Tabela Preditiva LL(1)

> **Lendo a Tabela Preditiva:** Para garantir a legibilidade e utilidade prática, disponibilizamos a tabela em dois formatos: uma lista estruturada e a tradicional matriz bidimensional (tabela de verdade).

### 6.1. Formato em Lista (Mais Legível)

Procure o **Não-Terminal** que você está derivando e, em seguida, verifique qual é o **Token (Terminal)** de entrada. A seta indicará a regra que o Parser deve seguir.

#### Modificadores Globais
* **`<programa>`**
  * `LPAREN` -> `LPAREN START RPAREN <lista_comandos_globais>`
* **`<lista_comandos_globais>`**
  * `LPAREN` -> `LPAREN <conteudo_global>`
* **`<conteudo_global>`**
  * `END` -> `END RPAREN`
  * `NUM_INT`, `NUM_REAL`, `MEM`, `LPAREN` ➔ `<conteudo_comando> RPAREN <lista_comandos_globais>`

#### Blocos e Comandos
* **`<lista_comandos_bloco>`**
  * `LPAREN` -> `LPAREN <conteudo_comando> RPAREN <lista_comandos_bloco>`
  * `RPAREN` -> `[VAZIO]`
* **`<conteudo_comando>`**
  * `NUM_INT` -> `NUM_INT <acao_numero>`
  * `NUM_REAL` -> `NUM_REAL <acao_numero>`
  * `MEM` -> `MEM`
  * `LPAREN` -> `LPAREN <conteudo_par> RPAREN <acao_pos_par>`

#### Ações (Resoluções de Fluxo)
* **`<acao_numero>`**
  * `KEYWORD_RES` -> `KEYWORD_RES`
  * `MEM` -> `MEM`
  * `NUM_INT`, `NUM_REAL`, `LPAREN` -> `<operando> <operador>`
* **`<acao_pos_par>`**
  * `NUM_INT` -> `NUM_INT <operador>`
  * `NUM_REAL` -> `NUM_REAL <operador>`
  * `LPAREN` -> `LPAREN <conteudo_pos_par_lparen>`
* **`<conteudo_pos_par_lparen>`**
  * `LET` -> `LET <lista_comandos_bloco> RPAREN <controle>`
  * `MEM`, `NUM_INT`, `NUM_REAL`, `LPAREN` -> `<conteudo_operando> RPAREN <operador>`

#### Matemática e Operandos
* **`<conteudo_par>`**
  * `NUM_INT`, `NUM_REAL`, `LPAREN` -> `<expressao>`
* **`<expressao>`**
  * `NUM_INT`, `NUM_REAL`, `LPAREN` -> `<operando> <operando> <operador>`
* **`<operando>`**
  * `NUM_INT` -> `NUM_INT`
  * `NUM_REAL` -> `NUM_REAL`
  * `LPAREN` -> `LPAREN <conteudo_operando> RPAREN`
* **`<conteudo_operando>`**
  * `MEM` -> `MEM`
  * `NUM_INT`, `NUM_REAL`, `LPAREN` -> `<expressao>`
* **`<controle>`**
  * `IF` -> `IF`
  * `WHILE` -> `WHILE`

#### Operadores Finais
* **`<operador>`**
  * Qualquer token de operador (`OP_SOMA`, `OP_SUB`, etc) -> *O Próprio Operador*

### 6.2. Matriz Preditiva (Tabela de Verdade)

Esta é a visualização clássica 2D do Parser LL(1). O cruzamento de um **Não-Terminal** (linha) com um **Terminal** (coluna) define qual regra de produção o parser deve empilhar. Células em branco indicam **Erro Sintático**. 
*(Nota: A coluna `OP_*` engloba todos os operadores matemáticos e relacionais).*

| Não-Terminal | `LPAREN` | `RPAREN` | `END` | `NUM_INT` | `NUM_REAL` | `MEM` | `LET` | `KEYWORD_RES` | `IF` | `WHILE` | `OP_*` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<programa>` | `LPAREN START RPAREN <lista_comandos_globais>` | | | | | | | | | | |
| `<lista_comandos_globais>` | `LPAREN <conteudo_global>` | | | | | | | | | | |
| `<conteudo_global>` | `<conteudo_comando> RPAREN <lista_comandos_globais>` | | `END RPAREN` | `<conteudo_comando> RPAREN <lista_comandos_globais>` | `<conteudo_comando> RPAREN <lista_comandos_globais>` | `<conteudo_comando> RPAREN <lista_comandos_globais>` | | | | | |
| `<lista_comandos_bloco>` | `LPAREN <conteudo_comando> RPAREN <lista_comandos_bloco>` | `[VAZIO]` | | | | | | | | | |
| `<conteudo_comando>` | `LPAREN <conteudo_par> RPAREN <acao_pos_par>` | | | `NUM_INT <acao_numero>` | `NUM_REAL <acao_numero>` | `MEM` | | | | | |
| `<acao_numero>` | `<operando> <operador>` | | | `<operando> <operador>` | `<operando> <operador>` | `MEM` | | `KEYWORD_RES` | | | |
| `<conteudo_par>` | `<expressao>` | | | `<expressao>` | `<expressao>` | | | | | | |
| `<acao_pos_par>` | `LPAREN <conteudo_pos_par_lparen>` | | | `NUM_INT <operador>` | `NUM_REAL <operador>` | | | | | | |
| `<conteudo_pos_par_lparen>` | `<conteudo_operando> RPAREN <operador>` | | | `<conteudo_operando> RPAREN <operador>` | `<conteudo_operando> RPAREN <operador>` | `<conteudo_operando> RPAREN <operador>` | `KEYWORD_LET <lista_comandos_bloco> RPAREN <controle>` | | | | |
| `<controle>` | | | | | | | | | `IF` | `WHILE` | |
| `<expressao>` | `<operando> <operando> <operador>` | | | `<operando> <operando> <operador>` | `<operando> <operando> <operador>` | | | | | | |
| `<operando>` | `LPAREN <conteudo_operando> RPAREN` | | | `NUM_INT` | `NUM_REAL` | | | | | | |
| `<conteudo_operando>` | `<expressao>` | | | `<expressao>` | `<expressao>` | `MEM` | | | | | |
| `<operador>` | | | | | | | | | | | *O próprio operador* |

## 7. Exemplos de Árvores Sintáticas (AST)

> **Exemplo 1: Expressão Matemática `(3.14 2.0 +)`**
> O processo abaixo demonstra a hierarquia preditiva (Top-Down) do nosso Parser LL(1) consumindo os tokens fornecidos pelo Lexer.

```
<conteudo_comando>
├── NUM_REAL (3.14)
└── <acao_numero>
    ├── <operando>
    │   └── NUM_REAL (2.0)
    └── <operador>
        └── OP_SOMA (+)
```
### Exemplo 2: Gravação em Memória `10 MEM`
Neste exemplo, o parser identifica um número seguido imediatamente por uma variável de memória, derivando para a regra de armazenamento (atribuição).

```
<conteudo_comando>
├── NUM_INT (10)
└── <acao_numero>
    └── MEM (MEM)

```

### Exemplo 3: Expressão Aninhada ( 2 3 + ) 4 *

O parser consome o parêntese interno, resolve a soma e, ao encontrar o fecha-parêntese, delega a multiplicação externa para o <acao_pos_par>.
```
<conteudo_comando>
├── LPAREN ( ( )
├── <conteudo_par>
│   └── <expressao>
│       ├── <operando>
│       │   └── NUM_INT (2)
│       ├── <operando>
│       │   └── NUM_INT (3)
│       └── <operador>
│           └── OP_SOMA (+)
├── RPAREN ( ) )
└── <acao_pos_par>
    ├── NUM_INT (4)
    └── <operador>
        └── OP_MULT (*)

```