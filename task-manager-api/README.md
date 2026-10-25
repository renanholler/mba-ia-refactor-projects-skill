# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. A estrutura tem `models/`, `routes/`, `controllers/`, `services/`, `utils/`, `config/` e `middlewares/`.

## Como rodar

```bash
pip install -r requirements.txt
SEED_JOAO_PASSWORD=1234 SEED_MARIA_PASSWORD=abcd SEED_PEDRO_PASSWORD=pass python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo. Rode-o antes do primeiro boot, com as três variáveis de senha definidas; sem elas o script para, e sem o seed os endpoints devolvem listas vazias. Login: `joao@email.com` / `1234`.
