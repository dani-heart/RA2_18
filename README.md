# Compilador RPN — RA2-18

Projeto acadêmico para a disciplina **Linguagens Formais e Compiladores (2026-1)**.

**Instituição:** Pontifícia Universidade Católica do Paraná - PUC/PR — 2026-1

## Integrantes

- Dani Heart Basso — @dani-heart
- Mariana Alves da Silva — @himarialves

**Grupo no Canvas:** RA2-18

---

## Descrição

Compilador completo para uma linguagem RPN (Notação Polonesa Reversa) simplificada, composto por:

1. **Analisador Léxico** (`lexer.py`) — tokenização do código-fonte
2. **Gramática LL(1)** (`gramatica.py`) — construção da gramática, cálculo de FIRST/FOLLOW e tabela LL(1)
3. **Analisador Sintático LL(1)** (`parser.py`) — análise descendente recursiva com recuperação de erros, gera a árvore sintática
4. **Gerador de Árvore** (`arvore.py`) — impressão e serialização JSON da árvore sintática
5. **Gerador de Assembly ARMv7** (`assembly.py`) — geração de código para o CPulator (DEC1-SOC v16.1)
6. **Integração** (`main.py`) — pipeline completo

---

## Como executar

```bash
python3 main.py <arquivo.txt>
```

Exemplos:
```bash
python3 main.py teste1.txt
python3 main.py teste2.txt
python3 main.py teste3.txt
```

Saídas geradas:
- `arvore_<nome>.json` — árvore sintática serializada em JSON
- `output_<nome>.s` — código Assembly ARMv7 pronto para o CPulator

---

## Arquivos de teste

| Arquivo | Conteúdo |
|---|---|
| `teste1.txt` | Todos os operadores (`+` `-` `*` `/` `%` `^` `\|`), inteiros, reais, `RES`, `MEM`, `IF`, `WHILE` |
| `teste2.txt` | Todos os operadores, `MEM`, `IF`, `WHILE`, `RES` com histórico |
| `teste3.txt` | Todos os operadores, `MEM`, `IF`, `WHILE`, `RES` com reais |
| `erro_lexico.txt` | Demonstração de erro léxico (caractere inválido) |

Os três testes principais foram executados e validados manualmente no **CPulator ARMv7 DEC1-SOC v16.1**.

---

## Sintaxe da linguagem

### Estrutura do programa

```
(START)
... comandos ...
(END)
```

### Expressões aritméticas (notação RPN)

```
(operando1 operando2 operador)
```

Exemplos:
```
(3 4 +)          @ 3 + 4 = 7
(10 2 -)         @ 10 - 2 = 8
(6 7 *)          @ 6 * 7 = 42
(20 4 /)         @ divisão inteira: 20 / 4 = 5
(17 5 %)         @ resto: 17 % 5 = 2
(2 10 ^)         @ potência: 2^10 = 1024
(9.0 3.0 |)      @ divisão real: 9.0 / 3.0 = 3.0
```

Operandos podem ser aninhados:
```
((3 4 +) 2 *)    @ (3+4) * 2 = 14
```

### Operadores disponíveis

| Símbolo | Operação |
|---|---|
| `+` | Adição |
| `-` | Subtração |
| `*` | Multiplicação |
| `/` | Divisão inteira |
| `\|` | Divisão real (ponto flutuante) |
| `%` | Resto |
| `^` | Potenciação |
| `>` `<` `==` `!=` `>=` `<=` | Relacionais (retornam 0.0 ou 1.0) |

### Variáveis de memória

```
(5 NOME)         @ armazena 5 em NOME
(NOME)           @ carrega valor de NOME (0 se não inicializada)
```

Nomes de variáveis: somente letras maiúsculas (ex.: `VAR`, `CONT`, `EULER`). `RES` é reservado.

### Histórico de resultados

```
(N RES)          @ carrega o resultado de N expressões atrás no histórico
```

Apenas expressões aritméticas de topo de programa são salvas no histórico (não IF/WHILE/MEM).

### Estruturas de controle

**Sintaxe: Proposta A (postfix completo)**

#### Condicional (ramo único, sem ELSE)

```
( condição (LET (cmd1) (cmd2) ... ) IF )
```

Exemplo — executa o bloco se `VALOR > 5`:
```
( ((VALOR) 5 >) (LET (100 RESULTADO) ) IF )
```

#### Laço de repetição

```
( condição (LET (cmd1) (cmd2) ... ) WHILE )
```

Exemplo — executa enquanto `CONT == 1`:
```
( ((CONT) 1 ==) (LET (0 CONT) ) WHILE )
```

**Notas:**
- Variáveis usadas como operando devem estar entre parênteses: `(VARNAME)`
- O bloco `LET` termina com `)` antes do `IF` ou `WHILE`
- Não há `ELSE` — o IF é de ramo único

---

## Assembly gerado

O código Assembly é para ARMv7 bare-metal no **CPulator DEC1-SOC v16.1**.

- Todos os valores são representados em **F64 (IEEE 754 double-precision)**
- Resultado de cada expressão fica em `D0` (registrador VFP de 64 bits)
- Inteiros são convertidos para F64 via `VCVT.F64.S32`
- Variáveis MEM: alocadas em `.data` como `.double` (8 bytes)
- Histórico RES: array `RES_HIST` em `.data` (256 entradas × 8 bytes), índice em `RES_IDX`
- Pilha de software: `STACK` em `.data` (1 KB), inicializada via `LDR SP, =STACK_TOP`
- Divisão e módulo: implementados via loop de subtração (VDIV não suportado no CPulator)
- Potenciação: implementada via loop de multiplicação

Para executar o assembly gerado, copie o conteúdo de `output_<nome>.s` no CPulator em [cpulator.01xz.net](https://cpulator.01xz.net/?sys=arm-de1soc).
