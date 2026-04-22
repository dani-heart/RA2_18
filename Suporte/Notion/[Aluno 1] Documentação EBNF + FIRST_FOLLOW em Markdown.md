**Responsável:** Dani Heart Basso

## Tarefas

- Criar arquivo markdown com:
    - Conjunto completo de regras de produção da gramática
    - Conjuntos FIRST e FOLLOW de cada não-terminal
    - Tabela de Análise LL(1) completa
- Incluir este arquivo no repositório GitHub
- A gramática deve cobrir: expressões RPN, `RES`, `MEM`, estruturas de controle, `START`, `END`

---

### Decisões de Arquitetura

## 1. Fatoração à Esquerda "Extrema" (O Problema do Parêntese)

**O que é:**
A gramática da nossa linguagem exige que quase todos os comandos comecem com `(`. Para resolver isso, todas as regras derivam de produções "ponta-de-lança" que consomem o `LPAREN` antes de tomar a decisão final.
Exemplo: O `<conteudo_comando>` consome coisas base, mas se vir um `(`, ele joga a decisão para `<acao_pos_par>`.

**Por que:**
Uma gramática preditiva LL(1) só consegue olhar 1 token à frente. Se existissem regras como `<IF> ::= ( ...` e `<WHILE> ::= ( ...` o Parser LL(1) entraria em conflito, pois a Tabela Preditiva teria múltiplas regras na coluna `LPAREN`. Fatorando à esquerda, nós eliminamos 100% da ambiguidade. O Parser "engole" o parêntese e escolhe o caminho baseando-se no que está *dentro* dele.

---

## 2. Tabelas e Conjuntos Estáticos (`gramatica.py`)

**O que é:**
Os conjuntos FIRST e FOLLOW, bem como a tabela de Parsing, foram hardcoded (escritos estaticamente em dicionários do Python), em vez de calculados dinamicamente no início da execução.

**Por que:**
A gramática é estrita e imutável neste projeto. Calcular os conjuntos FIRST/FOLLOW em runtime gastaria CPU desnecessariamente e abriria margem para bugs computacionais difíceis de rastrear. Escrevê-los estaticamente atesta o nosso domínio sobre a teoria da disciplina.

---

## 3. Uso do símbolo `[VAZIO]` (Épsilon)

**O que é:**
Nas regras de produção que regem blocos de controle (como `<lista_comandos_bloco>`), implementamos o símbolo terminal `[VAZIO]` indicando o encerramento da derivação quando o parser encontra um `RPAREN`.

**Por que:**
Isso nos permite ter "blocos opcionais" ou que sejam ecerrados mais cedo. É a clássica técnica de recursão de cauda da teoria de compiladores, que previne o parser de esperar infinitamente por um token de preenchimento onde não é necessário.

---

## 4. Gramática Mapeada para Dicionário 2D

**O que é:**
A tabela LL(1) entregue por `construirTabelaLL1()` no `gramatica.py` é um dicionário onde a chave primária é o Não-Terminal, a chave secundária é o Terminal (Token de Entrada), e o valor é a Produção de Regra correspondente.

**Por que:**
Para facilitar a integração com a Mari (Aluno 2). Esse formato O(1) de acesso permite que ela faça algo simples como `tabela[nao_terminal_atual][token_atual]` e receba perfeitamente a lista de derivação que ela precisa empilhar.