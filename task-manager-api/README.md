# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. A estrutura tem `models/`, `routes/`, `controllers/`, `services/`, `utils/`, `config/` e `middlewares/`.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo. Rode-o antes do primeiro boot; sem o seed, os endpoints devolvem listas vazias. A senha de desenvolvimento dos três usuários é `dev-only-change-me`. `SEED_JOAO_PASSWORD`, `SEED_MARIA_PASSWORD` e `SEED_PEDRO_PASSWORD` substituem esse valor. Login: `joao@email.com` / `dev-only-change-me`.
