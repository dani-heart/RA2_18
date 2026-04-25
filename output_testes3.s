.data

@ Historico de resultados (maximo 256 entradas x 8 bytes = F64)
RES_IDX: .word 0
RES_HIST: .space 2048

@ Constantes auxiliares para loops e relacionais
CONST_ZERO: .double 0.0
CONST_ONE:  .double 1.0

@ Variaveis de memoria (F64, 8 bytes cada)
ATIVO: .double 0.0
BASE: .double 0.0
SAIDA: .double 0.0

@ Constantes de ponto flutuante (F64)
FC_15_0: .double 15.0
FC_5_0: .double 5.0

@ Pilha de software (1 KB)
STACK: .space 1024
STACK_TOP:

.text
@ Assembly ARMv7 gerado automaticamente — RA2-18
@ Plataforma: CPulator ARMv7 DEC1-SOC v16.1

.global _start
_start:

    @ Inicializa stack pointer
    LDR SP, =STACK_TOP

    @ Habilita coprocessador VFP
    LDR R0, =0x40000000
    FMXR FPEXC, R0

    @ Inicializa indice do historico RES
    LDR R4, =RES_IDX
    MOV R5, #0
    STR R5, [R4]

    @ EXPR +
    MOV R0, #8
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 8 -> F64
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #3
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 3 -> F64
    VPOP {D1}   @ desempilha esq em D1
    VADD.F64 D0, D1, D0
    @ salva resultado F64 no historico (8 bytes)
    LDR R3, =RES_IDX
    LDR R2, [R3]
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VSTR D0, [R6]
    ADD R2, R2, #1
    STR R2, [R3]

    @ EXPR -
    MOV R0, #20
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 20 -> F64
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #7
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 7 -> F64
    VPOP {D1}   @ desempilha esq em D1
    VSUB.F64 D0, D1, D0
    @ salva resultado F64 no historico (8 bytes)
    LDR R3, =RES_IDX
    LDR R2, [R3]
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VSTR D0, [R6]
    ADD R2, R2, #1
    STR R2, [R3]

    @ EXPR *
    MOV R0, #4
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 4 -> F64
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #9
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 9 -> F64
    VPOP {D1}   @ desempilha esq em D1
    VMUL.F64 D0, D1, D0
    @ salva resultado F64 no historico (8 bytes)
    LDR R3, =RES_IDX
    LDR R2, [R3]
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VSTR D0, [R6]
    ADD R2, R2, #1
    STR R2, [R3]

    @ EXPR /
    MOV R0, #30
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 30 -> F64
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #6
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 6 -> F64
    VPOP {D1}   @ desempilha esq em D1
    @ divisao via loop de subtracao em F64 (VDIV nao suportado)
    VMOV.F64 D2, D1         @ D2 = esq (dividendo)
    VMOV.F64 D3, D0         @ D3 = dir (divisor)
    LDR R6, =CONST_ZERO
    VLDR D4, [R6]           @ D4 = contador
    LDR R6, =CONST_ONE
    VLDR D5, [R6]           @ D5 = incremento
DIV_LOOP_1:
    VCMP.F64 D2, D3
    VMRS APSR_nzcv, FPSCR
    BLT DIV_FIM_2
    VSUB.F64 D2, D2, D3
    VADD.F64 D4, D4, D5
    B DIV_LOOP_1
DIV_FIM_2:
    VMOV.F64 D0, D4         @ quociente -> D0
    @ salva resultado F64 no historico (8 bytes)
    LDR R3, =RES_IDX
    LDR R2, [R3]
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VSTR D0, [R6]
    ADD R2, R2, #1
    STR R2, [R3]

    @ EXPR %
    MOV R0, #19
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 19 -> F64
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #4
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 4 -> F64
    VPOP {D1}   @ desempilha esq em D1
    @ modulo via loop de subtracao em F64
    VMOV.F64 D2, D1         @ D2 = esq (dividendo)
    VMOV.F64 D3, D0         @ D3 = dir (divisor)
MOD_LOOP_3:
    VCMP.F64 D2, D3
    VMRS APSR_nzcv, FPSCR
    BLT MOD_FIM_4
    VSUB.F64 D2, D2, D3
    B MOD_LOOP_3
MOD_FIM_4:
    VMOV.F64 D0, D2         @ resto -> D0
    @ salva resultado F64 no historico (8 bytes)
    LDR R3, =RES_IDX
    LDR R2, [R3]
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VSTR D0, [R6]
    ADD R2, R2, #1
    STR R2, [R3]

    @ EXPR ^
    MOV R0, #5
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 5 -> F64
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #3
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 3 -> F64
    VPOP {D1}   @ desempilha esq em D1
    @ potencia via loop de multiplicacao em F64
    VMOV.F64 D2, D1         @ D2 = base
    VMOV.F64 D3, D0         @ D3 = expoente (contador)
    LDR R6, =CONST_ONE
    VLDR D4, [R6]           @ D4 = acumulador
    LDR R6, =CONST_ONE
    VLDR D5, [R6]           @ D5 = decremento
POT_LOOP_5:
    VCMP.F64 D3, #0.0
    VMRS APSR_nzcv, FPSCR
    BLE POT_FIM_6
    VMUL.F64 D4, D4, D2
    VSUB.F64 D3, D3, D5
    B POT_LOOP_5
POT_FIM_6:
    VMOV.F64 D0, D4         @ resultado -> D0
    @ salva resultado F64 no historico (8 bytes)
    LDR R3, =RES_IDX
    LDR R2, [R3]
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VSTR D0, [R6]
    ADD R2, R2, #1
    STR R2, [R3]

    @ EXPR |
    LDR R6, =FC_15_0
    VLDR D0, [R6]  @ real 15.0
    VPUSH {D0}  @ empilha esq (8 bytes)
    LDR R6, =FC_5_0
    VLDR D0, [R6]  @ real 5.0
    VPOP {D1}   @ desempilha esq em D1
    @ divisao via loop de subtracao em F64 (VDIV nao suportado)
    VMOV.F64 D2, D1         @ D2 = esq (dividendo)
    VMOV.F64 D3, D0         @ D3 = dir (divisor)
    LDR R6, =CONST_ZERO
    VLDR D4, [R6]           @ D4 = contador
    LDR R6, =CONST_ONE
    VLDR D5, [R6]           @ D5 = incremento
DIV_LOOP_7:
    VCMP.F64 D2, D3
    VMRS APSR_nzcv, FPSCR
    BLT DIV_FIM_8
    VSUB.F64 D2, D2, D3
    VADD.F64 D4, D4, D5
    B DIV_LOOP_7
DIV_FIM_8:
    VMOV.F64 D0, D4         @ quociente -> D0
    @ salva resultado F64 no historico (8 bytes)
    LDR R3, =RES_IDX
    LDR R2, [R3]
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VSTR D0, [R6]
    ADD R2, R2, #1
    STR R2, [R3]

    @ CMD_MEM_STORE: BASE = 5
    MOV R0, #5
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 5 -> F64
    LDR R1, =BASE
    VSTR D0, [R1]  @ salva F64 em BASE

    @ CMD_MEM_STORE: ATIVO = 1
    MOV R0, #1
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 1 -> F64
    LDR R1, =ATIVO
    VSTR D0, [R1]  @ salva F64 em ATIVO

    @ CMD_MEM_LOAD: D0 = BASE
    LDR R1, =BASE
    VLDR D0, [R1]

    @ CMD_RES: resultado de 2 posicao(oes) atras -> D0
    LDR R3, =RES_IDX
    LDR R2, [R3]
    SUB R2, R2, #2
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VLDR D0, [R6]

    @ IF -- avalia condicao -> D0
    @ EXPR >
    LDR R1, =BASE
    VLDR D0, [R1]  @ MEM BASE -> D0
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #3
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 3 -> F64
    VPOP {D1}   @ desempilha esq em D1
    VCMP.F64 D1, D0
    VMRS APSR_nzcv, FPSCR
    BGT GT_T_10
    LDR R6, =CONST_ZERO
    VLDR D0, [R6]
    B GT_E_11
GT_T_10:
    LDR R6, =CONST_ONE
    VLDR D0, [R6]
GT_E_11:
    VCMP.F64 D0, #0.0
    VMRS APSR_nzcv, FPSCR
    BEQ IF_FIM_9  @ pula se falso (D0 == 0.0)
    @ bloco IF
    @ BLOCO (1 comando(s))
    @ CMD_MEM_STORE: SAIDA = 999
    LDR R0, =999
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 999 -> F64
    LDR R1, =SAIDA
    VSTR D0, [R1]  @ salva F64 em SAIDA
IF_FIM_9:

    @ WHILE
WHILE_LOOP_12:
    @ avalia condicao -> D0
    @ EXPR ==
    LDR R1, =ATIVO
    VLDR D0, [R1]  @ MEM ATIVO -> D0
    VPUSH {D0}  @ empilha esq (8 bytes)
    MOV R0, #1
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 1 -> F64
    VPOP {D1}   @ desempilha esq em D1
    VCMP.F64 D1, D0
    VMRS APSR_nzcv, FPSCR
    BEQ EQ_T_14
    LDR R6, =CONST_ZERO
    VLDR D0, [R6]
    B EQ_E_15
EQ_T_14:
    LDR R6, =CONST_ONE
    VLDR D0, [R6]
EQ_E_15:
    VCMP.F64 D0, #0.0
    VMRS APSR_nzcv, FPSCR
    BEQ WHILE_FIM_13  @ sai se falso (D0 == 0.0)
    @ corpo do WHILE
    @ BLOCO (1 comando(s))
    @ CMD_MEM_STORE: ATIVO = 0
    MOV R0, #0
    VMOV S0, R0
    VCVT.F64.S32 D0, S0  @ int 0 -> F64
    LDR R1, =ATIVO
    VSTR D0, [R1]  @ salva F64 em ATIVO
    B WHILE_LOOP_12
WHILE_FIM_13:

    @ CMD_MEM_LOAD: D0 = SAIDA
    LDR R1, =SAIDA
    VLDR D0, [R1]

    @ CMD_RES: resultado de 1 posicao(oes) atras -> D0
    LDR R3, =RES_IDX
    LDR R2, [R3]
    SUB R2, R2, #1
    LDR R4, =RES_HIST
    ADD R6, R4, R2, LSL #3
    VLDR D0, [R6]

_end:
    B _end
