---
name: refactor-arch
description: Analisa a stack de um backend, audita anti-patterns de MVC, segurança e APIs obsoletas, e refatora para Model-View-Controller. Use somente quando o usuário invocar /refactor-arch ou pedir explicitamente a skill refactor-arch.
disable-model-invocation: true
---

# refactor-arch

Skill agnóstica de tecnologia. Funciona em monolito e em projeto que já tem pastas. Não cite nomes de arquivo destes três projetos de exemplo dentro das regras: detecte sinais no código que estiver aberto.

Execute as fases em ordem. Leia cada referência só na fase que a cita.

## Fase 1 — Análise

Leia [references/project-analysis.md](references/project-analysis.md). Não edite arquivo nenhum.

Imprima exatamente este bloco, preenchido:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:      <framework e versão>
Dependencies:  <dependências diretas>
Domain:        <domínio em uma linha>
Architecture:  <como o código está organizado hoje>
Source files:  <N> files analyzed
DB tables:     <tabelas ou "none">
================================
```

Conte só arquivos de código da aplicação. Ignore `.cursor/`, `reports/`, lockfiles e `node_modules`.

## Fase 2 — Auditoria

Leia [references/anti-patterns.md](references/anti-patterns.md) e [references/audit-report-template.md](references/audit-report-template.md).

Compare o código com o catálogo. Cada finding precisa de arquivo e linhas reais. Ordene CRITICAL, HIGH, MEDIUM, LOW. Inclua APIs obsoletas quando existirem; se não existirem, registre uma linha dizendo que a checagem foi feita e nada foi encontrado.

Grave o relatório em `reports/audit-project-N.md` na raiz do repositório (N = 1, 2 ou 3, conforme o projeto pedido). Não altere código de aplicação.

Pare e pergunte, neste formato:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Espere um sim explícito. Sem esse sim, a Fase 3 não começa.

## Fase 3 — Refatoração

Só depois do sim. Leia [references/mvc-guidelines.md](references/mvc-guidelines.md) e [references/refactor-playbook.md](references/refactor-playbook.md).

Reestruture para MVC. Se o projeto já tiver models, routes ou services, complete o que falta (config, controllers, erro central, entry point) em vez de apagar a separação que já existe.

Regras:

- Mantenha os endpoints de negócio e os códigos HTTP que o cliente já usa.
- Elimine o anti-pattern. Rota que existe só para executar SQL arbitrário ou vazar segredo continua respondendo, sem o comportamento perigoso.
- Config vem de ambiente. Sem segredo no fonte.
- Valide subindo a aplicação e chamando os endpoints originais.

Ao terminar, imprima:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Se o boot ou um endpoint falhar, ajuste a referência que levou ao erro e repita a Fase 3. Não declare sucesso com a aplicação quebrada.
