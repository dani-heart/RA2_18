**Responsável:** Dani Heart Basso

## Tarefas

- Definir e implementar a sintaxe para a estrutura de decisão e repetição em notação pós-fixada
- Criar tokens especiais para estruturas de controle
- Documentar a sintaxe das novas estruturas
- Validar e testar o código Assembly gerado

---

### Decisões de Arquitetura

## 1. Manutenção Estrita do RPN (Notação Polonesa Reversa)

**O que é:**
As estruturas de controle foram desenhadas para que a keyword principal (`IF` ou `WHILE`) seja o **último** token do comando, respeitando a regra base da linguagem. 
Exemplo: `( [condição] [bloco] IF )`.

**Por que:**
Isso evita quebrar a lógica do Parser e mantém a homogeneidade conceitual da linguagem. Se adotássemos `(IF [condição] [bloco])`, estaríamos criando uma regra prefixada em um ecossistema inteiramente pós-fixado.

---

## 2. Adoção da keyword `LET` para encapsulamento de blocos

**O que é:**
Todo bloco de comandos que pertence a uma estrutura de controle deve ser abraçado por `(LET ...)`.
Exemplo: `(LET (2 VAR) (3 RES) )`

**Por que:**
Como o Parser Descendente Recursivo LL(1) olha apenas um token à frente, ele teria dificuldade de diferenciar onde termina a condição do IF e onde começam os comandos internos, visto que tudo está entre parênteses. A introdução da palavra reservada `LET` atua como um "sinalizador de escopo", facilitando muito o roteamento no Parser.

---

## 3. Ausência de instrução `ELSE`

**O que é:**
A linguagem fornece apenas a estrutura condicional `IF` simples (ramo verdadeiro).

**Por que:**
Em RPN rigoroso, o gerenciamento de dois escopos na mesma diretriz `( [condicao] [bloco_if] [bloco_else] IF )` exigiria um empilhamento complexo no assembly e no próprio parser. Como a linguagem é simplificada e não possui variáveis booleanas nativas, adotamos a regra de que lógicas divergentes devem ser tratadas com lógicas sequenciais opostas (ex: usar um IF para `A > B` e outro para `A <= B`).