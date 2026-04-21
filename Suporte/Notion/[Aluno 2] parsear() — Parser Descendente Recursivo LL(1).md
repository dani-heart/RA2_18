**Responsável:** Mariana Alves

## Tarefas

- Validar teoricamente a gramática do Aluno 1 (verificar ausência de conflitos LL(1))
- Implementar `parsear(_tokens_, tabela_ll1)` para análise sintática descendente recursiva
- Usar a tabela LL(1) para guiar o processo de parsing
- Implementar a **pilha de análise** e controle de derivação
- Criar função para cada não-terminal (parsing descendente recursivo)
- Gerenciar o buffer de entrada de tokens
- Detectar e reportar **erros sintáticos** com mensagens claras (linha + tipo)
- Implementar **recuperação básica de erros**
- Criar funções de teste para validar o parser
- Testar com expressões válidas e inválidas:
    - `(3.14 2.0 +)` (expressao valida)
    - `((A B +) (C D *) /)` (expressao valida)
    - `(A B + C)` (erro sintatico)

## Funções a implementar

- `parsear(_tokens_, tabela_ll1)`
- Funções para cada não-terminal

## Interface

- **Entrada:** Vetor de tokens + tabela LL(1)
- **Saída:** Estrutura de derivação ou erro sintático
- **Fornece:** estrutura de derivação para `gerarArvore()`

---

### Decisoes de Arquitetura para o Projeto:

## 1. `Token` como Protocol:

`parser.py` define seu próprio `Token` como um `Protocol` do Python:

```python
class Token(Protocol):
    tipo: str
    valor: str
    linha: int
```

**Por que?**
Com `Protocol`, o parser declara apenas o que ele precisa que um token tenha — três atributos. Qualquer objeto que tenha `tipo`, `valor` e `linha` funciona automaticamente, sem precisar herdar nada nem importar nada. Isso é chamado de *structural typing*.

**Consequência:**
`parser.py` não importa nenhum módulo externo do projeto. É completamente independente. 
---

## 2. `ConstrutorArvore` como Protocol (builder pattern)

**O que é:**
O parser define uma segunda interface, também como Protocol:

```python
class ConstrutorArvore(Protocol):
    def criar_operando_num(self, valor: str, linha: int) -> Any: ...
    def criar_expr(self, esq: Any, dir: Any, op: Any, linha: int) -> Any: ...
    # ... etc
```

**Por que:**
O parser (aluno 2) não deveria saber como a árvore sintática é representada — isso é responsabilidade de aluno 4. O builder é o contrato entre os dois: o parser diz "vou te chamar nesses momentos com esses dados", e aluno 4 decide o que fazer com isso. O parser passa handles opacos (`Any`) sem saber o que são.

**Consequência:**
`parser.py` não importa `No`, não conhece `EXPR`, `CMD_MEM_STORE` ou qualquer nó semântico. Aluno 4 poderia trocar a representação interna da árvore sem tocar no parser.

---

## 3. Assinatura `parsear(tokens, tabela_ll1, builder)`

**O que é:**
A função pública recebe três parâmetros: a lista de tokens, a tabela LL(1) (produzida por aluno 1) e o builder (produzido por aluno 4).

**Por que `tabela_ll1` se o parser não a usa diretamente?**
O parser descendente recursivo já tem as regras da gramática embutidas nas funções recursivas — ele não precisa consultar a tabela em tempo de execução. Mas a tabela é passada por contrato: aluno 1 a produz, aluno 2 a recebe. 
Manter o parâmetro garante que a interface entre os módulos seja respeitada e que, se no futuro o parser for substituído por uma versão orientada a tabela, a assinatura não precise mudar.

**Por que `builder` como parâmetro e não criado internamente?**
Se o parser criasse o builder internamente, estaria acoplado a `ConstrutorNo` de aluno 4. Receber o builder de fora (injeção de dependência) significa que o parser não sabe nem precisa saber quem vai construir a árvore.

---

## 4. `parsear()` retorna `Any`

**O que é:**
A função retorna `Any`, não `No`.

**Por que:**
Do ponto de vista do parser, o retorno é o que o builder produz — e o parser não sabe o que o builder produz. O tipo concreto (`No`) é conhecimento de aluno 4. Se o parser retornasse `No`, estaria importando algo de aluno 4, criando dependência circular.

---

## 5. `_Parser` como classe interna

**O que é:**
Toda a lógica de parsing vive em `_Parser`, que é prefixada com `_` (convencção Python para "privado"). A única interface pública é a função `parsear()`.

**Por que:**
Encapsulamento. Quem chama `parsear()` não precisa saber que existe um objeto `_Parser`, não precisa gerenciar estado, não precisa chamar métodos em sequência. A função `parsear()` cria o parser, roda, e retorna o resultado. 

---

## 6. Uma função por não-terminal da gramática

**O que é:**
Cada regra da gramática LL(1) tem sua própria função privada: `_programa`, `_conteudo_comando`, `_acao_numero`, `_expressao`, `_operando`, `_operador`, etc.

**Por que:**
Essa é a definição de parser descendente recursivo — cada não-terminal vira uma função. Facilita rastrear erros ("em qual regra estou?"), testar regras isoladamente, e corresponde diretamente à gramática documentada no EBNF.

---

## 7. `ErroSintatico` com número de linha

**O que é:**
Todos os erros lançam `ErroSintatico` com mensagem que inclui o número da linha, o token esperado e o token encontrado:

```
Erro sintático na linha 10: esperado 'RPAREN', encontrado 'OP_SOMA' ('+').
```

**Por que:**
Requisito de robustez  (15% da nota).

---

## 8. Handles opacos passados entre funções

**O que é:**
As funções internas do parser retornam `Any` e passam esses valores para o builder sem inspecioná-los:

```python
op_esq = self._builder.criar_operando_num(primeiro.valor, linha)
op_dir = self._operando()   # retorna Any
op_no  = self._operador()   # retorna Any
return self._builder.criar_expr(op_esq, op_dir, op_no, linha)
```

**Por que:**
O parser sabe quando chamar o builder e com quais dados brutos (strings de valores, números de linha). Não sabe o que o builder faz com isso. Os handles são opacos porque o parser não precisa nem deve abri-los.

---

## 9. `_lista_comandos_bloco` com loop em vez de recursão

**O que é:**
Blocos de comandos dentro de IF/WHILE são coletados com um `while`:

```python
def _lista_comandos_bloco(self) -> list:
    cmds = []
    while self._tipo_atual() == "LPAREN":
        self._consumir("LPAREN")
        cmd = self._conteudo_comando()
        self._consumir("RPAREN")
        cmds.append(cmd)
    return cmds
```

**Por que:**
A gramática permite zero ou mais comandos no bloco (produção com ε). Implementar com loop é mais legível e evita risco de stack overflow em blocos muito grandes. O resultado é uma lista plana de comandos que o builder transforma em nó `BLOCO`.

---

## 10. `_controle()` retorna string, não nó

**O que é:**
A função que identifica `IF` ou `WHILE` retorna `"IF"` ou `"WHILE"` como string:

```python
def _controle(self) -> str:
    if tipo == "IF":
        self._consumir("IF")
        return "IF"
    elif tipo == "WHILE":
        ...
```

**Por que:**
O parser não cria nós para palavras-chave de controle isoladas — elas só têm significado em conjunto com a condição e o bloco. A string é usada imediatamente para decidir qual método do builder chamar (`criar_if` ou `criar_while`), sem precisar criar nenhum nó intermediário.
