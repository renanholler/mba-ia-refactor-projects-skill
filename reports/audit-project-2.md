================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] Log imprime cartão e chave do gateway
File: src/AppManager.js:45
Description: No checkout, o console escreve o número completo do cartão (`cc`) e `config.paymentGatewayKey`.
Impact: O log do processo fica com o PAN do cartão e a chave `pk_live_`. Quem lê o stdout lê o pagamento.
Recommendation: Log sem dado sensível. A chave sai do fonte (finding de segredo) e não entra em mensagem de log.

### [CRITICAL] Senha de banco, chave de gateway e SMTP no fonte
File: src/utils.js:2-6
Description: `config` fixa `dbPass` (`senha_super_secreta_prod_123`), `paymentGatewayKey` (`pk_live_1234567890abcdef`) e `smtpUser`. A porta 3000 está no mesmo objeto.
Impact: Credencial e chave de produção entram no repositório. A chave é a mesma impressa no checkout.
Recommendation: Ler segredo, SMTP e porta de `process.env`. O fallback de desenvolvimento não reutiliza o valor que já está no fonte.

### [CRITICAL] Seed grava senha em texto puro
File: src/AppManager.js:18
Description: O boot insere o usuário Leonan com `pass` igual a `123` direto no `INSERT`.
Impact: A credencial de exemplo fica no Git e no banco em claro. O checkout de usuário novo ainda passa por outro hash, fraco, tratado no finding de criptografia.
Recommendation: Não versionar senha. Se o seed precisar de usuário, gravar só o resultado de `crypto.pbkdf2` ou `crypto.scrypt`, com o segredo vindo de ambiente.

### [CRITICAL] God class concentra banco, pagamento e rotas
File: src/AppManager.js:4-138
Description: `AppManager` abre o SQLite, cria `users`, `courses`, `enrollments`, `payments` e `audit_logs`, e registra checkout, relatório financeiro e delete de usuário. `src/app.js` só instancia essa classe.
Impact: Pagamento, matrícula e relatório não existem fora desse objeto. Um domínio não testa sem carregar os outros.
Recommendation: Partir em config, model por domínio, controller por fluxo e rotas só de registro. O entry point fica como composition root.

### [HIGH] Relatório e delete sem checagem de identidade
File: src/AppManager.js:131-136
Description: `DELETE /api/users/:id` apaga o usuário e não verifica quem chamou. `GET /api/admin/financial-report` (`src/AppManager.js:80`) devolve receita e alunos do mesmo modo. A API não tem sessão.
Impact: Qualquer cliente apaga conta e lê o relatório financeiro. O delete ainda deixa matrícula e pagamento, e a própria resposta descreve isso.
Recommendation: Exigir token de admin vindo do ambiente (`ADMIN_TOKEN`), enviado em `Authorization: Bearer`. Sem token válido, responder 401 e não apagar o usuário nem devolver o relatório. Não inventar JWT nem sessão.

### [HIGH] Hash caseiro de senha com fallback 123456
File: src/utils.js:17-23
Description: `badCrypto` repete, 10000 vezes, os dois primeiros caracteres do base64 da senha e devolve 10 caracteres. No checkout (`src/AppManager.js:68`), se `pwd` não vem, a função recebe `123456`.
Impact: O valor gravado em `pass` não é um hash de senha. Duas senhas com o mesmo prefixo base64 colidem, e a senha padrão é previsível.
Recommendation: `crypto.pbkdf2` ou `crypto.scrypt`. Usuário novo grava esse hash. Não usar senha padrão quando o campo falta.

### [HIGH] Cache global e uma conexão para todos os requests
File: src/utils.js:9-15
Description: `globalCache` é variável de módulo. `logAndCache` grava o último checkout de cada usuário nesse objeto, chamado em `src/AppManager.js:59`. O `sqlite3.Database` também é único: `src/AppManager.js:7`, criado uma vez em `src/app.js:8`.
Impact: Requests compartilham cache e conexão. Um checkout lê e escreve estado deixado por outro.
Recommendation: Criar cache e conexão no composition root e injetar, ou abrir conexão por operação. Sem objeto mutável exportado do módulo de config.

### [HIGH] Checkout mistura validação, SQL e pagamento
File: src/AppManager.js:28-77
Description: O handler de `POST /api/checkout` valida o corpo, consulta curso e usuário, decide se o cartão paga, insere matrícula, pagamento e auditoria, e grava cache. O log do cartão na linha 45 é o finding de exposição.
Impact: A regra de pagamento não roda sem o handler HTTP. O fluxo é uma cadeia de callbacks difícil de testar.
Recommendation: Rota só encaminha. Controller orquestra. Model persiste. Efeito colateral de pagamento e cache vai para um service.

### [MEDIUM] Erro ora é texto, ora JSON, em callbacks aninhados
File: src/AppManager.js:35-61
Description: Checkout responde 400, 404 e 500 com `send` de texto (`"Bad Request"`, `"Erro DB"`, `"Pagamento recusado"`) e o sucesso com `json`. O relatório (`src/AppManager.js:104-106`) ignora `err` nas queries internas. O delete (`src/AppManager.js:133-135`) também ignora `err` e sempre responde texto; esse handler está no finding de identidade, aqui entra o formato.
Impact: O cliente não tem um contrato de erro. Se uma query do meio falha, o relatório pode não responder.
Recommendation: Handler único. Erro de domínio com status estável. 500 genérico para falha inesperada, detalhe só no log.

### [MEDIUM] N+1 no relatório financeiro
File: src/AppManager.js:89-123
Description: Para cada curso, uma query de matrículas; para cada matrícula, uma query de usuário e outra de pagamento.
Impact: O número de queries cresce com cursos e matrículas. O aninhamento é o mesmo bloco que perde a resposta se uma query interna falha.
Recommendation: Uma query com `JOIN` de curso, matrícula, usuário e pagamento, agrupada no model.

### [LOW] Corpo do checkout lido em variáveis de uma letra
File: src/AppManager.js:29-33
Description: O handler copia `usr`, `eml`, `pwd`, `c_id` e `card` para `u`, `e`, `p`, `cid` e `cc`.
Impact: A regra de checkout fica ilegível. O contrato que o cliente já envia continua sendo essas chaves JSON.
Recommendation: Nomear as variáveis no controller (`name`, `email`, `password`, `courseId`, `card`). As chaves do JSON de entrada permanecem `usr`, `eml`, `pwd`, `c_id` e `card`.

### [LOW] totalRevenue exportado e nunca lido
File: src/utils.js:10
Description: `totalRevenue` começa em 0, é exportado em `src/utils.js:25` e importado em `src/AppManager.js:2`. Nenhuma rota lê ou atualiza o valor.
Impact: O módulo mente sobre um totalizador de receita. Quem procura o faturamento acha uma variável morta ao lado do relatório de verdade.
Recommendation: Apagar a variável, o export e o import.

## Deprecated APIs
- src/utils.js:17-23 — hash caseiro → `crypto.pbkdf2` ou `crypto.scrypt`. O trecho está no finding HIGH de hash fraco, para não entrar de novo como MEDIUM.
- Checagem também feita para `datetime.utcnow`, `Query.get`, `SQLALCHEMY_TRACK_MODIFICATIONS` e MD5/SHA1 de senha. Nenhum desses apareceu.

================================
Total: 12 findings
================================
