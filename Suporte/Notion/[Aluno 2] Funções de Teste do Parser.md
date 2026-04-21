**Responsável:** Mariana Alves

## Tarefas

- Criar funções de teste específicas para o parser:
    - Erros léxicos (tokens inválidos)
    - Expressões válidas simples e aninhadas
    - Estruturas de controle válidas
    - Entradas inválidas (erros sintáticos)
    - Casos extremos (aninhamento profundo, expressões vazias)
- Garantir que as mensagens de erro incluam **linha e tipo do erro**
- Documentar os casos de teste

## Decisões de Arquitetura

## 1. Testar `parsear()` isolado, sem lexer e sem builder real

**O que é:**
Os testes chamam `parsear()` diretamente com listas de tokens construídas à mão.

```python
tokens = [
    Token("LPAREN", "(", 1), Token("START", "START", 1), Token("RPAREN", ")", 1),
    Token("LPAREN", "(", 2), Token("END", "END", 2), Token("RPAREN", ")", 2),
]
arvore = parsear(tokens, {}, builder_stub)
```

**Por que:**
Testar junto com o lexer real (aluno 3) é testar dois módulos ao mesmo tempo — se o teste falha, não se sabe qual dos dois está errado. Tokens manuais tornam o teste de unidade puro.

**Consequência:**
Qualquer falha nos testes aponta diretamente para um bug em `parser.py`, não em outro módulo. 

---

## 2. Builder stub mínimo como verificador de chamadas

**O que é:**
Em vez de usar `ConstrutorNo` (que constrói `No` real), os testes usam um builder stub que apenas registra quais métodos foram chamados e com quais argumentos:

```python
class BuilderStub:
    def __init__(self):
        self.chamadas = []

    def criar_operando_num(self, valor, linha):
        self.chamadas.append(("criar_operando_num", valor, linha))
        return f"NUM:{valor}"

    def criar_expr(self, esq, dir, op, linha):
        self.chamadas.append(("criar_expr", esq, dir, op))
        return f"EXPR({esq},{dir},{op})"

    # ... etc
```

**Por que:**
O que o parser precisa produzir não é uma árvore específica — é uma sequência correta de chamadas ao builder. O stub permite verificar isso sem depender da implementação de `ConstrutorNo`. Além disso, retornar strings simples (como `"NUM:3"`) em vez de objetos `No` facilita a leitura dos asserts nos testes.

**Consequência:**
Os testes verificam o comportamento do parser (quais chamadas ele faz, em que ordem, com quais dados), não a estrutura interna da árvore. 

---

## 3. Tokens como dataclass simples nos testes

**O que é:**
Os testes definem um `Token` simples para evitar dependência do lexer:

```python
from dataclasses import dataclass

@dataclass
class Token:
    tipo: str
    valor: str
    linha: int
```

**Por que:**
O parser usa `Token` como Protocol — qualquer objeto com `tipo`, `valor` e `linha` serve. Um dataclass local nos testes satisfaz o Protocol sem importar nada do projeto. Isso mantém os testes completamente independentes.

**Consequência:**
O arquivo de testes não importa nenhum módulo além de `parser`. Se `parser.py` mudar internamente sem quebrar o contrato, os testes continuam funcionando sem alteração.

---

## 4. Casos de teste organizados por categoria gramatical

**O que é:**
Os testes são agrupados por categoria, não por número sequencial:

- **Caminho feliz — programa mínimo**: `(START)(END)` sem nenhum comando
- **Caminho feliz — expressões**: aritméticas simples, aninhadas, reais
- **Caminho feliz — comandos especiais**: `N RES`, `V MEM`, `(MEM)`
- **Caminho feliz — controle**: IF com bloco, WHILE com bloco
- **Erros sintáticos esperados**: token errado, EOF prematuro, token inesperado após programa

**Por que:**
Cada categoria da gramática tem seu próprio conjunto de regras (`_expressao`, `_conteudo_comando`, `_controle`, etc.). Agrupar por categoria facilita identificar qual regra quebrou quando um teste falha.

**Consequência:**
Quando um novo operador ou estrutura de controle é adicionado à gramática, fica claro em qual grupo adicionar o caso de teste correspondente.

---

## 5. Testes de erro verificam tipo da exceção e número da linha

**O que é:**
Testes que esperam `ErroSintatico` verificam também que a mensagem inclui o número de linha correto:

```python
import pytest

def test_token_inesperado_apos_programa():
    tokens = [
        Token("LPAREN", "(", 1), Token("START", "START", 1), Token("RPAREN", ")", 1),
        Token("LPAREN", "(", 2), Token("END", "END", 2), Token("RPAREN", ")", 2),
        Token("NUM_INT", "5", 3),  # token sobrando
    ]
    with pytest.raises(ErroSintatico) as exc_info:
        parsear(tokens, {}, BuilderStub())
    assert "linha 3" in str(exc_info.value)
```

**Por que:**
Requisito de projeto: mensagens de erro devem incluir linha e tipo do token inesperado. Testar apenas `pytest.raises(ErroSintatico)` sem verificar a mensagem não cobre esse requisito — o parser poderia lançar a exceção na linha errada ou sem informação útil.

**Consequência:**
Qualquer refatoração que quebre o número de linha nos erros é detectada imediatamente pelos testes.

---

## 6. A tabela LL(1) é passada como dicionário vazio nos testes

**O que é:**
`parsear(tokens, {}, builder)` — a tabela é sempre `{}` nos testes unitários.

**Por que:**
O parser descendente recursivo não consulta a tabela em tempo de execução — as regras estão embutidas nas funções. A tabela é um parâmetro de contrato (produzido por aluno 1), mas não afeta o comportamento do parser. Passar `{}` é honesto: o parser não usa esse valor, e o teste não finge que usa.

**Consequência:**
Se algum dia o parser for refatorado para consultar a tabela, os testes quebrarão — o que é correto, porque os testes precisariam ser atualizados com uma tabela real.

---

## 7. Teste de programa mínimo como sanidade básica

**O que é:**
O primeiro teste (executado antes de qualquer outro) é o programa mais simples possível:

```python
def test_programa_minimo():
    tokens = [
        Token("LPAREN", "(", 1), Token("START", "START", 1), Token("RPAREN", ")", 1),
        Token("LPAREN", "(", 2), Token("END", "END", 2), Token("RPAREN", ")", 2),
    ]
    builder = BuilderStub()
    parsear(tokens, {}, builder)
    assert ("criar_programa", [], 1) in builder.chamadas
```

**Por que:**
Se esse teste falha, o parser não funciona nem para o caso trivial — inútil rodar os outros. É o "smoke test" do parser. Confirma que `_programa`, `_lista_comandos_globais` e `_conteudo_global` (caminho END) funcionam.

**Consequência:**
Qualquer erro de inicialização (import errado, método faltando no builder) é detectado aqui, não no meio de um teste complexo.

---

## 8. Expressões aninhadas testam recursão do parser

**O que é:**
Um teste específico para expressão com operando entre parênteses (que ativa `_operando` → `_conteudo_operando_no` → `_expressao` recursivamente):

```python
# Representa: ( (3 4 +) 5 * )
tokens = [
    Token("LPAREN", "(", 1), Token("START", ...),  # cabeçalho
    Token("LPAREN", "(", 2),
      Token("LPAREN", "(", 2),
        Token("NUM_INT", "3", 2), Token("NUM_INT", "4", 2), Token("OP_SOMA", "+", 2),
      Token("RPAREN", ")", 2),
      Token("NUM_INT", "5", 2),
      Token("OP_MULT", "*", 2),
    Token("RPAREN", ")", 2),
    Token("LPAREN", "(", 3), Token("END", ...),  # rodapé
]
```

**Por que:**
A gramática permite expressões arbitrariamente aninhadas. Se o parser tiver bug na recursão (ex.: consumir RPAREN demais ou de menos), o teste de expressão simples passa, mas o de aninhamento falha. Sem esse teste, o bug só aparece em tempo de execução.

**Consequência:**
Garante que `_conteudo_operando_no` chama `_expressao` corretamente quando o operando é uma sub-expressão entre parênteses.
