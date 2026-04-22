**Responsável:** Mariana Alves

## Tarefas

- Implementar `gerarArvore(derivacao)` para construir a árvore sintática
- Transformar a derivação em estrutura de árvore
- Implementar impressão da árvore em formato legível
- Salvar árvore em arquivo (JSON ou formato customizado) para uso nas próximas fases
- Implementar `gerarAssembly(arvore)` gerando código **ARMv7** diretamente da árvore
- Plataforma: **Cpulator-ARMv7 DEC1-SOC (v16.1)**
- Implementar `main()` e gerenciar a interface de linha de comando
- Coordenar integração de todos os módulos (`lerTokens`, `construirGramatica`, `parsear`, `gerarArvore`)
- Criar funções de teste end-to-end
- Testar o sistema completo com os 3 arquivos de teste

## Funções a implementar

- `gerarArvore(derivacao)`
- `gerarAssembly(arvore)`
- `main()`

## Interface

- **Entrada:** Estrutura de derivação do parser
- **Saída:** Árvore sintática em formato estruturado
- **Gerencia:** execução completa via linha de comando

## Execução

```
./AnalisadorSintatico teste1.txt
```

### Decisões de Arquitetura

## 1. `No` como dataclass com 4 campos fixos

**O que é:**
Todo nó da árvore é um `No` com exatamente quatro campos:

```python
@dataclass
class No:
    tipo: str          # "PROGRAMA", "EXPR", "IF", "WHILE", "BLOCO",
                       # "CMD_RES", "CMD_MEM_STORE", "CMD_MEM_LOAD",
                       # "OPERANDO", "MEM_ID", "OP"
    valor: Optional[str]  # literal do token (None para nós compostos)
    filhos: list          # List[No]
    linha: int            # linha de origem para rastreio de erros
```

**Por que:**
`@dataclass` gera `__init__`, `__eq__` e `__repr__` automaticamente. Manter 4 campos em todos os nós — mesmo que `valor` seja `None` e `filhos` seja `[]` — torna o código de assembly previsível: sempre acessa `no.valor`, `no.filhos[0]`, etc., sem checar se o campo existe.

**Consequência:**
`assembly.py` desestrutura os filhos por índice fixo. Se a ordem dos filhos mudar em `ConstrutorNo`, o assembly quebra. Essa dependência é intencional e está documentada nos comentários de `criar_expr` e `criar_cmd_mem_store`.

---

## 2. `ConstrutorNo` como implementação concreta do Protocol

**O que é:**
`ConstrutorNo` em `arvore.py` implementa os 11 métodos do `ConstrutorArvore` Protocol definido em `parser.py`, sem herdar explicitamente.

**Por que:**
Python Protocols usam *structural typing* — qualquer classe que tenha os métodos certos satisfaz o contrato. `ConstrutorNo` não importa o Protocol nem herda dele; apenas implementa os mesmos métodos. O parser chama os métodos sem saber que `ConstrutorNo` existe.

**Consequência:**
Se o parser mudar a assinatura de um método do Protocol, `ConstrutorNo` deixa de satisfazê-lo silenciosamente em runtime (mypy pega em tempo estático). Mudanças no contrato precisam ser sincronizadas entre os dois arquivos.

---

## 3. Ordem dos filhos em `criar_expr`: [esq, dir, op]

**O que é:**
Nós `EXPR` têm exatamente 3 filhos na ordem: operando esquerdo, operando direito, operador.

```python
def criar_expr(self, esq, dir, op, linha) -> No:
    return No(tipo="EXPR", valor=None, filhos=[esq, dir, op], linha=linha)
```

**Por que:**
Espelha a gramática RPN da linguagem — na sintaxe do código-fonte, o operador vem depois dos dois operandos. `assembly.py` faz `op_esq, op_dir, op_no = no.filhos[0], no.filhos[1], no.filhos[2]` diretamente, sem nenhuma reordenação.

**Consequência:**
Diferente de árvores de expressão convencionais (onde o operador é a raiz). Aqui o operador é uma *folha* — filho de `EXPR`, não pai.

---

## 4. Gerador de assembly como funções puras, não como classe

**O que é:**
`assembly.py` é um conjunto de funções (`_gerar_expr`, `_gerar_if`, etc.) em vez de uma classe `GeradorAssembly`.

**Por que:**
O gerador não precisa de estado entre chamadas, exceto pelo contador de labels (`_label_count`) e o mapa de floats (`_float_labels`), que são globais resetados no início de `gerarAssembly()`. Funções puras são mais fáceis de testar isoladamente e de ler — cada função recebe um nó e retorna uma string.

**Consequência:**
O contador global não é thread-safe, mas o projeto é single-threaded. Se o gerador for chamado duas vezes sem reset, os números de label continuam de onde pararam — por isso `gerarAssembly()` reseta `_label_count = 0` sempre.

---

## 5. Registradores de convenção: R0 (inteiro) e D0 (real, F64)

**O que é:**
Toda expressão inteira deixa resultado em `R0`. Toda expressão real deixa resultado em `D0` (VFP double-precision, 64 bits).

**Por que F64 e não F32?**
O O projeto anterior confirmou que F64 (`D` registers) é obrigatório.

**Consequência:**
Para operações binárias reais, o padrão é: avalia esq -> `VPUSH {D0}` (8 bytes) -> avalia dir -> `VPOP {D1}` -> opera com `D1=esq, D0=dir`. Conversão entre int e double usa `S0` como registrador intermediário: `VMOV S0, R0` -> `VCVT.F64.S32 D0, S0`.

**Por que ainda aparece S0 na conversão inteiro → F64?**
O ARMv7 não possui a instrução `VCVT.F64.S32 Dd, Rn` — não existe conversão direta de registrador ARM (`R`) para double (`D`). O conjunto de instruções exige passar por um registrador `S` (32 bits) como ponte obrigatória:

```asm
VMOV S0, R0          @ move o inteiro para S0 (bit pattern idêntico, não é float)
VCVT.F64.S32 D0, S0  @ converte o inteiro de 32 bits para F64 em D0
```

`S0` aqui guarda um **inteiro**, não um float de 32 bits. F64 representa todos os inteiros de 32 bits com precisão exata, então não há perda de informação. Para constantes float vindas do `.data`, o carregamento é direto em 64 bits: `VLDR D0, label` — sem passar por `S`.

---

## 6. Dois pré-passos antes de gerar o texto do assembly

**O que é:**
`gerarAssembly()` percorre a árvore duas vezes antes de gerar qualquer instrução:
1. `_coletar_mem_ids` — coleta todos os nomes de variáveis MEM
2. `_coletar_floats` — coleta todos os literais de ponto flutuante

**Por que:**
A seção `.data` precisa declarar variáveis e constantes float *antes* que a seção `.text` as referencie. Não é possível emitir a seção `.data` parcialmente enquanto se gera `.text`. Os pré-passos garantem que tudo que `.text` vai usar já está declarado em `.data`.

**Consequência:**
A ordem no arquivo gerado é sempre `.data` depois `.text`. O CPulator exige essa ordem; referências a labels não declarados causam erro de montagem.

---

## 7. `salvar_res=True` apenas para comandos de topo

**O que é:**
`_gerar_expr` recebe um flag `salvar_res`. Quando `True`, emite instruções para salvar o resultado no array `RES_HIST` e incrementar `RES_IDX`. Quando `False`, apenas calcula.

**Por que:**
O histórico RES é uma feature do nível de programa — cada *comando* de topo produz um resultado que pode ser recuperado por `(N RES)`. Expressões usadas como *condição* de IF/WHILE não são comandos; salvá-las no histórico quebraria a semântica de `(1 RES)`.

**Consequência:**
`_gerar_cmd_topo` passa `salvar_res=True`; `_gerar_if` e `_gerar_while` chamam `_gerar_no(cond)` que passa `salvar_res=False` implicitamente.

---

## 8. Potência (`^`) e divisão real (`|`) implementadas como loops — sem instruções nativas

A mesma estratégia de loop usada para potência foi aplicada à divisão.

---

## 8a. Potência (`^`) implementada como loop de multiplicação

**O que é:**

```asm
@ potencia R0^R1
MOV R6, R0    @ base
MOV R7, R1    @ expoente
MOV R0, #1   @ acumulador
POT_LOOP:
    CMP R7, #0
    BLE POT_FIM
    MUL R0, R0, R6
    SUB R7, R7, #1
    B POT_LOOP
POT_FIM:
```

**Por que:**
ARMv7 não tem instrução nativa de potência. A biblioteca VFP tem `VPOW` em versões mais completas, mas o CPulator DEC1-SOC não expõe essa instrução. Loop de multiplicação é a alternativa correta para expoentes inteiros não-negativos.

**Consequência:**
Expoentes negativos retornam resultado incorreto (o loop não executa e o acumulador fica em 1). Limitação conhecida — fora do escopo da linguagem RPN definida.

---

## 8b. Divisão real (`|`) implementada como loop de subtração

**O que é:**

```asm
@ R0 / R1 via subtração
MOV R2, #0
RDIV_LOOP:
    CMP R0, R1
    BLT RDIV_FIM
    SUB R0, R0, R1
    ADD R2, R2, #1
    B RDIV_LOOP
RDIV_FIM:
    MOV R0, R2   @ quociente inteiro
```

**Por que:**
`VDIV.F32` não é suportado pelo CPulator DEC1-SOC (verificado em trabalho anterior). Loop de subtração conta quantas vezes o divisor cabe no dividendo — equivalente a divisão inteira por quociente.

**Consequência:**
O resultado de `|` é inteiro truncado, sem parte fracionária. Para os casos de teste do projeto (inteiros), o comportamento é equivalente à divisão inteira `/`. A diferença entre os dois operadores no CPulator fica sem efeito prático.

---

## 9. Inicialização explícita de SP e VFP em `_gerar_programa`

**O que é:**
Todo programa gerado começa com:

```asm
LDR SP, =STACK_TOP   @ inicializa stack pointer
LDR R0, =0x40000000
FMXR FPEXC, R0       @ habilita coprocessador VFP
```

**Por que:**
O CPulator ARMv7 bare-metal (DEC1-SOC) não inicializa SP automaticamente. Qualquer `PUSH`/`POP` sem SP inicializado lê/escreve no endereço 0x0, corrompendo o programa. O VFP precisa ser habilitado via `FPEXC` (bit EN = 1) antes de qualquer instrução com registradores S.

**Consequência:**
Sem essas linhas, programas que usam operandos reais ou blocos IF/WHILE travam no simulador sem mensagem de erro clara.

---