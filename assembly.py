# Integrantes do grupo (ordem alfabética):
# Dani Heart Basso - @dani-heart
# Mariana Alves da Silva - @himarialves
#
# Nome do grupo no Canvas: RA2-18


from arvore import No


# Convenções do gerador

# - Toda expressão inteira deixa resultado em R0.
# - Toda expressão real deixa resultado em D0 (VFP double-precision, 64 bits).
# - F64 é obrigatório .
# - Pilha de software: usa SP real (R13) com PUSH/POP e VPUSH/VPOP.
#   Reais usam VPUSH {D0} / VPOP {D1} (8 bytes cada).
# - Variáveis MEM: alocadas na seção .data, uma word por variável.
# - Histórico RES: array de words em .data (RES_HIST), índice em RES_IDX.
# - Constantes float: coletadas em pré-passo, emitidas como labels .double em .data.
# - Inteiro vs Real: um nó EXPR é real se QUALQUER operando descendente
#   contiver '.' no valor; caso contrário é inteiro.
# - Operador ^ (potência): implementado como loop de multiplicação (confirmado por exp anterior).
# - Operador | (divisão real): VDIV não funciona no CPulator DEC1-SOC (confirmado por exp anterior).
#   Implementado como loop de subtração. Resultado é inteiro truncado.
# - Histórico RES: salvo SOMENTE para comandos de topo de programa
#   (não para expressões usadas como condição em IF/WHILE).

# Contador global de labels. Resetado em gerarAssembly() a cada chamada,
# garantindo que o arquivo gerado sempre comece em L_1, L_2, ...
# Global (não instância) porque o gerador não é uma classe — são funções puras.
_label_count = 0


def _novo_label(prefixo: str = "L") -> str:
    # Sem esse contador, dois IFs no mesmo programa gerariam IF_FIM duplicado,
    # quebrando o assembler (labels duplicados são erro de montagem no CPulator).
    global _label_count
    _label_count += 1
    return f"{prefixo}_{_label_count}"


def _coletar_mem_ids(no: No, vistos: set[str]) -> None:
    # set garante deduplicação: se VAR aparece 10 vezes no código,
    # geramos apenas uma entrada "VAR: .word 0" na seção .data.
    if no.tipo == "MEM_ID" and no.valor is not None:
        vistos.add(no.valor)
    for filho in no.filhos:
        _coletar_mem_ids(filho, vistos)


def _coletar_floats(no: No, floats: dict[str, str]) -> None:
    # Label: '.' → '_' e '-' → 'N' para criar identificadores válidos em assembly.
    # Ex: "3.14" → "FC_3_14", "-1.5" → "FC_N1_5".
    # dict por label (não por valor) garante que o mesmo literal não gere duas entradas.
    if no.tipo == "OPERANDO" and no.valor is not None and "." in no.valor:
        label = f"FC_{no.valor.replace('.', '_').replace('-', 'N')}"
        floats[label] = no.valor
    for filho in no.filhos:
        _coletar_floats(filho, floats)


def _e_real(no: No) -> bool:
    # Verifica TODOS os descendentes porque a linguagem não tem declaração de tipo:
    # o tipo da expressão inteira é inferido — se qualquer operando tem '.', é real.
    # MEM_ID é tratado como inteiro (variáveis armazenam words de 32 bits).
    if no.tipo == "OPERANDO" and no.valor is not None and "." in no.valor:
        return True
    if no.tipo == "MEM_ID":
        return False
    return any(_e_real(f) for f in no.filhos)


# Mapa global de float label -> valor (preenchido em gerarAssembly)
_float_labels: dict[str, str] = {}


def _label_para_float(val: str) -> str:
    """Retorna o label .data correspondente a um literal float."""
    label = f"FC_{val.replace('.', '_').replace('-', 'N')}"
    return label

# Geração de código por tipo de nó

def _gerar_programa(no: No) -> str:
    """Emite seção .text, header e itera sobre filhos."""
    linhas: list[str] = []

    linhas.append(".text")
    linhas.append("@ Assembly ARMv7 gerado automaticamente — RA2-18")
    linhas.append("@ Plataforma: CPulator ARMv7 DEC1-SOC v16.1")
    linhas.append("")
    linhas.append(".global _start")
    linhas.append("_start:")
    linhas.append("")

    # CPulator ARMv7 bare-metal não inicializa SP automaticamente.
    # Sem isso, qualquer PUSH/POP lê/escreve endereço 0x0 e corrompe o programa -> confirmado em exp anterior
    # entao inicializamos o stack pointer.

    linhas.append("    @ Inicializa stack pointer")
    linhas.append("    LDR SP, =STACK_TOP")
    linhas.append("")

    # FPEXC bit 30 (EN) precisa ser 1 para habilitar o coprocessador VFP.
    # Sem isso, qualquer instrução VLDR/VADD/VCVT gera undefined instruction fault.
    # novamente, erro confirmado por exp anterior. 
    linhas.append("    @ Habilita coprocessador VFP")
    linhas.append("    LDR R0, =0x40000000")
    linhas.append("    FMXR FPEXC, R0")
    linhas.append("")

    # Inicializa RES_IDX em zero. Cada entrada ocupa 8 bytes (F64) — índice, não byte offset.
    linhas.append("    @ Inicializa indice do historico RES (entradas de 8 bytes)")
    linhas.append("    LDR R4, =RES_IDX")
    linhas.append("    MOV R5, #0")
    linhas.append("    STR R5, [R4]")
    linhas.append("")

    # Gera código para cada comando de topo do programa (salva no histórico)
    for filho in no.filhos:
        linhas.append(_gerar_cmd_topo(filho))
        linhas.append("")

    # Epilogo
    # finalizamos em B por exp anterior tambem -> quando terminavamos com pop tambem davaa erro. 
    # tentamos muitas opcoes no PJBL1 com push e pop, e thumb. Thumb nao é suportado pelo CPulator ARMv7, pop estoura SP.
    linhas.append("_end:")
    linhas.append("    B _end")
    linhas.append("")

    return "\n".join(linhas)


def _gerar_cmd_topo(no: No) -> str:
    # Só EXPR produz um valor numérico que vai para o histórico RES.
    # Comandos como CMD_MEM_STORE, CMD_MEM_LOAD, IF, WHILE executam efeitos colaterais
    # mas não produzem um "resultado" que (N RES) deveria recuperar.
    if no.tipo == "EXPR":
        linhas = [_gerar_expr(no, salvar_res=True)]
        return "\n".join(linhas)
    else:
        return _gerar_no(no)


def _gerar_no(no: No) -> str:
    # PROGRAMA nunca chega aqui — é tratado diretamente em gerarAssembly.
    # OP não gera instrução própria: é filho de EXPR e consumido por _gerar_op_int/real.
    if no.tipo == "PROGRAMA":
        raise ValueError("_gerar_no nao deve receber PROGRAMA diretamente.")
    elif no.tipo == "EXPR":
        # EXPR dentro de bloco IF/WHILE não salva no histórico RES.
        return _gerar_expr(no, salvar_res=False)
    elif no.tipo == "OPERANDO":
        return _gerar_operando_int(no)
    elif no.tipo == "MEM_ID":
        return _gerar_mem_load(no)
    elif no.tipo == "CMD_MEM_STORE":
        return _gerar_cmd_mem_store(no)
    elif no.tipo == "CMD_MEM_LOAD":
        return _gerar_cmd_mem_load(no)
    elif no.tipo == "CMD_RES":
        return _gerar_cmd_res(no)
    elif no.tipo == "IF":
        return _gerar_if(no)
    elif no.tipo == "WHILE":
        return _gerar_while(no)
    elif no.tipo == "BLOCO":
        return _gerar_bloco(no)
    elif no.tipo == "OP":
        return f"    @ OP {no.valor}"
    else:
        return f"    @ [no desconhecido: {no.tipo}]"


def _gerar_operando_int(no: No) -> str:
    if no.tipo == "OPERANDO":
        val = no.valor or "0"
        ival = int(val)
        # MOV aceita imediato de 8 bits (0–255) na codificação ARMv7.
        # Para valores maiores, LDR com literal pool (=valor) é a alternativa portável.
        if 0 <= ival <= 255:
            return f"    MOV R0, #{ival}  @ operando {val}"
        else:
            return f"    LDR R0, ={ival}  @ operando {val}"
    elif no.tipo == "MEM_ID":
        return _gerar_mem_load(no)
    elif no.tipo == "EXPR":
        return _gerar_expr(no, salvar_res=False)
    else:
        return f"    @ operando int desconhecido: {no.tipo}"


def _gerar_operando_real_em_d0(no: No) -> str:
    if no.tipo == "OPERANDO":
        val = no.valor or "0.0"
        if "." in val:
            # Constante double: VLDR D0 carrega 8 bytes do label .double em .data.
            label = _label_para_float(val)
            return f"    VLDR D0, {label}  @ operando real {val}"
        else:
            # Inteiro em contexto real: carrega em R0, move para S0 (32-bit),
            # depois VCVT.F64.S32 promove S32 -> D0 (F64).
            ival = int(val)
            if 0 <= ival <= 255:
                return (
                    f"    MOV R0, #{ival}\n"
                    f"    VMOV S0, R0\n"
                    f"    VCVT.F64.S32 D0, S0"
                )
            else:
                return (
                    f"    LDR R0, ={ival}\n"
                    f"    VMOV S0, R0\n"
                    f"    VCVT.F64.S32 D0, S0"
                )
    elif no.tipo == "MEM_ID":
        # Variável armazena word inteira de 32 bits; promove para F64 ao carregar.
        nome = no.valor or "?"
        return (
            f"    LDR R1, ={nome}\n"
            f"    LDR R0, [R1]\n"
            f"    VMOV S0, R0\n"
            f"    VCVT.F64.S32 D0, S0"
        )
    elif no.tipo == "EXPR":
        return _gerar_expr(no, salvar_res=False)
    else:
        return f"    @ operando real desconhecido: {no.tipo}"


def _gerar_mem_load(no: No) -> str:
    # Dois passos: LDR R1 carrega o endereço do label; LDR R0 carrega o valor naquele endereço.
    # Não é possível fazer "LDR R0, =VAR" e já ter o valor — isso carregaria o ponteiro.
    nome = no.valor or "?"
    return (
        f"    @ carregar MEM {nome}\n"
        f"    LDR R1, ={nome}\n"
        f"    LDR R0, [R1]"
    )


def _gerar_expr(no: No, salvar_res: bool) -> str:
    op_esq, op_dir, op_no = no.filhos[0], no.filhos[1], no.filhos[2]
    op = op_no.valor or "?"
    real = _e_real(no)

    linhas: list[str] = [f"    @ EXPR {op} ({'real' if real else 'int'})"]

    if real:
        # Padrão avalia-esq → empilha → avalia-dir → desempilha-em-D1 → opera.
        # D0 é o resultado; D1 recebe o esq depois do POP.
        # VPUSH {D0} empilha 8 bytes (double); VPOP {D1} desempilha em D1.
        linhas.append(_gerar_operando_real_em_d0(op_esq))
        linhas.append("    @ empilha D0 (operando esq, 8 bytes)")
        linhas.append("    VPUSH {D0}")
        linhas.append(_gerar_operando_real_em_d0(op_dir))
        linhas.append("    @ desempilha operando esq em D1")
        linhas.append("    VPOP {D1}")
        linhas.append(_gerar_op_real(op))
        if salvar_res:
            # D0 já é F64 — VSTR salva 8 bytes sem truncar.
            # LSL #3 porque cada entrada ocupa 8 bytes (índice × 8).
            linhas.append("    @ salva resultado F64 no historico (8 bytes, sem truncar)")
            linhas.append("    LDR R3, =RES_IDX")
            linhas.append("    LDR R2, [R3]")
            linhas.append("    LDR R4, =RES_HIST")
            linhas.append("    VSTR D0, [R4, R2, LSL #3]")
            linhas.append("    ADD R2, R2, #1")
            linhas.append("    STR R2, [R3]")
    else:
        # Mesmo padrão do real: avalia-esq -> PUSH → avalia-dir -> POP.
        # Após POP: R0=esq, R1=dir. _gerar_op_int opera nessa convenção.
        linhas.append(_gerar_operando_int(op_esq))
        linhas.append("    @ empilha R0 (operando esq)")
        linhas.append("    PUSH {R0}")
        linhas.append(_gerar_operando_int(op_dir))
        linhas.append("    MOV R1, R0  @ operando dir em R1")
        linhas.append("    @ desempilha operando esq em R0")
        linhas.append("    POP {R0}")
        linhas.append(_gerar_op_int(op))

        if salvar_res:
            # Inteiro: converte R0 para F64 antes de salvar — histórico uniforme em F64.
            # Assim CMD_RES sempre carrega F64 (VLDR D0) independente do tipo original.
            linhas.append("    @ converte resultado int -> F64 e salva no historico")
            linhas.append("    VMOV S0, R0")
            linhas.append("    VCVT.F64.S32 D0, S0")
            linhas.append("    LDR R3, =RES_IDX")
            linhas.append("    LDR R2, [R3]")
            linhas.append("    LDR R4, =RES_HIST")
            linhas.append("    VSTR D0, [R4, R2, LSL #3]")
            linhas.append("    ADD R2, R2, #1")
            linhas.append("    STR R2, [R3]")

    return "\n".join(linhas)


def _gerar_op_int(op: str) -> str:
    if op == "+":
        return "    ADD R0, R0, R1"
    elif op == "-":
        return "    SUB R0, R0, R1"
    elif op == "*":
        return "    MUL R0, R0, R1"
    elif op == "/":
        return "    SDIV R0, R0, R1"
    elif op == "|":
        # VDIV.F32 não funciona no CPulator DEC1-SOC.
        # Alternativa: loop de subtração — conta quantas vezes R1 cabe em R0.
        # Resultado é inteiro (quociente), sem parte fracionária.
        label_loop = _novo_label("DIV_LOOP")
        label_fim = _novo_label("DIV_FIM")
        return (
            f"    @ divisao via loop de subtracao (VDIV nao suportado no CPulator)\n"
            f"    MOV R2, #0\n"
            f"{label_loop}:\n"
            f"    CMP R0, R1\n"
            f"    BLT {label_fim}\n"
            f"    SUB R0, R0, R1\n"
            f"    ADD R2, R2, #1\n"
            f"    B {label_loop}\n"
            f"{label_fim}:\n"
            f"    MOV R0, R2"
        )
    elif op == "%":
        # Fórmula: R0 mod R1 = R0 - (R0 / R1) * R1
        # ARMv7 não tem instrução de módulo — derivamos a partir de SDIV.
        return (
            "    MOV R6, R0\n"
            "    SDIV R0, R6, R1\n"
            "    MUL R0, R0, R1\n"
            "    SUB R0, R6, R0"
        )
    elif op == "^":
        # ARMv7 não tem instrução de potência. Implementamos como loop de multiplicação:
        # acumulador = 1, multiplica pela base expoente vezes. Funciona para inteiros >= 0.
        label_loop = _novo_label("POT_LOOP")
        label_fim = _novo_label("POT_FIM")
        return (
            f"    @ potencia R0^R1\n"
            f"    MOV R6, R0  @ base\n"
            f"    MOV R7, R1  @ expoente\n"
            f"    MOV R0, #1  @ acumulador\n"
            f"{label_loop}:\n"
            f"    CMP R7, #0\n"
            f"    BLE {label_fim}\n"
            f"    MUL R0, R0, R6\n"
            f"    SUB R7, R7, #1\n"
            f"    B {label_loop}\n"
            f"{label_fim}:"
        )
    elif op == ">":
        # Convenção booleana: 1 = verdadeiro, 0 = falso (mesma usada por IF/WHILE).
        # Padrão de todos os relacionais: CMP -> branch para ramo verdadeiro ->
        # falso emite MOV R0, #0 e pula para fim -> verdadeiro emite MOV R0, #1.
        lt, le = _novo_label("GT_T"), _novo_label("GT_E")
        return (
            f"    CMP R0, R1\n"
            f"    BGT {lt}\n"
            f"    MOV R0, #0\n"
            f"    B {le}\n"
            f"{lt}:\n"
            f"    MOV R0, #1\n"
            f"{le}:"
        )
    elif op == "<":
        lt, le = _novo_label("LT_T"), _novo_label("LT_E")
        return (
            f"    CMP R0, R1\n"
            f"    BLT {lt}\n"
            f"    MOV R0, #0\n"
            f"    B {le}\n"
            f"{lt}:\n"
            f"    MOV R0, #1\n"
            f"{le}:"
        )
    elif op == "==":
        lt, le = _novo_label("EQ_T"), _novo_label("EQ_E")
        return (
            f"    CMP R0, R1\n"
            f"    BEQ {lt}\n"
            f"    MOV R0, #0\n"
            f"    B {le}\n"
            f"{lt}:\n"
            f"    MOV R0, #1\n"
            f"{le}:"
        )
    elif op == "!=":
        lt, le = _novo_label("NE_T"), _novo_label("NE_E")
        return (
            f"    CMP R0, R1\n"
            f"    BNE {lt}\n"
            f"    MOV R0, #0\n"
            f"    B {le}\n"
            f"{lt}:\n"
            f"    MOV R0, #1\n"
            f"{le}:"
        )
    elif op == ">=":
        lt, le = _novo_label("GE_T"), _novo_label("GE_E")
        return (
            f"    CMP R0, R1\n"
            f"    BGE {lt}\n"
            f"    MOV R0, #0\n"
            f"    B {le}\n"
            f"{lt}:\n"
            f"    MOV R0, #1\n"
            f"{le}:"
        )
    elif op == "<=":
        lt, le = _novo_label("LE_T"), _novo_label("LE_E")
        return (
            f"    CMP R0, R1\n"
            f"    BLE {lt}\n"
            f"    MOV R0, #0\n"
            f"    B {le}\n"
            f"{lt}:\n"
            f"    MOV R0, #1\n"
            f"{le}:"
        )
    else:
        return f"    @ operador desconhecido: {op}"


def _gerar_op_real(op: str) -> str:
    # D1=esq porque foi desempilhado depois de avaliar dir. Ordem:
    # VADD.F64 D0, D1, D0 → D0 = D1 + D0 (esq op dir).
    if op == "+":
        return "    VADD.F64 D0, D1, D0"
    elif op == "-":
        return "    VSUB.F64 D0, D1, D0"
    elif op == "*":
        return "    VMUL.F64 D0, D1, D0"
    elif op in ("|", "/"):
        # VDIV não funciona no CPulator DEC1-SOC.
        # Converte D1 e D0 para inteiros (via S), aplica loop de subtração,
        # converte resultado de volta para D0 (F64).
        label_loop = _novo_label("RDIV_LOOP")
        label_fim = _novo_label("RDIV_FIM")
        return (
            f"    @ divisao real via loop de subtracao (VDIV nao suportado)\n"
            f"    VCVT.S32.F64 S0, D1\n"
            f"    VMOV R0, S0\n"
            f"    VCVT.S32.F64 S0, D0\n"
            f"    VMOV R1, S0\n"
            f"    MOV R2, #0\n"
            f"{label_loop}:\n"
            f"    CMP R0, R1\n"
            f"    BLT {label_fim}\n"
            f"    SUB R0, R0, R1\n"
            f"    ADD R2, R2, #1\n"
            f"    B {label_loop}\n"
            f"{label_fim}:\n"
            f"    VMOV S0, R2\n"
            f"    VCVT.F64.S32 D0, S0"
        )
    else:
        return f"    @ operador real nao suportado: {op}"


def _gerar_cmd_mem_store(no: No) -> str:
    valor_no, mem_id_no = no.filhos[0], no.filhos[1]
    nome = mem_id_no.valor or "?"
    linhas = [f"    @ CMD_MEM_STORE: {nome} = {valor_no.valor}"]
    linhas.append(_gerar_operando_int(valor_no))
    linhas.append(f"    LDR R1, ={nome}")
    linhas.append(f"    STR R0, [R1]")
    return "\n".join(linhas)


def _gerar_cmd_mem_load(no: No) -> str:
    mem_id_no = no.filhos[0]
    nome = mem_id_no.valor or "?"
    return (
        f"    @ CMD_MEM_LOAD: R0 = {nome}\n"
        f"    LDR R1, ={nome}\n"
        f"    LDR R0, [R1]"
    )


def _gerar_cmd_res(no: No) -> str:
    # RES_HIST armazena F64 (8 bytes por entrada). LSL #3 = índice × 8.
    # VLDR D0 carrega 8 bytes sem truncar — resultado disponível em D0 (real)
    # e em R0 (inteiro truncado via VCVT) para uso em qualquer contexto.
    n_no = no.filhos[0]
    n_val = int(n_no.valor or "0")
    linhas = [f"    @ CMD_RES: resultado de {n_val} posicao(oes) atras"]
    linhas.append("    LDR R3, =RES_IDX")
    linhas.append("    LDR R2, [R3]")
    if n_val > 0:
        linhas.append(f"    SUB R2, R2, #{n_val}")
    linhas.append("    LDR R4, =RES_HIST")
    linhas.append("    VLDR D0, [R4, R2, LSL #3]")
    linhas.append("    VCVT.S32.F64 S0, D0")
    linhas.append("    VMOV R0, S0")
    return "\n".join(linhas)


def _gerar_if(no: No) -> str:
    # Estrutura gerada:
    #   avalia condição → R0
    #   CMP R0, #0 / BEQ IF_FIM   (pula se falso, ou seja, R0 == 0)
    #   ... bloco ...
    # IF_FIM:
    # Não há ELSE — a linguagem RPN só define ramo verdadeiro.
    cond_no, bloco_no = no.filhos[0], no.filhos[1]
    label_fim = _novo_label("IF_FIM")

    linhas = ["    @ IF -- avalia condicao"]
    linhas.append(_gerar_no(cond_no))
    linhas.append("    @ se condicao = 0, pula bloco")
    linhas.append("    CMP R0, #0")
    linhas.append(f"    BEQ {label_fim}")
    linhas.append("    @ bloco IF")
    linhas.append(_gerar_bloco(bloco_no))
    linhas.append(f"{label_fim}:")
    return "\n".join(linhas)


def _gerar_while(no: No) -> str:
    # Estrutura gerada:
    # WHILE_LOOP:
    #   avalia condição → R0
    #   CMP R0, #0 / BEQ WHILE_FIM   (sai se falso)
    #   ... corpo ...
    #   B WHILE_LOOP                  (volta ao topo incondicionalmente)
    # WHILE_FIM:
    # A condição é reavaliada a cada iteração — não é otimizada.
    cond_no, bloco_no = no.filhos[0], no.filhos[1]
    label_loop = _novo_label("WHILE_LOOP")
    label_fim = _novo_label("WHILE_FIM")

    linhas = ["    @ WHILE"]
    linhas.append(f"{label_loop}:")
    linhas.append("    @ avalia condicao")
    linhas.append(_gerar_no(cond_no))
    linhas.append("    CMP R0, #0")
    linhas.append(f"    BEQ {label_fim}")
    linhas.append("    @ corpo do WHILE")
    linhas.append(_gerar_bloco(bloco_no))
    linhas.append(f"    B {label_loop}")
    linhas.append(f"{label_fim}:")
    return "\n".join(linhas)


def _gerar_bloco(no: No) -> str:
    """Gera código para um BLOCO de comandos."""
    partes = [f"    @ BLOCO ({len(no.filhos)} comando(s))"]
    for filho in no.filhos:
        partes.append(_gerar_no(filho))
    return "\n".join(partes)


def _gerar_secao_dados(mem_ids: list[str], floats: dict[str, str]) -> str:
    # RES_HIST: 1024 bytes = 256 words × 4 bytes. Suficiente para programas de teste.
    # STACK_TOP fica no final do bloco .space da pilha — SP cresce para baixo em ARMv7,
    # então inicializar SP = STACK_TOP e fazer PUSH decrementa o endereço corretamente.
    linhas = [".data"]
    linhas.append("")
    linhas.append("@ Historico de resultados (maximo 256 entradas x 8 bytes = F64)")
    linhas.append("RES_IDX: .word 0")
    linhas.append("RES_HIST: .space 2048")
    linhas.append("")

    if mem_ids:
        linhas.append("@ Variaveis de memoria")
        for nome in sorted(mem_ids):
            linhas.append(f"{nome}: .word 0")
        linhas.append("")

    if floats:
        linhas.append("@ Constantes de ponto flutuante (F64 — obrigatorio no CPulator v16.1)")
        for label, val in sorted(floats.items()):
            linhas.append(f"{label}: .double {val}")
        linhas.append("")

    linhas.append("@ Pilha de software (1 KB)")
    linhas.append("STACK: .space 1024")
    linhas.append("STACK_TOP:")
    linhas.append("")

    return "\n".join(linhas)

# Interface pública de assembly.py -> gerarAssembly

def gerarAssembly(arvore: No) -> str:
    """Gera string de código Assembly ARMv7 a partir da árvore sintática."""
    global _label_count, _float_labels
    _label_count = 0

    # Pré-passo 1: coleta nomes de variáveis MEM para alocar em .data.
    # Feito antes de gerar .text porque a seção .data precisa vir primeiro no arquivo.
    mem_ids: set[str] = set()
    _coletar_mem_ids(arvore, mem_ids)
    mem_lista = sorted(mem_ids)

    # Pré-passo 2: coleta literais float para gerar labels .float em .data.
    # _gerar_operando_real_em_s0 usa VLDR com label — o label precisa existir em .data.
    _float_labels = {}
    _coletar_floats(arvore, _float_labels)

    # Ordem do arquivo: .data primeiro, depois .text.
    # CPulator exige essa ordem; .text referencia labels definidos em .data.
    secao_dados = _gerar_secao_dados(mem_lista, _float_labels)
    secao_texto = _gerar_programa(arvore)

    return secao_dados + "\n" + secao_texto
