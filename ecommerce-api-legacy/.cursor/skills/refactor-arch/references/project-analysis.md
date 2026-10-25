# Análise de projeto

Use estes sinais. A primeira evidência forte vence; confirme com uma segunda.

## Linguagem

- `requirements.txt`, `pyproject.toml`, `import` / `def` → Python
- `package.json`, `require(`, `import ` de pacote npm → JavaScript (Node)
- Não misture linguagem de teste ou de script solto com a da aplicação. A linguagem é a dos arquivos que sobem o servidor.

## Framework e versão

- Python: `from flask import` ou `Flask(` → Flask. Versão em `requirements.txt` (`flask==`). `flask_sqlalchemy` / `SQLAlchemy()` → Flask-SQLAlchemy, versão na mesma lista.
- Node: `require('express')` ou `from 'express'` → Express. Versão em `dependencies.express` do `package.json`.
- Anote também bibliotecas de HTTP, CORS, banco e validação que aparecem no manifesto.

## Banco

- `sqlite3`, arquivo `.db`, `sqlite:///`, `':memory:'` → SQLite
- `CREATE TABLE`, modelos `db.Model` / `db.Column` → leia os nomes das tabelas (`__tablename__` ou o SQL)
- Sem conexão e sem schema → `none`

## Arquitetura atual

Classifique o que existe, não o que você quer criar.

- Monólito: regras, SQL e rotas no mesmo arquivo, ou um único objeto que registra todas as rotas e fala com o banco.
- Parcial: pastas `models/`, `routes/`, `services/` ou `utils/`, mas sem controller, sem config externa, ou com regra de negócio ainda na rota.
- MVC: models só de dados, rotas só encaminham, controllers orquestram, config fora do código, erro centralizado.

Conte os arquivos de código. Descreva o domínio pelo nome das rotas e das tabelas (loja, curso, task, pagamento), em uma linha.

## O que imprimir

Preencha o bloco da Fase 1 com o que foi observado. Não proponha a estrutura nova nesta fase.
