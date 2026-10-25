# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado no primeiro boot, com produtos e usuários. A senha de desenvolvimento é `dev-only-change-me`. `SEED_ADMIN_PASSWORD`, `SEED_JOAO_PASSWORD` e `SEED_MARIA_PASSWORD` substituem esse valor. Login: `admin@loja.com` / `dev-only-change-me`.
