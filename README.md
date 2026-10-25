# Refatoração arquitetural com a skill refactor-arch

Skill de projeto, no Cursor, que analisa um backend, audita anti-patterns e refatora para MVC. A mesma pasta está nos três projetos do repositório. A ferramenta é o Cursor: o enunciado aceita qualquer ferramenta agêntica com skill, e a convenção daqui é `.cursor/skills/refactor-arch/`.

Severidade usada na análise e nos relatórios:

- **CRITICAL:** falha grave de arquitetura ou segurança (credencial no fonte, SQL injection, God class, dado sensível na resposta).
- **HIGH:** violação forte de MVC ou SOLID (regra de negócio presa na rota, estado global, hash fraco, rota destrutiva sem identidade).
- **MEDIUM:** duplicação, N+1, erro espalhado, API obsoleta.
- **LOW:** nome ruim, número mágico, import morto.

## Análise Manual

Leitura do código antes da skill existir. Cada projeto tem pelo menos um achado CRITICAL ou HIGH, dois MEDIUM e dois LOW.

### code-smells-project (Python/Flask)

API de e-commerce em quatro arquivos (`app.py`, `controllers.py`, `models.py`, `database.py`), sem camadas.

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | SQL injection por concatenação, e `POST /admin/query` executa o SQL enviado pelo cliente | `models.py:28`, `models.py:47-50`, `models.py:109-111`, `models.py:289-297`, `app.py:59-76` | Qualquer texto vira comando no banco. A rota administrativa lê ou apaga a base. |
| CRITICAL | `SECRET_KEY` no fonte, o health devolve essa chave, e o seed grava senha em texto puro | `app.py:7`, `controllers.py:286-289`, `database.py:76-78` | O segredo está no Git e na resposta HTTP. |
| HIGH | God class: SQL, estoque, desconto e formatação de quatro domínios no mesmo módulo. O entry point também executa SQL | `models.py:1-314`, `app.py:47-58` | Não dá para testar um domínio sem carregar o resto. |
| MEDIUM | N+1 ao montar pedidos: por pedido, uma query de itens e outra de produto | `models.py:171-200`, `models.py:203-233` | A listagem cresce em queries com o volume. |
| MEDIUM | Validação de produto copiada entre criar e atualizar. Cada função devolve `str(e)` no próprio `except` | `controllers.py:24-54`, `controllers.py:64-90` | A regra diverge e o cliente recebe detalhe interno. |
| LOW | Faixas de desconto do relatório são números soltos (`10000`, `0.1`, `5000`, `0.05`) | `models.py:257-262` | A regra de faturamento não tem nome. |
| LOW | Conexão SQLite numa variável global e `print` no fluxo HTTP | `database.py:4-10`, `controllers.py:8` | Requests compartilham a mesma conexão. |

### ecommerce-api-legacy (Node.js/Express)

LMS com checkout. `app.js` só sobe o processo. `AppManager.js` concentra banco, rotas, pagamento e relatório.

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | Senha de banco, chave de gateway e SMTP fixos no módulo de config | `src/utils.js:2-5` | Chave `pk_live_` e senha entram no Git. |
| CRITICAL | God class. O número do cartão e a chave do gateway vão para o log | `src/AppManager.js:25-138`, `src/AppManager.js:45` | Um arquivo é a aplicação, e o log vaza o cartão. |
| HIGH | `badCrypto` repete um prefixo de base64. Se a senha não vem, o código usa `123456` | `src/utils.js:17-23`, `src/AppManager.js:68` | O valor gravado não é um hash de senha. |
| MEDIUM | Relatório financeiro em queries aninhadas: curso, matrícula, usuário, pagamento | `src/AppManager.js:83-123` | N+1. Se uma query falha no meio, a resposta se perde. |
| MEDIUM | Callbacks aninhados. Erro ora é texto puro, ora JSON | `src/AppManager.js:37-77` | O checkout é difícil de seguir e o formato de erro não é estável. |
| LOW | Corpo do checkout lido para `u`, `e`, `p`, `cid`, `cc` | `src/AppManager.js:29-33` | O contrato `usr`, `eml`, `pwd`, `c_id`, `card` fica ilegível. |
| LOW | `totalRevenue` é exportado e nunca lido. O delete de usuário deixa matrícula e pagamento, e a resposta descreve isso | `src/utils.js:10`, `src/AppManager.js:131-136` | Código morto e dado órfão de propósito. |

### task-manager-api (Python/Flask)

Já tem `models/`, `routes/`, `services/` e `utils/`. Falta controller, config fora do fonte, e os problemas de segurança continuam.

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | `SECRET_KEY` e senha SMTP hardcoded | `app.py:13`, `services/notification_service.py:7-10` | Segredo da aplicação e credencial de e-mail no fonte. |
| HIGH | `to_dict` devolve o hash da senha, e o hash é MD5 | `models/user.py:16-25`, `models/user.py:27-32` | Login e consulta entregam a senha. MD5 não serve para senha. |
| HIGH | Rotas gordas: validação, ORM e regra de atraso dentro do blueprint, sem controller | `routes/task_routes.py:11-299` | A pasta `routes/` é a aplicação. O service de notificação existe e não é usado. |
| MEDIUM | N+1 na listagem: uma query de usuário e outra de categoria por task | `routes/task_routes.py:41-57` | O model já tem `relationship` e a rota não usa. |
| MEDIUM | APIs obsoletas: `datetime.utcnow`, `Query.get` e `SQLALCHEMY_TRACK_MODIFICATIONS` | `models/user.py:14`, `models/task.py:15-16`, `routes/task_routes.py:42`, `app.py:12` | A biblioteca já tem o substituto. |
| LOW | Imports não usados | `app.py:7`, `routes/task_routes.py:7`, `utils/helpers.py:3-7` | O arquivo mente sobre o que depende. |
| LOW | Tamanho de título (3 e 200) e a conta de atraso estão copiados. `helpers.py` já tem parte disso e ninguém chama | `routes/task_routes.py:96-100`, `utils/helpers.py:57-108` | Número mágico repetido ao lado de função morta. |

## Construção da Skill

A skill fica em `.cursor/skills/refactor-arch/` e é a mesma nos três projetos. O `SKILL.md` só conduz as fases. O conhecimento está em cinco arquivos:

| Arquivo | Papel |
|---|---|
| `references/project-analysis.md` | Heurística de linguagem, framework, banco e arquitetura atual |
| `references/anti-patterns.md` | 15 sinais, nas quatro severidades, com API obsoleta |
| `references/audit-report-template.md` | Formato da Fase 2: arquivo, linha, ordem CRITICAL → LOW |
| `references/mvc-guidelines.md` | Config, model, controller, rota, erro central e entry point, em Flask e em Express |
| `references/refactor-playbook.md` | Oito transformações com antes e depois |

`disable-model-invocation: true` faz a skill carregar só quando alguém chama `/refactor-arch`. A Fase 2 grava `reports/audit-project-N.md` na raiz do repositório e para. A Fase 3 só edita código depois de um sim.

O catálogo cobre o que a análise manual mostrou, em forma genérica: SQL concatenado, segredo literal, God class, senha na resposta, hash fraco, estado global, rota gorda, N+1, validação duplicada, erro espalhado, API obsoleta, número mágico, nome ruim e código morto. Nenhum sinal cita o nome de um arquivo destes projetos. Por isso a mesma pasta serve para Flask monolito, Express e Flask que já tem camadas.

No projeto que já tem `models/` e `routes/`, a guideline manda completar controller, config e erro central, sem mover tudo para `src/`.

Dois cuidados ficaram no playbook. Tirar senha do JSON e recusar SQL arbitrário muda a resposta perigosa; as rotas de negócio continuam com o mesmo caminho e o mesmo status. No task manager, datetime com fuso quebraria a comparação com o que o SQLite já guarda ingênuo, então a troca de `datetime.utcnow` tira o fuso na borda.

## Resultados

A Fase 2 rodou nos três projetos e gravou `reports/audit-project-1.md`, `reports/audit-project-2.md` e `reports/audit-project-3.md`. Cada relatório tem arquivo e linha, ordem CRITICAL → LOW, e uma seção de API obsoleta. A Fase 3 só começou depois do sim.

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | API obsoleta |
|---|---|---|---|---|---|---|
| code-smells-project | 7 | 3 | 3 | 3 | 16 | nenhuma do catálogo |
| ecommerce-api-legacy | 4 | 4 | 2 | 2 | 12 | hash caseiro → `crypto.pbkdf2` |
| task-manager-api | 4 | 3 | 4 | 3 | 14 | `datetime.utcnow`, `Query.get`, `SQLALCHEMY_TRACK_MODIFICATIONS`, MD5 |

### Antes e depois

**code-smells-project.** Quatro arquivos na raiz (`app.py`, `controllers.py`, `models.py`, `database.py`), sem camada. Depois, `app.py` só compõe a aplicação. O resto foi para `src/config`, `src/models`, `src/controllers`, `src/views`, `src/middlewares`, `src/services` e `src/database.py`. O comando continua `python app.py`.

**ecommerce-api-legacy.** `src/app.js` subia o processo e `AppManager.js` com `utils.js` eram a aplicação. Esses dois arquivos saíram. No lugar: `src/config`, `src/db.js`, `src/security`, `src/models`, `src/controllers`, `src/routes`, `src/middlewares` e `src/services`. O comando continua `npm start`, o banco continua em memória e a porta continua 3000.

**task-manager-api.** Já tinha `models/`, `routes/`, `services/` e `utils/`. A Fase 3 não moveu isso para `src/`. Entrou `config/`, `controllers/` e `middlewares/`, e as rotas de categoria ganharam `routes/category_routes.py`. Os blueprints ficaram finos. `python app.py` e `python seed.py` continuam na raiz.

### Checklist de validação

O mesmo checklist vale para os três. Todos os itens foram conferidos no código refatorado e na subida de cada API.

| Item | Loja | LMS | Tasks |
|---|---|---|---|
| Linguagem e framework certos na Fase 1 | sim | sim | sim |
| Domínio certo (e-commerce, LMS, task manager) | sim | sim | sim |
| Contagem de arquivos condiz com o código auditado (4, 3 e 12) | sim | sim | sim |
| Relatório no template, com arquivo e linha, ordenado por severidade | sim | sim | sim |
| Pelo menos 5 findings, com CRITICAL | sim | sim | sim |
| API obsoleta registrada, ou a checagem explícita de que não havia | sim | sim | sim |
| Fase 2 parou e esperou o sim | sim | sim | sim |
| MVC, config fora do fonte, model, rota, controller, erro central, entry point | sim | sim | sim |
| Sobe e os endpoints originais respondem | sim | sim | sim |

### Logs

Nesta máquina a porta 5000 já estava ocupada, então as duas APIs Flask subiram com `PORT`. O default do código continua 5000.

Loja, `PORT=5050`, banco novo e senhas de seed definidas:

```text
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5050
==================================================
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5050
```

`GET /`, `GET /health`, `GET /produtos` e `GET /usuarios` responderam 200. O health não devolve `secret_key`. A lista de usuários não tem `senha`. `POST /login` com `admin@loja.com` respondeu 200. `POST /produtos` respondeu 201 e `POST /pedidos` respondeu 201. `GET /relatorios/vendas` respondeu 200. `POST /admin/query` respondeu 403.

LMS, `node src/app.js`:

```text
Frankenstein LMS rodando na porta 3000...
[LOG] Salvando no cache: last_checkout_2
```

Checkout com cartão `4111…` respondeu 200 `{"msg":"Sucesso","enrollment_id":2}`. Cartão `5111…` respondeu 400 `Pagamento recusado`. O log do cache não imprime o cartão. `GET /api/admin/financial-report` respondeu 200. `DELETE /api/users/1` respondeu 200. As chaves do corpo continuam `usr`, `eml`, `pwd`, `c_id` e `card`.

Task manager, seed e depois `PORT=5051`:

```text
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5051
```

`GET /`, `GET /health`, `GET /tasks`, `GET /tasks/stats`, `GET /categories` e `GET /reports/summary` responderam 200. A listagem de tasks traz `user_name` e `category_name`. `GET /users` não traz `password`. `POST /login` com `joao@email.com` respondeu 200.

### O que mudou entre as stacks

No Flask monolito a skill criou a árvore `src/` inteira e deixou o entry point na raiz, porque `python app.py` é o contrato. No Express a árvore MVC ficou dentro de `src/`, porque `npm start` já apontava para `src/app.js`, e o banco em memória não ganhou arquivo. No Flask que já tinha pastas, a skill completou controller, config e erro central no lugar em que o código já estava, sem inventar um `src/`.

O catálogo é o mesmo. O que muda é o sinal encontrado. A loja não tinha API obsoleta do catálogo: a senha estava em texto puro. O LMS tinha o hash caseiro. O task manager tinha `datetime.utcnow`, `Query.get`, `SQLALCHEMY_TRACK_MODIFICATIONS` e MD5. Nas três, segredo saiu do fonte (fallback `dev-only-change-me`), senha nova vai com PBKDF2, e senha antiga em texto puro ou MD5 ainda confere se o banco já existia. A comparação de data no task manager tira o fuso na borda, para não quebrar o datetime ingênuo que o SQLite já guarda.

## Como Executar

Pré-requisito: Cursor aberto na raiz deste repositório.

```text
/refactor-arch no code-smells-project
```

Troque o nome da pasta para `ecommerce-api-legacy` e depois para `task-manager-api`. A Fase 1 imprime a stack. A Fase 2 grava o relatório na raiz e pergunta se pode refatorar. A Fase 3 só começa com um sim.

As duas APIs Flask usam a porta 5000. Suba uma de cada vez.

```bash
cd code-smells-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

```bash
cd ecommerce-api-legacy
npm install
npm start
```

```bash
cd task-manager-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
python app.py
```

A senha de desenvolvimento dos usuários de exemplo é `dev-only-change-me`. Ela não é a senha antiga do clone. `SEED_ADMIN_PASSWORD`, `SEED_JOAO_PASSWORD`, `SEED_MARIA_PASSWORD`, `SEED_PEDRO_PASSWORD` e `SEED_USER_PASSWORD` substituem esse valor quando existem. Login da loja: `admin@loja.com` / `dev-only-change-me`. Login do task manager: `joao@email.com` / `dev-only-change-me`. O Leonan entra com a mesma senha.

Loja em `http://localhost:5000/health` e `http://localhost:5000/produtos`. LMS em `http://localhost:3000`, com os pedidos de `ecommerce-api-legacy/api.http`. Task manager em `http://localhost:5000/health`, `/tasks` e `/login`. Se a 5000 já estiver ocupada, suba uma das APIs Flask com `PORT`.
