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