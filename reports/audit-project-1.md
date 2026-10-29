================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 7 | HIGH: 3 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Endpoint executa SQL enviado pelo cliente
File: app.py:59-76
Description: `POST /admin/query` lê `sql` do JSON e passa a string para `cursor.execute`. Se o texto começa com SELECT, devolve as linhas; caso contrário faz `commit`.
Impact: Qualquer cliente lê, altera ou apaga `produtos`, `usuarios`, `pedidos` e `itens_pedido`. O banco inteiro fica exposto na rede.
Recommendation: Remover a execução de SQL arbitrário. A rota pode continuar existindo e responder 403. Queries de negócio usam parâmetros, no padrão de sql-injection do playbook.

### [CRITICAL] Queries montadas por concatenação
File: models.py:289-297
Description: `buscar_produtos` interpola `termo`, `categoria`, `preco_min` e `preco_max` em `LIKE` e em filtros. O mesmo padrão aparece em `models.py:28` (produto por id), `models.py:47-50` (insert de produto), `models.py:57-61` (update), `models.py:68` (delete), `models.py:91` (usuário por id), `models.py:109-111` (login com email e senha), `models.py:126-129` (insert de usuário), `models.py:140` e `models.py:148-166` (pedido, item e estoque), `models.py:174` (pedidos do usuário) e `models.py:279-281` (status).
Impact: Texto vindo do cliente vira comando SQL. No login, a senha ainda é comparada em texto puro dentro da própria query; a correção desse trecho é a deste finding, para não classificar as mesmas linhas de novo.
Recommendation: Trocar cada concatenação por query parametrizada. No login, gravar e comparar a senha com `hashlib.pbkdf2_hmac` (sinal weak-crypto), sem manter a senha na cláusula SQL.

### [CRITICAL] God class e entry point que apaga tabelas
File: models.py:1-314
Description: `models.py` concentra SQL, checagem de estoque, preço do pedido, formatação e o desconto do relatório dos quatro domínios (produto, usuário, pedido, venda). O entry point repete o acesso direto ao banco: `app.py:47-58` abre cursor e executa `DELETE` em `itens_pedido`, `pedidos`, `produtos` e `usuarios`.
Impact: Não dá para testar um domínio sem carregar os outros. `POST /admin/reset-db` zera a base sem checagem de identidade.
Recommendation: Partir em models, controllers e rotas por domínio. O entry point só sobe o processo. A rota de reset continua respondendo, sem abrir cursor nem apagar tabela.

### [CRITICAL] Health devolve a SECRET_KEY
File: controllers.py:276-289
Description: `health_check` coloca no JSON `secret_key` com o literal `minha-chave-super-secreta-123`, além de `debug`, `db_path` e `ambiente`.
Impact: Qualquer chamada a `GET /health` revela o segredo da aplicação e detalhe interno de deploy.
Recommendation: DTO público sem segredo. O valor da chave, se existir, vem de ambiente e não entra na resposta HTTP.

### [CRITICAL] Resposta de usuário inclui a senha
File: models.py:79-86
Description: `get_todos_usuarios` monta o dicionário com `senha`. `get_usuario_por_id` repete o campo em `models.py:95-100`. `GET /usuarios` e `GET /usuarios/<id>` devolvem esse dicionário. O login (`models.py:114-119`) não inclui a senha.
Impact: Listar ou buscar usuário entrega a credencial em texto puro para quem chamar a rota.
Recommendation: DTO público sem `senha`. Log e JSON ficam sem dado sensível.

### [CRITICAL] SECRET_KEY fixa no fonte
File: app.py:7
Description: `app.config["SECRET_KEY"]` recebe o literal `minha-chave-super-secreta-123`. O mesmo texto é repetido na resposta do health, tratado no finding anterior.
Impact: O segredo da aplicação entra no repositório. Quem lê o fonte forja sessão ou confirma o valor vazado no health.
Recommendation: Ler a chave de `os.environ`. Sem literal de segredo no fonte.

### [CRITICAL] Seed grava senha em texto puro
File: database.py:76-78
Description: No primeiro boot, o seed insere `admin123`, `123456` e `senha123` na coluna `senha` de `usuarios`. O `INSERT` em si usa placeholder; o problema é o valor literal.
Impact: Três credenciais de exemplo ficam no Git e no banco, inclusive a conta `admin@loja.com` com tipo `admin`.
Recommendation: Não versionar senha. Se o seed precisar de usuário, gravar só o hash (`hashlib.pbkdf2_hmac`), com o segredo vindo de ambiente.

### [HIGH] Rotas sensíveis sem checagem de identidade
File: app.py:18
Description: `GET /usuarios` lista usuários (a senha vai no JSON, no finding de exposição). `GET /relatorios/vendas` (`app.py:28`) devolve faturamento. `DELETE /produtos/<id>` (`app.py:16`) apaga produto. Nenhuma dessas rotas verifica identidade. O `POST /admin/reset-db` fica no finding de god class (`app.py:47-58`) para não repetir o mesmo trecho.
Impact: Relatório financeiro, lista de contas e exclusão de produto respondem para qualquer cliente. A API não tem sessão; o buraco é a ausência de fronteira em rota que apaga dado ou revela dado sensível.
Recommendation: Exigir token de admin vindo do ambiente (`ADMIN_TOKEN`), enviado em `Authorization: Bearer`. Sem token válido, responder 401 e não listar usuários, não apagar produto e não devolver o relatório. Não inventar JWT. Não devolver senha.

### [HIGH] Conexão SQLite global compartilhada
File: database.py:4-10
Description: `db_connection` é variável de módulo, criada uma vez em `get_db` e reutilizada com `check_same_thread=False`.
Impact: Todos os requests compartilham a mesma conexão e o mesmo cursor lógico. Requisições concorrentes interferem no estado da conexão.
Recommendation: Abrir conexão por request, ou criar o objeto no composition root e injetar. Sem global mutável.

### [HIGH] Controller mistura validação e efeito colateral
File: controllers.py:188-220
Description: `criar_pedido` valida o corpo, chama o model e em seguida dá `print` de e-mail, SMS e push. `health_check` (`controllers.py:266-274`) abre cursor e conta tabelas dentro do handler. `listar_produtos` (`controllers.py:8`) também imprime o fluxo HTTP.
Impact: A regra de pedido e o I/O de notificação não podem ser testados sem o handler. O health conhece SQL que pertence ao model.
Recommendation: Rota só encaminha. Controller orquestra. Model persiste. Efeito colateral (e-mail, SMS, push) vai para um service. Sem `print` de negócio na resposta.

### [MEDIUM] N+1 ao montar pedidos
File: models.py:187-199
Description: Para cada pedido, `get_pedidos_usuario` consulta `itens_pedido` e, para cada item, consulta `produtos`. `get_todos_pedidos` repete o aninhamento em `models.py:219-231`. O `SELECT` externo de `models.py:174` entra no finding de SQL injection.
Impact: A listagem cresce em queries com o número de pedidos e de itens. As queries internas também concatenam o id.
Recommendation: Uma query com `JOIN` (ou eager load) e parâmetros. Os dois montadores de pedido passam a usar o mesmo carregamento.

### [MEDIUM] Validação de produto copiada
File: controllers.py:24-54
Description: `criar_produto` valida presença de nome, preço e estoque, valores negativos, tamanho do nome e categoria. `atualizar_produto` (`controllers.py:64-90`) repete presença e negativo, e já divergiu: não checa tamanho nem categoria. O mapeamento de produto também está copiado em `models.py:12-21`, `models.py:31-40` e `models.py:304-313`.
Impact: A regra de criar e a de atualizar saem de sincronia. Um ajuste de limite precisa ser feito em dois handlers.
Recommendation: Uma função de validação, chamada pelos dois fluxos, e um único mapeamento de linha para dicionário.

### [MEDIUM] Erro interno devolvido em toda rota
File: controllers.py:10-12
Description: Cada handler captura `Exception` e responde `{"erro": str(e)}` com 500. O mesmo padrão está em `app.py:77-78` na query administrativa. Não há handler único.
Impact: Falha de SQL, de arquivo ou de tipo chega ao cliente com detalhe interno. O formato de erro muda entre rotas que esquecem `sucesso` e rotas que o incluem.
Recommendation: Handler único. Erro de domínio explícito. 500 genérico para falha inesperada, com detalhe só no log.

### [LOW] Faixas de desconto sem nome
File: models.py:257-262
Description: O relatório aplica `10000` / `0.1`, `5000` / `0.05` e `1000` / `0.02` direto na conta do faturamento.
Impact: A regra de desconto não tem nome. Mudar uma faixa exige achar o número solto no meio do SQL do relatório.
Recommendation: Constantes nomeadas no módulo da regra de venda.

### [LOW] Parâmetro de busca com uma letra
File: controllers.py:113
Description: `GET /produtos/busca` lê o termo em `request.args.get("q")`.
Impact: O contrato HTTP não diz o que o parâmetro significa. O restante do corpo usa nomes claros (`nome`, `preco`, `categoria`).
Recommendation: Renomear o parâmetro do contrato para `termo`.

### [LOW] Imports não usados
File: models.py:2
Description: `models.py` importa `sqlite3` e não usa o módulo. `database.py:2` importa `os` e não usa.
Impact: O arquivo mente sobre a dependência. Quem lê procura uso de `sqlite3` no model e não acha.
Recommendation: Apagar os dois imports.

## Deprecated APIs
- Checagem feita. Nenhuma API obsoleta do catálogo encontrada (`datetime.utcnow`, `Query.get`, `SQLALCHEMY_TRACK_MODIFICATIONS`, MD5/SHA1 de senha, hash caseiro).

================================
Total: 16 findings
================================
