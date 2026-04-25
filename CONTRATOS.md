# CONTRATOS.md — Contratos de Interface do Projeto RA2-18

---

## 1. Nomes Canônicos dos Tipos de Token

Os nomes abaixo são os únicos válidos no código. São os mesmos usados em `gramatica.py`,
que é o módulo implementado e, portanto, a fonte de verdade.

> **Nota:** `EBNF.md` usa `ID_VAR`, `LET` e `RES` como nomes de documentação/alias.
> No código, os nomes corretos são `MEM`, `KEYWORD_LET` e `KEYWORD_RES`.
> `AGENT_INSTRUCTIONS_PJBL2.md` usa `OP`, `REL_OP`, `KEYWORD_MEM`, `KEYWORD_START`,
> `KEYWORD_END` — esses nomes NÃO são usados no código. Use os nomes desta tabela.

| Tipo (canônico) | Exemplos de valor | Descrição |
|---|---|---|
| `NUM_INT` | `3`, `42`, `0` | Literal inteiro |
| `NUM_REAL` | `3.14`, `2.0`, `0.5` | Literal real (ponto flutuante) |
| `MEM` | `VAR`, `X`, `EULER`, `CONTADOR` | Identificador de variável em memória (letras maiúsculas) |
| `LPAREN` | `(` | Abre parêntese |
| `RPAREN` | `)` | Fecha parêntese |
| `KEYWORD_RES` | `RES` | Keyword de histórico de resultados |
| `KEYWORD_LET` | `LET` | Keyword de abertura de bloco de controle |
| `START` | `START` | Keyword de início de programa |
| `END` | `END` | Keyword de fim de programa |
| `IF` | `IF` | Keyword de condicional |
| `WHILE` | `WHILE` | Keyword de laço |
| `OP_SOMA` | `+` | Adição |
| `OP_SUB` | `-` | Subtração |
| `OP_MULT` | `*` | Multiplicação |
| `OP_DIV_INT` | `/` | Divisão inteira |
| `OP_DIV_REAL` | `\|` | Divisão real |
| `OP_MOD` | `%` | Resto da divisão inteira |
| `OP_POT` | `^` | Potenciação (expoente inteiro positivo) |
| `OP_MAIOR` | `>` | Maior que |
| `OP_MENOR` | `<` | Menor que |
| `OP_IGUAL` | `==` | Igual a |
| `OP_DIF` | `!=` | Diferente de |
| `OP_MAIOR_IGUAL` | `>=` | Maior ou igual a |
| `OP_MENOR_IGUAL` | `<=` | Menor ou igual a |

---

## 2. Contrato: Dataclass Token

```python
from dataclasses import dataclass, field

@dataclass
class Token:
    tipo: str   # Um dos tipos canônicos listados na seção 1
    valor: str  # Valor literal do token no arquivo fonte
    linha: int  # Número da linha no arquivo fonte (base 1)
```

---

## 3. Contrato: Dataclass No (Nó da Árvore Sintática)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class No:
    tipo: str           # Tipo semântico do nó (ver tabela abaixo)
    valor: Optional[str]  # Token literal para nós folha; None para nós compostos
    filhos: list        # List[No] — filhos na ordem da derivação
    linha: int          # Linha no arquivo fonte para rastreamento de erros
```

### Tipos de nó válidos

| tipo | valor | filhos | Descrição |
|---|---|---|---|
| `"PROGRAMA"` | `None` | lista de nós de comando | Raiz da árvore |
| `"EXPR"` | `None` | `[operando_esq, operando_dir, operador]` | Expressão aritmética/relacional RPN |
| `"OP"` | literal do operador (`"+"`, `"-"`, etc.) | `[]` | Nó folha de operador |
| `"OPERANDO"` | valor numérico literal | `[]` | Nó folha de número inteiro ou real |
| `"CMD_RES"` | `None` | `[operando_n]` | Comando `(N RES)` — histórico |
| `"CMD_MEM_STORE"` | `None` | `[valor_no, mem_id_no]` | Comando `(V MEM)` — armazenar |
| `"CMD_MEM_LOAD"` | `None` | `[mem_id_no]` | Comando `(MEM)` — carregar |
| `"IF"` | `None` | `[condicao_no, bloco_no]` | Condicional de ramo único |
| `"WHILE"` | `None` | `[condicao_no, bloco_no]` | Laço de repetição |
| `"BLOCO"` | `None` | lista de nós de comando | Bloco interno de IF/WHILE |
| `"MEM_ID"` | nome da variável (`"VAR"`, etc.) | `[]` | Nó folha de identificador de memória |

---

## 4. Sintaxe das Estruturas de Controle

Conforme implementado em `gramatica.py` com `KEYWORD_LET`.

### Condicional (ramo único — sem ELSE)
```
( condição ( LET (cmd1) (cmd2) ... ) IF )
```

Exemplo concreto:
```
( (3 4 >) (LET (1 2 +) ) IF )
```

### Laço de repetição
```
( condição ( LET (cmd1) (cmd2) ... ) WHILE )
```

Exemplo concreto:
```
( (CONT 0 >) (LET (CONT 1 - CONT) ) WHILE )
```

**Notas importantes:**
- O bloco `LET` sempre termina com `)` antes do `IF` ou `WHILE`.
- Não há `ELSE` — o IF é de ramo único.
- A condição é uma expressão relacional RPN completa.
- O bloco interno pode conter zero ou mais comandos.

---

## 5. Contrato: Interfaces das Funções Principais

```python
# lexer (Dani)
def lerTokens(caminho: str) -> list[Token]: ...

# gramática (Dani)
def construirTabelaLL1() -> dict: ...

# parser (Mariana)
def parsear(tokens: list[Token], tabela_ll1: dict) -> No: ...

# árvore (Mariana)
def imprimir_arvore(no: No, indent: int = 0) -> None: ...
def salvar_arvore_json(no: No, caminho: str) -> None: ...

# assembly (Mariana)
def gerarAssembly(arvore: No) -> str: ...

# integração (Mariana)
def main() -> None: ...
```

---

## 6. Regras de Precedência de Documentos

1. **Este arquivo (`CONTRATOS.md`)** — fonte de verdade para interfaces
2. **`gramatica.py`** — fonte de verdade para nomes de token e gramática
3. **`EBNF.md`** — documentação de gramática (aliases de token diferentes do código)
