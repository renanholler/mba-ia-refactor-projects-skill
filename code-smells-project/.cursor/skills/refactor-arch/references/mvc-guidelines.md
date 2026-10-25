# Guidelines MVC

O alvo é o mesmo nas duas stacks. Os nomes de pasta mudam só na extensão e no entry point.

## Responsabilidades

- **Config:** lê ambiente (segredo, porta, caminho do banco, CORS, debug). Não tem regra de negócio.
- **Model:** schema, SQL ou ORM, e regra que precisa do dado (estoque, status, atraso). Não importa request HTTP.
- **Controller:** lê o request, chama model ou service, devolve status e corpo. Não monta SQL.
- **View / Routes:** registra método, caminho e controller. Sem `if` de negócio.
- **Middleware de erro:** 500 genérico, exceção no log. Erro de domínio (400, 404, 401, 409) nasce no controller, com mensagem estável.
- **Entry point:** cria a app, aplica config, registra rotas e handler, sobe o servidor. É o composition root.

Service é opcional. Use para efeito colateral (e-mail, cache) que não é dado nem HTTP.

## Python / Flask

```
app.py                      # composition root; `python app.py` continua válido
src/
├── config/settings.py
├── models/
├── controllers/
├── views/routes.py
└── middlewares/error_handler.py
```

Conexão por request (`flask.g`) e `teardown_appcontext`. Schema e seed rodam uma vez na subida.

## Node / Express

```
src/
├── app.js                  # composition root; `npm start` continua válido
├── config/settings.js
├── db.js
├── models/
├── controllers/
├── routes/index.js
└── middlewares/errorHandler.js
```

O `app.js` espera o schema antes de `listen` quando o banco é criado na subida.

## Projeto que já tem camadas

Não mova tudo para `src/` se `models/`, `routes/` e `python app.py` já são o contrato do repositório.

Acrescente:

- `config/settings.py` e tire literal de segredo do `app.py`
- `controllers/` e deixe a rota com uma chamada
- `middlewares/error_handler.py`
- model com o método que a rota duplicava (atraso, DTO sem senha)

Mantenha blueprints e URLs.

## O que não fazer

- Não apague endpoint de negócio para "limpar" o código.
- Não troque o formato de sucesso de checkout, listagem ou login além de tirar segredo do corpo.
- Não introduza framework novo. Use a biblioteca que já está no manifesto.
- Não deixe a skill acoplada a um projeto: a mesma pasta `refactor-arch` é copiada para os outros.
