**Responsável:** Dani Heart Basso

## Tarefas

- Implementar `lerTokens(arquivo)` para ler tokens salvos da Fase 1
- Ler arquivo de tokens no formato definido pelo grupo
- Implementar validação básica de tokens
- Criar exemplos de uso
- Testar integração com o analisador léxico da Fase 1

## Interface

- **Entrada:** Nome do arquivo de tokens
- **Saída:** Vetor de tokens estruturado
- **Fornece:** tokens para `parsear()`

---

### Decisões de Arquitetura

## 1. Uso de Expressões Regulares (Regex) para Varredura

**O que é:**
O lexer (`lexer.py`) utiliza o módulo `re` do Python para varrer as linhas e classificar os tokens, destacando-se o uso de `re.findall(r'\(|\)|[^\s()]+', linha_limpa)`.

**Por que:**
Na Fase 1, a leitura era feita caractere por caractere (simulando uma máquina de estados finitos manualmente). Usar Regex com a função `findall` simplifica drasticamente o código. A regra `\(|\)` garante que parênteses nunca fiquem grudados em variáveis (ex: `(VAR)` é lido como `(`, `VAR`, `)` automaticamente), eliminando o "balanceamento manual" da fase anterior.

---

## 2. Mapa de Tokens Fixos em O(1)

**O que é:**
Keywords e operadores são validados através de um dicionário chamado `MAPA_TOKENS_FIXOS`.

**Por que:**
Ao invés de criar dezenas de `if/elif` para validar se um caractere é um `+`, `-`, `LET` ou `IF`, o dicionário permite uma busca de complexidade O(1) (instantânea). Se a linguagem for expandida no futuro, basta adicionar uma nova chave no dicionário.

---

## 3. Ignorar o `tokens.txt` da Fase 1

**O que é:**
Apesar do enunciado citar a leitura de tokens "da Fase 1", nosso `lerTokens` processa os arquivos de código-fonte cru (`testes1.txt`).

**Por que:**
O professor exige explicitamente que o executável rode passando o script como argumento (`./AnalisadorSintatico teste1.txt`). Se lêssemos o vetor literal `['(', '3', ')']` do arquivo `tokens.txt` gerado na Fase 1, o Lexer falharia em varrer os colchetes e as aspas. Refazer a análise léxica do zero diretamente do arquivo garante os 70% da nota por "Análise Léxica Consistente".

---

## 4. `Token` como `@dataclass` simples

**O que é:**
A classe `Token` foi implementada usando o decorador `@dataclass` contendo apenas `tipo`, `valor` e `linha`.

**Por que:**
Reduz a quantidade de código boilerplate (não precisamos escrever `__init__` ou `__repr__`). Além disso, ela casa perfeitamente com o `Protocol` definido pela Mari no parser. O Lexer gera o dataclass, e o Parser aceita por *structural typing*, sem que precisemos importar nada de um arquivo para o outro.

---

## 5. TDD (Test-Driven Development) Isolado

**O que é:**
Os testes no `test_lexer.py` usam a biblioteca `pytest` simulando arquivos temporários através da fixture `tmp_path`.

**Por que:**
Criar arquivos `.txt` reais para rodar testes suja o repositório. O `tmp_path` cria os arquivos na memória do Sistema Operacional e destrói após o teste. Além disso, garante que o Aluno 3 possua 100% de cobertura contra "lixo" no código, testando se a exceção `ValueError` é levantada na linha correta, conforme exige a rubrica de robustez.