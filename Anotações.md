# 📝 Anotações e Decisões - Fase 2 (Compiladores)

> [!warning] 1. Regras de Ouro da Linguagem
> * **Estrutura Global:** Todo programa que a gente fizer **tem** que começar com a linha `(START)` e terminar com `(END)`. O miolo é a nossa lista de comandos.
> * **Notação RPN e Parênteses:** A linguagem usa Notação Polonesa Reversa (os operandos vêm antes, e o operador no final). O detalhe mais chato/importante: **absolutamente tudo** tem que estar abraçado por parênteses.

> [!info] 2. Tipos de Dados e Variáveis
> * **O que vamos aceitar:** Números Inteiros e Reais (Double IEEE 754).
> * **Memória (Nossas variáveis):** Só podemos usar letras **MAIÚSCULAS** (ex: `PI`, `EULER`, `CONTADOR`).
> * **Matemática:** `+`, `-`, `*`, `|` (divisão real), `/` (divisão inteira), `%` (resto) e `^` (potência).

> [!example] 3. Comandos Especiais (Memória e Histórico)
> A documentação do professor pede `(V MEM)` e `(N RES)`. Traduzindo isso pra nossa vida prática:
> * **Gravar:** `(2.31 EULER)` -> Salva o valor `2.31` na variável `EULER`.
> * **Ler:** `(EULER)` -> Puxa o valor que tá em `EULER`.
> * **Histórico:** `(2 RES)` -> Pega a resposta de 2 linhas atrás (`RES` é palavra reservada).

> [!tip] 4. Estruturas de Controle (Como a gente decidiu fazer)
> Pra fazer os IFs e WHILEs funcionarem, a gente precisou adicionar operadores relacionais: `>`, `<`, `>=`, `<=`, `==`, `!=`.
> Como temos que manter a regra bendita do RPN `(A B operador)`, nossa sintaxe ficou assim:
> * **Nosso IF:** `( [condição] [bloco_de_codigo] IF )`
> * **Nosso WHILE:** `( [condição] [bloco_de_codigo] WHILE )`
> * *Detalhe:* O `[bloco_de_codigo]` interno usa a keyword `LET` para abrir um escopo novo. Ex: `( LET (comandos...) )`.

> [!bug] 5. O "Problema do Parêntese" e a Teoria LL(1)
> * **O BO:** Um parser LL(1) puro só enxerga 1 token pra frente. O problema é que a nossa linguagem obriga tudo a começar com `(`. Então o parser batia no `(` e travava sem saber se era uma conta, um IF, ou o fim do programa. Isso causava conflito.
> * **Como a gente resolveu (Fatoração):** Pegamos todas as regras que começavam com `(` e juntamos. Agora, o nosso parser "engole" o `(` primeiro e deixa pra tomar a decisão olhando o que tem *dentro* do parêntese (o próximo token). Assim a gente eliminou a ambiguidade e garantiu o 10 da gramática!

> [!todo] 6. Entregáveis Teóricos (Checklist)
> - [x] Gramática documentada em EBNF.
> - [x] Conjuntos FIRST e FOLLOW limpos (sem conflitos).
> - [x] Tabela Preditiva LL(1) construída.

---

## 7. Nosso rascunho final da Gramática (Já fatorada!)

*(Anotação rápida pra colar no código, a versão bonita está em `EBNF.md`)*

```ebnf
<Programa> ::= LPAREN START RPAREN <ListaComandosGlobais>

<ListaComandosGlobais> ::= LPAREN <ConteudoGlobal>

<ConteudoGlobal> ::= END RPAREN
                   | <ConteudoComando> RPAREN <ListaComandosGlobais>

<ListaComandosBloco> ::= LPAREN <ConteudoComando> RPAREN <ListaComandosBloco> 
                       | [VAZIO]

<ConteudoComando> ::= NUM_INT <AcaoNumero>
                    | NUM_REAL <AcaoNumero>
                    | ID_VAR
                    | LPAREN <ConteudoPar> RPAREN <AcaoPosPar>

<AcaoNumero> ::= RES
               | ID_VAR
               | <Operando> <Operador>

<ConteudoPar> ::= <Expressao>

<AcaoPosPar> ::= NUM_INT <Operador>
               | NUM_REAL <Operador>
               | LPAREN <ConteudoPosParLparen>

<ConteudoPosParLparen> ::= LET <ListaComandosBloco> RPAREN <Controle>
                         | <ConteudoOperando> RPAREN <Operador>

<Controle> ::= IF | WHILE

<Expressao> ::= <Operando> <Operando> <Operador>

<Operando> ::= NUM_INT
             | NUM_REAL
             | LPAREN <ConteudoOperando> RPAREN

<ConteudoOperando> ::= ID_VAR
                     | <Expressao>

<Operador> ::= OP_SOMA | OP_SUB | OP_MULT | OP_DIV_INT | OP_DIV_REAL | OP_MOD | OP_POT
             | OP_MAIOR | OP_MENOR | OP_IGUAL | OP_DIF | OP_MAIOR_IGUAL | OP_MENOR_IGUAL
