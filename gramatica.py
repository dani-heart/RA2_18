# Integrantes do grupo:
# Dani Heart Basso - @dani-heart
# Mariana Alves da Silva - @himarialves
#
# Nome do grupo no Canvas: RA1-18

## CONSTRUIR GRAMÁTICA
# Essa função retorna a gramática livre de contexto, como um dicionário
# Chaves são Não-Terminais
# Valores são listas de produção (As regrinhas)
# O projeto é para uma gramática LL(1), no caso, só olha 1 à frente
# Usa fatoração à esquerda em não terminais, em (LPAREN), já que muitos caminhos poderiam começar com (
# [VAZIO] representa ε e indica uma produção vazia, para permitir que blocos sejam opcionais
def construirGramatica(): 
   
    gramatica = {
        # O programa global exige (START) no início. 
        # Em seguida, chama a lista de comandos que processará até achar o (END)
        "<programa>": [
            ["LPAREN", "START", "RPAREN", "<lista_comandos_globais>"]
        ],

        # Fatoração à esquerda, para evitar conflitos quando lê (
        # Todas as linhas de comando começam consumindo um parentesis e jogando a decisão pra frente
        "<lista_comandos_globais>": [
            ["LPAREN", "<conteudo_global>"]
        ],

        # Aqui "Decidimos" se é o fim do programa (END) ou um comando executável
        "<conteudo_global>": [
            ["END", "RPAREN"],
            ["<conteudo_comando>", "RPAREN", "<lista_comandos_globais>"]
        ],

        # Utilizado para comandos como IF/WHILE
        # Pode estar VAZIO no fim do bloco
        "<lista_comandos_bloco>": [
            ["LPAREN", "<conteudo_comando>", "RPAREN", "<lista_comandos_bloco>"],
            ["[VAZIO]"]
        ],
 
        # Esse bloco é complicado:
        # NUM_INT ou NUM_REAL pode ser parte de: Operação, Memória, ou Resultado Histórico
        # MEM sem ação significa que está puxando o valor
        # LPAREN indica uma expressão com parentesis ou estrutura de controle
        "<conteudo_comando>": [
            ["NUM_INT", "<acao_numero>"], # Numero pode ser uma conta, guardar valor através de MEM ou histórico (KEYWORD_RES)
            ["NUM_REAL", "<acao_numero>"], # Mesma coisa para REAL
            ["MEM"],
            ["LPAREN", "<conteudo_par>", "RPAREN", "<acao_pos_par>"] # Isso é para parentesis dentro de parentesis.  
        ],

        # Define a ação tomada depois de um token numerico ou outra expressão
        # KEYWORD_RES: Resultado do histórico
        # MEM: Guarda o valor na variável com esse ID
        # <Operando> <Operador>: Expressão matemática
        "<acao_numero>": [
            ["KEYWORD_RES"],
            ["MEM"],
            ["<operando>", "<operador>"]
        ],

        # PASSTHROUGH: Redireciona diretamente para <Expressao>.
        # Mantido na gramática para deixar a arquitetura aberta para futuras 
        # expansões do que pode existir dentro de blocos isolados de parênteses.
        "<conteudo_par>": [
            ["<expressao>"]
        ],

        # Determina o que acontece depois de fechar um parentesis
        # Pode ser desde um número para uma operação, ou um LPAREN (Que indica uma estrutura mais complexa)
        "<acao_pos_par>": [
            ["NUM_INT", "<operador>"], # Pode ser um inteiro
            ["NUM_REAL", "<operador>"], # Um real
            ["LPAREN", "<conteudo_pos_par_lparen>"] # Esse operando abre um parentesis, então pode ser uma conta ou IF/WHILE
        ],
 
        # Só sabemos se é uma conta ao ler o primeiro token dentro do parentesis, então usamos KEYWORD_LET
        # Se KEYWORD_LET é encontrado, é um bloco de controle (IF/WHILE)
        # Se não, é um operando matemático
        "<conteudo_pos_par_lparen>": [
            ["KEYWORD_LET", "<lista_comandos_bloco>", "RPAREN", "<controle>"], # Achou KEYWORD_LET? Controle
            ["<conteudo_operando>", "RPAREN", "<operador>"] 
        ],

        ## A partir daqui temos operações bem mais simples

        # Representa as palavras possíveis de controle, usadas acima
        "<controle>": [
            ["IF"],
            ["WHILE"]
        ],

        # Literalmente a definição de RPN: Expressão, Expressão, Operando
        "<expressao>": [
            ["<operando>", "<operando>", "<operador>"]
        ],

        # Define o que podem ser os tais operandos
        "<operando>": [
            ["NUM_INT"],
            ["NUM_REAL"],
            ["LPAREN", "<conteudo_operando>", "RPAREN"]
        ],

        # Define o que pode estar dentro do parentesis: MEM ou outra expressão
        "<conteudo_operando>": [
            ["MEM"],
            ["<expressao>"]
        ],

        # Todos os operadores suportados. Mais detalhes em Anotações.md e EBNF.md
        "<operador>": [
            ["OP_SOMA"], ["OP_SUB"], ["OP_MULT"], ["OP_DIV_INT"], ["OP_DIV_REAL"], 
            ["OP_MOD"], ["OP_POT"], ["OP_MAIOR"], ["OP_MENOR"], ["OP_IGUAL"], 
            ["OP_DIF"], ["OP_MAIOR_IGUAL"], ["OP_MENOR_IGUAL"]
        ]
    }
    return gramatica

## CALCULAR FIRST
# Retorna os firsts
# Um first representa os conjuntos de tokens terminais que podem ser derivados de um não-terminal

#COMO FUNCIONA UM FIRST SET
#-> Para um Terminal (t): FIRST(t) = {t}
#-> Para um Não Terminal A: (Complexo)
#---> Se A -> [VAZIO] é uma produção, então [VAZIO] está em FIRST(A)
#---> Se A -> X1 X2 X3... é uma pdrodução
#-----> Adicionar todos os terminais de FIRST (X1) a FIRST(A) (Tirando o [VAZIO])
#-----> Se VAZIO está em FIRST (X1), então adicione todos os terminais de FIRST (X2) à FIRST (A) (Novamente, tirando [VAZIO])
#-----> Continuar o processo enquanto tiver [VAZIO] em não-First

#Nessa implementação os conjuntos FIRST são pré calculados e codificados diretamente
#Em um parser automático esses conjuntos seriam gerados a partir das regras de construirGramatica()
def calcularFirst():

    first = {
        "<programa>": {"LPAREN"},
        "<lista_comandos_globais>": {"LPAREN"},
        "<conteudo_global>": {"END", "NUM_INT", "NUM_REAL", "MEM", "LPAREN"},
        "<lista_comandos_bloco>": {"LPAREN", "[VAZIO]"},
        "<conteudo_comando>": {"NUM_INT", "NUM_REAL", "MEM", "LPAREN"},
        "<acao_numero>": {"KEYWORD_RES", "MEM", "NUM_INT", "NUM_REAL", "LPAREN"},
        "<conteudo_par>": {"NUM_INT", "NUM_REAL", "LPAREN"},
        "<acao_pos_par>": {"NUM_INT", "NUM_REAL", "LPAREN"},
        "<conteudo_pos_par_lparen>": {"KEYWORD_LET", "MEM", "NUM_INT", "NUM_REAL", "LPAREN"},
        "<controle>": {"IF", "WHILE"},
        "<expressao>": {"NUM_INT", "NUM_REAL", "LPAREN"},
        "<operando>": {"NUM_INT", "NUM_REAL", "LPAREN"},
        "<conteudo_operando>": {"MEM", "NUM_INT", "NUM_REAL", "LPAREN"},
        "<operador>": {"OP_SOMA", "OP_SUB", "OP_MULT", "OP_DIV_INT", "OP_DIV_REAL", 
                       "OP_MOD", "OP_POT", "OP_MAIOR", "OP_MENOR", "OP_IGUAL", 
                       "OP_DIF", "OP_MAIOR_IGUAL", "OP_MENOR_IGUAL"}
    }
    return first

## CALCULAR FOLLOW
# Retorna os conjuntos Follow

#Como funciona Follow:
#   1) Para o simbolo inícial S: Adiciona $ a FOLLOW(S)
#   2) Para cada produção A -> \alpha B \beta onde B não é terminal
#       Adicione todos os terminais de FIRST(\beta) à Follow(B) (Tirando [VAZIO])
#       Se tiver [VAZIO] em FIRST(\beta), então adicione todos os terminais de FOLLOW(A) e FOLLOW(B)
#   3) Para cada produção A -> \alphaB : (B não sendo terminal)
#       Adicione todos os terminais de FOLLOW(A) a FOLLOW(B)

#Repetir passos 2 e 3 até que nenhum terminal novo possa ser adicionado a nenhum FOLLOW

#Assim como em calcularFirst(), os conjuntos FOLLOW são pré calculados e codificados
#Especialmente importantes para construir a tabela LL(1)
def calcularFollow():

    follow = {
        "<programa>": {"$"},
        "<lista_comandos_globais>": {"$"},
        "<conteudo_global>": {"$"},
        "<lista_comandos_bloco>": {"RPAREN"},
        "<conteudo_comando>": {"RPAREN"},
        "<acao_numero>": {"RPAREN"},
        "<conteudo_par>": {"RPAREN"},
        "<acao_pos_par>": {"RPAREN"},
        "<conteudo_pos_par_lparen>": {"RPAREN"},
        "<controle>": {"RPAREN"},
        "<expressao>": {"RPAREN"},
        "<operando>": {"NUM_INT", "NUM_REAL", "LPAREN", "OP_SOMA", "OP_SUB", "OP_MULT", "OP_DIV_INT", "OP_DIV_REAL", "OP_MOD", "OP_POT", "OP_MAIOR", "OP_MENOR", "OP_IGUAL", "OP_DIF", "OP_MAIOR_IGUAL", "OP_MENOR_IGUAL"},
        "<conteudo_operando>": {"RPAREN"},
        "<operador>": {"RPAREN"}
    }
    return follow

## CONSTRUIR TABELA LL1
# Uma gramática é LL(1) se cada célula da tabela M[A,a] tiver no máximo uma produção
def construirTabelaLL1():

    tabela = {
        "<programa>": {
            "LPAREN": ["LPAREN", "START", "RPAREN", "<lista_comandos_globais>"]
        },
        "<lista_comandos_globais>": {
            "LPAREN": ["LPAREN", "<conteudo_global>"]
        },
        "<conteudo_global>": {
            "END": ["END", "RPAREN"],
            "NUM_INT": ["<conteudo_comando>", "RPAREN", "<lista_comandos_globais>"],
            "NUM_REAL": ["<conteudo_comando>", "RPAREN", "<lista_comandos_globais>"],
            "MEM": ["<conteudo_comando>", "RPAREN", "<lista_comandos_globais>"],
            "LPAREN": ["<conteudo_comando>", "RPAREN", "<lista_comandos_globais>"]
        },
        "<lista_comandos_bloco>": {
            "LPAREN": ["LPAREN", "<conteudo_comando>", "RPAREN", "<lista_comandos_bloco>"],
            "RPAREN": ["[VAZIO]"]
        },
        "<conteudo_comando>": {
            "NUM_INT": ["NUM_INT", "<acao_numero>"],
            "NUM_REAL": ["NUM_REAL", "<acao_numero>"],
            "MEM": ["MEM"],
            "LPAREN": ["LPAREN", "<conteudo_par>", "RPAREN", "<acao_pos_par>"]
        },
        "<acao_numero>": {
            "KEYWORD_RES": ["KEYWORD_RES"],
            "MEM": ["MEM"],
            "NUM_INT": ["<operando>", "<operador>"],
            "NUM_REAL": ["<operando>", "<operador>"],
            "LPAREN": ["<operando>", "<operador>"]
        },
        "<conteudo_par>": {
            "NUM_INT": ["<expressao>"],
            "NUM_REAL": ["<expressao>"],
            "LPAREN": ["<expressao>"]
        },
        "<acao_pos_par>": {
            "NUM_INT": ["NUM_INT", "<operador>"],
            "NUM_REAL": ["NUM_REAL", "<operador>"],
            "LPAREN": ["LPAREN", "<conteudo_pos_par_lparen>"]
        },
        "<conteudo_pos_par_lparen>": {
            "KEYWORD_LET": ["KEYWORD_LET", "<lista_comandos_bloco>", "RPAREN", "<controle>"],
            "MEM": ["<conteudo_operando>", "RPAREN", "<operador>"],
            "NUM_INT": ["<conteudo_operando>", "RPAREN", "<operador>"],
            "NUM_REAL": ["<conteudo_operando>", "RPAREN", "<operador>"],
            "LPAREN": ["<conteudo_operando>", "RPAREN", "<operador>"]
        },
        "<controle>": {
            "IF": ["IF"],
            "WHILE": ["WHILE"]
        },
        "<expressao>": {
            "NUM_INT": ["<operando>", "<operando>", "<operador>"],
            "NUM_REAL": ["<operando>", "<operando>", "<operador>"],
            "LPAREN": ["<operando>", "<operando>", "<operador>"]
        },
        "<operando>": {
            "NUM_INT": ["NUM_INT"],
            "NUM_REAL": ["NUM_REAL"],
            "LPAREN": ["LPAREN", "<conteudo_operando>", "RPAREN"]
        },
        "<conteudo_operando>": {
            "MEM": ["MEM"],
            "NUM_INT": ["<expressao>"],
            "NUM_REAL": ["<expressao>"],
            "LPAREN": ["<expressao>"]
        },
        "<operador>": {
            "OP_SOMA": ["OP_SOMA"], "OP_SUB": ["OP_SUB"], "OP_MULT": ["OP_MULT"], "OP_DIV_INT": ["OP_DIV_INT"], 
            "OP_DIV_REAL": ["OP_DIV_REAL"], "OP_MOD": ["OP_MOD"], "OP_POT": ["OP_POT"], 
            "OP_MAIOR": ["OP_MAIOR"], "OP_MENOR": ["OP_MENOR"], "OP_IGUAL": ["OP_IGUAL"], 
            "OP_DIF": ["OP_DIF"], "OP_MAIOR_IGUAL": ["OP_MAIOR_IGUAL"], "OP_MENOR_IGUAL": ["OP_MENOR_IGUAL"]
        }
    }
    return tabela
