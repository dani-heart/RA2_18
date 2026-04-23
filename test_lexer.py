import pytest
from lexer import _classificar_token, lerTokens, Token

# ---------------------------------------------------------------------------
# Caminho Feliz — Classificação de Tokens Individuais
# ---------------------------------------------------------------------------

def test_classificar_inteiros_e_reais():
    # Testando inteiros (positivos e negativos)
    tok_int = _classificar_token("42", 1)
    assert tok_int.tipo == "NUM_INT"
    assert tok_int.valor == "42"
    
    tok_int_neg = _classificar_token("-7", 1)
    assert tok_int_neg.tipo == "NUM_INT"
    
    # Testando reais
    tok_real = _classificar_token("3.1415", 2)
    assert tok_real.tipo == "NUM_REAL"
    
    tok_real_neg = _classificar_token("-0.5", 2)
    assert tok_real_neg.tipo == "NUM_REAL"

def test_classificar_variaveis_memoria():
    # Apenas maiúsculas
    tok_mem = _classificar_token("MINHAVARIAVEL", 3)
    assert tok_mem.tipo == "MEM"
    assert tok_mem.valor == "MINHAVARIAVEL"

    # Variável de uma letra só
    tok_mem_uma_letra = _classificar_token("X", 1)
    assert tok_mem_uma_letra.tipo == "MEM"

def test_classificar_palavras_chave_controle():
    assert _classificar_token("WHILE", 1).tipo == "WHILE"
    assert _classificar_token("IF", 1).tipo == "IF"
    assert _classificar_token("LET", 1).tipo == "KEYWORD_LET"
    assert _classificar_token("RES", 1).tipo == "KEYWORD_RES"

def test_classificar_operadores():
    # Matemáticos
    assert _classificar_token("+", 1).tipo == "OP_SOMA"
    assert _classificar_token("-", 1).tipo == "OP_SUB"
    assert _classificar_token("*", 1).tipo == "OP_MULT"
    assert _classificar_token("/", 1).tipo == "OP_DIV_INT"
    assert _classificar_token("^", 1).tipo == "OP_POT"
    assert _classificar_token("|", 1).tipo == "OP_DIV_REAL"
    assert _classificar_token("%", 1).tipo == "OP_MOD"
    
    # Relacionais
    assert _classificar_token("<", 1).tipo == "OP_MENOR"
    assert _classificar_token(">", 1).tipo == "OP_MAIOR"
    assert _classificar_token("==", 1).tipo == "OP_IGUAL"
    assert _classificar_token(">=", 1).tipo == "OP_MAIOR_IGUAL"
    assert _classificar_token("<=", 1).tipo == "OP_MENOR_IGUAL"
    assert _classificar_token("!=", 1).tipo == "OP_DIF"

def test_classificar_estrutura():
    # Parenteses e delimitadores globais
    assert _classificar_token("(", 1).tipo == "LPAREN"
    assert _classificar_token(")", 1).tipo == "RPAREN"
    assert _classificar_token("START", 1).tipo == "START"
    assert _classificar_token("END", 1).tipo == "END"

# ---------------------------------------------------------------------------
# Caminho Feliz — Leitura de Arquivos (lerTokens)
# ---------------------------------------------------------------------------

def test_ler_tokens_arquivo_completo(tmp_path):
    # tmp_path é uma 'fixture' do pytest. Ele cria uma pasta virtual temporária no SO.
    # Isso é ótimo porque não sujamos o projeto com arquivos de teste de verdade.
    arquivo_teste = tmp_path / "teste_lexico.txt"
    
    # Simulando o código-fonte de um programa real da nossa linguagem
    conteudo = """
    (10 20 +)
    ( ((VAR) 5 >) (LET (2 VAR)) IF )
    """
    arquivo_teste.write_text(conteudo, encoding="utf-8")
    
    tokens = lerTokens(str(arquivo_teste))
    
    # Verificando a sequência gerada (ignorou os espaços e separou os parênteses)
    assert len(tokens) == 22
    assert tokens[0].tipo == "LPAREN"
    assert tokens[1].tipo == "NUM_INT"
    assert tokens[1].valor == "10"
    
    # Verificando as estruturas de controle na segunda linha do código (linha 2 no token)
    assert tokens[20].tipo == "IF"
    assert tokens[21].tipo == "RPAREN"
    assert tokens[21].linha == 3

def test_ler_tokens_linhas_vazias_ignoradas(tmp_path):
    # Testar se espaços e quebras de linha são devidamente ignorados
    arquivo_teste = tmp_path / "teste_vazios.txt"
    arquivo_teste.write_text("(START)\n\n\n(END)\n", encoding="utf-8")
    
    tokens = lerTokens(str(arquivo_teste))
    assert len(tokens) == 6  # 3 tokens pra (START), 3 pra (END)

def test_ler_tokens_numero_de_linha_correto(tmp_path):
    # Valida se os tokens guardam a linha certa em que apareceram no código
    arquivo_teste = tmp_path / "teste_linhas.txt"
    arquivo_teste.write_text("(START)\n(3 4 +)\n(END)\n", encoding="utf-8")
    
    tokens = lerTokens(str(arquivo_teste))
    start = next(t for t in tokens if t.tipo == "START")
    assert start.linha == 1
    soma = next(t for t in tokens if t.tipo == "OP_SOMA")
    assert soma.linha == 2

def test_ler_tokens_arquivos_projeto():
    # Testa os arquivos oficiais do projeto que estão na raiz da pasta
    tokens1 = lerTokens("testes1.txt")
    tipos1 = [t.tipo for t in tokens1]
    assert "START" in tipos1 and "END" in tipos1
    assert "IF" in tipos1 and "WHILE" in tipos1
    
    tokens2 = lerTokens("testes2.txt")
    assert "START" in [t.tipo for t in tokens2]

    tokens3 = lerTokens("testes3.txt")
    assert "END" in [t.tipo for t in tokens3]

# ---------------------------------------------------------------------------
# Caminho Triste — Entradas Inválidas e Erros Léxicos
# ---------------------------------------------------------------------------

def test_erro_lexico_caractere_invalido():
    # Garantir que o lixo trava o compilador na hora
    # pytest.raises captura a exceção esperada. Se o código NÃO der erro, o teste falha.
    with pytest.raises(ValueError) as exc:
        _classificar_token("@", 5)
    
    # A mensagem DEVE conter a linha e o caractere (exigência de robustez do professor)
    assert "Erro léxico na linha 5" in str(exc.value)
    assert "@" in str(exc.value)

def test_erro_lexico_variavel_minuscula():
    # Variáveis só podem ser maiúsculas
    with pytest.raises(ValueError, match="Erro léxico"):
        _classificar_token("var", 3)

def test_erro_lexico_variavel_mista():
    # Letras misturadas com números não são aceitas
    with pytest.raises(ValueError, match="Erro léxico"):
        _classificar_token("Var1", 2)

def test_ler_tokens_arquivo_inexistente():
    # Testa se o programa reage bem quando o usuário digita o nome do arquivo errado no terminal.
    with pytest.raises(FileNotFoundError):
        lerTokens("arquivo_que_nao_existe.txt")

def test_ler_tokens_erro_lexico_no_arquivo(tmp_path):
    # Valida se o lerTokens repassa o erro léxico corretamente quando encontra lixo no arquivo
    arquivo_teste = tmp_path / "teste_erro.txt"
    arquivo_teste.write_text("(START)\n(@ 3 +)\n(END)\n", encoding="utf-8")
    
    with pytest.raises(ValueError, match="Erro léxico"):
        lerTokens(str(arquivo_teste))