# Analisador Sintático e Gerador de Assembly (Fase 2)

**Instituição:** [Nome da Instituição]  
**Ano:** 2026  
**Disciplina:** Compiladores  
**Professor:** [Nome do Professor]  

## 👥 Integrantes do Grupo (RA2-18)
* Dani Heart Basso - [@dani-heart](https://github.com/dani-heart)
* Mariana Alves da Silva - [@himarialves](https://github.com/himarialves)

---

## 🚀 Instruções para Compilar, Executar e Depurar

Nosso compilador foi desenvolvido inteiramente em **Python 3**. Ele não requer passos complexos de build, apenas a execução do script principal passando o arquivo fonte como argumento.

**Para Executar:**
```bash
# No terminal, dentro da pasta RA2_18, rode:
python main.py testes1.txt
```
*Nota: Opcionalmente, você pode testar `testes2.txt` ou `testes3.txt`.*

**Saídas Geradas:**
1. `saida.asm`: O código Assembly ARMv7 gerado.
2. `arvore_sintatica.json`: A representação da árvore gerada em formato JSON.

**Para Testar (Depurar):**
Para rodar nossa suíte de testes automatizados (Lexer e Parser):
```bash
python -m pytest
```

---

## ⚙️ Sintaxe das Estruturas de Controle

Nossa linguagem utiliza **Notação Polonesa Reversa (RPN)** estrita. Para implementar blocos de repetição e tomada de decisão, introduzimos operadores relacionais (`>`, `<`, `==`, `!=`, `>=`, `<=`) e novas palavras reservadas.

Toda estrutura de controle segue o padrão geral da linguagem: `( [operando_esquerdo] [operando_direito] [operador] )`.

### 1. Tomada de Decisão (IF)
A estrutura `IF` avalia uma condição. Se for verdadeira (diferente de 0), o bloco de comandos interno é executado. A linguagem não possui `ELSE`.
**Sintaxe:** `( [condição_rpn] (LET [comandos...]) IF )`

**Exemplo prático:** 
*Se o valor armazenado em `VAR` for maior que 5, armazene 2 em `VAR`.*
```lisp
( ((VAR) 5 >) (LET (2 VAR)) IF )
```

### 2. Laço de Repetição (WHILE)
A estrutura `WHILE` repete o bloco de comandos interno enquanto a condição for verdadeira.
**Sintaxe:** `( [condição_rpn] (LET [comandos...]) WHILE )`

**Exemplo prático:**
*Enquanto `CONT` for igual a 1, armazene 0 em `CONT` (loop executará apenas uma vez).*
```lisp
( ((CONT) 1 ==) (LET (0 CONT) ) WHILE )
```