# Catálogo de anti-patterns

Cada item tem sinal observável, severidade e correção. A correção detalhada está no playbook. Um arquivo pode ter vários findings.

## CRITICAL

### sql-injection

Sinal: SQL montado com concatenação, f-string ou template no meio da query (`"WHERE id = " +`, `` `... ${id}` ``, `LIKE '%" + termo`). Também conta endpoint que recebe SQL do cliente e executa.

Correção: query parametrizada. Remova a execução de SQL arbitrário; a rota pode responder 403.

### hardcoded-secrets

Sinal: `SECRET_KEY`, senha, token, chave de gateway, SMTP ou connection string com valor literal no fonte. Seed com senha em texto puro conta.

Correção: `os.environ` / `process.env`. Segredo não entra em resposta HTTP.

### god-class

Sinal: um arquivo ou uma classe concentra schema, SQL, regra de negócio e registro de rotas de mais de um domínio. Entry point que abre cursor e altera tabela também conta.

Correção: partir em models, controllers e rotas por domínio.

### sensitive-data-exposure

Sinal: resposta JSON inclui senha, hash, `SECRET_KEY`, cartão completo ou chave de pagamento. Log que imprime cartão ou segredo conta igual.

Correção: DTO público sem segredo. Log sem dado sensível.

## HIGH

### weak-crypto

Sinal: senha comparada em texto puro, hash MD5/SHA1 para senha, ou função caseira que repete base64/substring e chama isso de hash.

Correção: `hashlib.pbkdf2_hmac` (Python) ou `crypto.pbkdf2` / `crypto.scrypt` (Node).

### global-mutable-state

Sinal: conexão, cache ou totalizador em variável de módulo (`db_connection = None`, `let globalCache = {}`) reutilizada por todos os requests.

Correção: conexão por request, ou objeto criado no composition root e injetado.

### fat-controller

Sinal: a função de rota ou o controller mistura validação extensa, SQL e efeito colateral (e-mail, SMS, print de negócio). Em projeto que já tem `routes/`, a rota com dezenas de linhas de regra é o mesmo problema: falta controller.

Correção: rota só encaminha. Controller orquestra. Model persiste. Efeito colateral vai para um service.

### missing-auth

Sinal: rota que apaga dado, lista usuário com segredo ou devolve relatório financeiro sem qualquer checagem de identidade.

Correção: não invente um produto de login novo se a API não tinha sessão. Separe a rota, pare de vazar dado e registre o buraco. Onde já existe login, não devolva credencial e não use token previsível (`fake-jwt-token-` + id).

## MEDIUM

### n-plus-one

Sinal: query dentro de `for` / `forEach` para buscar o pai ou o filho de cada linha (pedido → itens → produto, curso → matrículas → usuário).

Correção: `JOIN` ou eager load (`joinedload`).

### duplicated-logic

Sinal: o mesmo bloco de validação ou a mesma regra (atraso, status válido) copiado em dois handlers, com um helper ao lado que ninguém chama.

Correção: uma função, chamada pelos dois fluxos.

### missing-error-handling

Sinal: `except:` nu, `try/except` copiado em toda função devolvendo `str(e)`, ou callbacks aninhados sem um tratamento só. Resposta de erro ora texto, ora JSON.

Correção: handler único. Erro de domínio explícito. 500 genérico para falha inesperada, detalhe só no log.

### deprecated-api

Sinal e substituição:

- `datetime.utcnow` → `datetime.now(timezone.utc)`. Se a coluna já guarda datetime ingênuo, retire o tzinfo na borda para não misturar os dois.
- `Model.query.get(id)` → `session.get(Model, id)`
- `SQLALCHEMY_TRACK_MODIFICATIONS` setado no config → remova a chave
- MD5/SHA1 de senha → PBKDF2 ou scrypt
- hash caseiro → `crypto.pbkdf2` ou `crypto.scrypt`

Se nenhum sinal aparecer, escreva no relatório que a checagem foi feita e não houve API obsoleta.

## LOW

### magic-numbers

Sinal: limite de taxa, tamanho mínimo ou código de status de negócio como literal repetido (`0.1`, `10000`, `3`, `200`) sem nome.

Correção: constante nomeada no módulo da regra.

### poor-naming

Sinal: parâmetro de uma letra (`u`, `e`, `p`, `cid`) no contrato HTTP ou em função de negócio.

Correção: nome do campo (`name`, `email`, `password`, `courseId`).

### dead-code

Sinal: import não usado, variável exportada e nunca lida, service que nenhuma rota chama.

Correção: apague ou passe a usar, se a chamada for parte do fluxo que já existia.
