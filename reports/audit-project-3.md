================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0, Flask-SQLAlchemy 3.1.1
Files:   12 analyzed | ~1155 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] to_dict devolve o hash da senha
File: models/user.py:16-25
Description: `User.to_dict` inclui `password`. `GET /users/<id>` usa esse dicionário (`routes/user_routes.py:33`). `POST /users` e `PUT /users/<id>` também (`routes/user_routes.py:85` e `routes/user_routes.py:129`). O login devolve o mesmo objeto em `user` (`routes/user_routes.py:207-210`). A listagem `GET /users` monta outro dicionário e não inclui a senha.
Impact: Consulta, cadastro, atualização e login entregam o hash da senha no JSON. Com MD5, o hash é o bastante para entrar de novo.
Recommendation: DTO público sem `password`. O login devolve o usuário público e não a credencial.

### [CRITICAL] Senha SMTP no fonte
File: services/notification_service.py:7-10
Description: `NotificationService` fixa host, porta, `taskmanager@gmail.com` e `email_password` igual a `senha123`. `send_email` faz login SMTP com esses valores.
Impact: A credencial de e-mail entra no repositório. Quem lê o fonte envia mensagem como essa conta.
Recommendation: Ler host, usuário e senha de `os.environ`. O segredo não fica no fonte e não entra em log.

### [CRITICAL] SECRET_KEY fixa no fonte
File: app.py:13
Description: `app.config['SECRET_KEY']` recebe o literal `super-secret-key-123`.
Impact: O segredo da aplicação fica no Git. Quem lê o fonte forja a sessão.
Recommendation: `os.environ.get("SECRET_KEY", "dev-only-change-me")`. O fallback não é o segredo antigo.

### [CRITICAL] Seed grava senha a partir de literal
File: seed.py:19
Description: O seed chama `set_password` com `1234` (`seed.py:19`), `abcd` (`seed.py:25`) e `pass` (`seed.py:31`). O valor chega ao banco só depois do MD5, mas a senha em claro está no fonte.
Impact: Três credenciais de exemplo ficam no Git, inclusive `joao@email.com` com role `admin`.
Recommendation: Não versionar senha. Se o seed precisar de usuário, a senha vem de ambiente e o que se grava é PBKDF2.

### [HIGH] Token previsível e rotas sem identidade
File: routes/user_routes.py:207-210
Description: O login responde `token` igual a `fake-jwt-token-` mais o id. Nenhuma rota lê esse token. `DELETE /users/<id>` (`routes/user_routes.py:134-148`), `DELETE /tasks/<id>` (`routes/task_routes.py:225-235`) e `GET /reports/summary` (`routes/report_routes.py:12`) seguem sem checagem.
Impact: O token é o id do usuário. Qualquer cliente apaga conta ou task e lê o relatório.
Recommendation: Não inventar um JWT novo. Parar de devolver credencial e de usar `fake-jwt-token-` + id. Registrar que delete e relatório seguem sem identidade.

### [HIGH] Senha comparada e gravada com MD5
File: models/user.py:27-32
Description: `set_password` e `check_password` usam `hashlib.md5(...).hexdigest()`, sem sal.
Impact: A senha vira um hash rápido e sem sal. O valor que `to_dict` devolve é reaproveitável no login.
Recommendation: `hashlib.pbkdf2_hmac`. Usuário novo grava PBKDF2. Senha antiga em MD5 pode comparar uma vez e, no acerto, ser regravada.

### [HIGH] Rotas com validação, ORM e regra de atraso
File: routes/task_routes.py:11-299
Description: O blueprint de tasks valida título, status e prioridade, consulta usuário e categoria, calcula atraso e monta o JSON. `routes/user_routes.py` e `routes/report_routes.py` repetem o mesmo tipo de handler. `Task.is_overdue` e `utils/helpers.py` existem e as rotas não chamam.
Impact: A pasta `routes/` é a aplicação. A regra de atraso não testa sem o request.
Recommendation: Rota só encaminha. Controller orquestra. Model persiste e calcula atraso. As URLs permanecem.

### [MEDIUM] N+1 na listagem de tasks e no relatório
File: routes/task_routes.py:41-57
Description: Para cada task, `GET /tasks` faz `User.query.get` e `Category.query.get`. O model já declara `relationship` em `models/task.py:20-21` e a rota não usa. O resumo percorre usuários e, para cada um, busca as tasks (`routes/report_routes.py:53-61`). `GET /categories` conta tasks por categoria (`routes/report_routes.py:163`).
Impact: A listagem e o relatório crescem em queries com o volume.
Recommendation: `joinedload` de `user` e `category` na listagem. No relatório, agregar sem uma query por usuário ou por categoria.

### [MEDIUM] except nu e erro sem um handler só
File: routes/task_routes.py:62
Description: `GET /tasks` usa `except:` sem tipo. O mesmo aparece na data do create (`routes/task_routes.py:137`), na data do update (`routes/task_routes.py:204`), no delete de task (`routes/task_routes.py:236`), no update e delete de usuário (`routes/user_routes.py:130` e `routes/user_routes.py:149`) e no CRUD de categoria (`routes/report_routes.py:186`, `routes/report_routes.py:207`, `routes/report_routes.py:221`). Vários handlers não têm `try`. O `print` de `str(e)` fica em `routes/task_routes.py:153` e `routes/user_routes.py:89`.
Impact: Falha inesperada some no `except` nu ou segue sem tratamento. Não há um formato único fora o JSON que cada rota monta à mão.
Recommendation: Handler único. Erro de domínio com mensagem estável. 500 genérico para falha inesperada, detalhe só no log. Rollback da sessão no erro.

### [MEDIUM] Atraso e validação copiados, com helper sem uso
File: routes/task_routes.py:30-39
Description: A conta de atraso está de novo em `routes/task_routes.py:71-80`, `routes/task_routes.py:283-287`, `routes/report_routes.py:33-36`, `routes/report_routes.py:132-135` e `routes/user_routes.py:171-180`. `Task.is_overdue` (`models/task.py:50-60`) faz a mesma conta e ninguém chama. Título (3 e 200) e status válido estão no create e no update, e de novo em `utils/helpers.py:57-108`, que nenhuma rota importa para usar.
Impact: A regra de atraso e a de título divergem se um handler mudar e o outro não.
Recommendation: Uma função de atraso no model, chamada pelos fluxos. Uma função de validação, no lugar das cópias.

### [MEDIUM] APIs obsoletas do SQLAlchemy e de datetime
File: app.py:12
Description: `SQLALCHEMY_TRACK_MODIFICATIONS` está ligado no config. `datetime.utcnow` é o default de `models/user.py:14`, `models/task.py:15-16` e `models/category.py:11`, e a comparação de atraso nas rotas. `Query.get` aparece em `routes/task_routes.py:42`, `routes/task_routes.py:51`, `routes/task_routes.py:67` e nos outros blueprints. O MD5 de senha está no finding HIGH, não aqui.
Impact: A biblioteca já marca esses pontos como obsoletos. `utcnow` devolve datetime ingênuo, o mesmo tipo que o SQLite já guarda.
Recommendation: Remover `SQLALCHEMY_TRACK_MODIFICATIONS`. Trocar `Query.get` por `session.get`. Trocar `datetime.utcnow` por `datetime.now(timezone.utc)` e tirar o tzinfo na borda, para não misturar com o valor ingênuo já persistido.

### [LOW] Limites de título, senha e janela de sete dias sem nome na rota
File: routes/task_routes.py:96-100
Description: Create exige título entre 3 e 200. O update repete em `routes/task_routes.py:167-170`. A senha usa 4 em `routes/user_routes.py:64` e `routes/user_routes.py:115`. O relatório usa 7 dias em `routes/report_routes.py:45`. `utils/helpers.py:112-116` já nomeia título e senha, e a rota não lê.
Impact: O contrato de tamanho está solto em cada handler.
Recommendation: Constantes no módulo da regra, usadas pelos dois fluxos.

### [LOW] Parâmetro de uma letra na prioridade e na busca
File: models/task.py:45
Description: `validate_priority` recebe `p`. A busca lê o termo em `request.args.get('q')` (`routes/task_routes.py:242`).
Impact: A regra de prioridade e o contrato da busca não dizem o campo. O restante do JSON já usa `title`, `email`, `password`.
Recommendation: Nomear o argumento da prioridade. Na busca, o nome interno deixa de ser uma letra; a chave `q` que o cliente já envia permanece.

### [LOW] Imports mortos e serviço que nenhuma rota chama
File: app.py:7
Description: `app.py` importa `os`, `sys` e `json` e não usa. `routes/task_routes.py:7` importa `json`, `os`, `sys` e `time`. `routes/user_routes.py:6` importa `hashlib` e `json`. `routes/report_routes.py:7` importa `format_date`, `calculate_percentage` e `json` sem usar. `utils/helpers.py:3-7` importa `os`, `json`, `sys`, `math` e `hashlib` sem usar. `NotificationService` não é importado por nenhuma rota; as linhas 7-10 desse arquivo estão no finding de SMTP.
Impact: O arquivo mente sobre a dependência. O serviço de e-mail parece parte do fluxo e não é.
Recommendation: Apagar import e export não lidos. Passar a chamar o serviço só se o fluxo que já existe precisar de notificação.

## Deprecated APIs
- app.py:12 — `SQLALCHEMY_TRACK_MODIFICATIONS` → remover a chave
- models/user.py:14, models/task.py:15-16, models/category.py:11 — `datetime.utcnow` → `datetime.now(timezone.utc).replace(tzinfo=None)` (a coluna já guarda datetime ingênuo; o mesmo chamado se repete nas rotas e no seed)
- routes/task_routes.py:42 — `User.query.get` → `db.session.get` (o mesmo padrão em `routes/task_routes.py:51`, `routes/task_routes.py:67`, `routes/user_routes.py:29` e `routes/report_routes.py:105`)
- models/user.py:29 — MD5 → `hashlib.pbkdf2_hmac`. Esse trecho está no finding HIGH de hash fraco, para não entrar de novo como MEDIUM.

================================
Total: 14 findings
================================
