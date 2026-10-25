# Template do relatório (Fase 2)

Grave este formato em `reports/audit-project-N.md`. Não encurte o cabeçalho. Ordenação dos findings: CRITICAL, depois HIGH, MEDIUM e LOW. Dentro da mesma severidade, o mais grave primeiro.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <título curto>
File: <caminho>:<linha> ou <caminho>:<inicio>-<fim>
Description: <o que o código faz>
Impact: <o que quebra ou vaza>
Recommendation: <apontar o padrão do playbook, sem aplicar ainda>

### [HIGH] <título>
File: <caminho>:<linha>
Description: ...
Impact: ...
Recommendation: ...

## Deprecated APIs
- <arquivo>:<linha> — <API antiga> → <API atual>
ou
- Checagem feita. Nenhuma API obsoleta do catálogo encontrada.

================================
Total: <n> findings
================================
```

Regras:

- Linha e arquivo têm de existir no código analisado.
- Não liste o mesmo trecho duas vezes com severidades diferentes. Escolha a severidade do catálogo.
- O total é a soma do summary.
- Depois do relatório, pare. A pergunta de confirmação fica no chat, não dentro do arquivo.
