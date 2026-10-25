# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
SEED_ADMIN_PASSWORD=admin123 SEED_JOAO_PASSWORD=joao123 SEED_MARIA_PASSWORD=maria123 python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado no primeiro boot, com os produtos de exemplo. Os usuários só entram se `SEED_ADMIN_PASSWORD`, `SEED_JOAO_PASSWORD` e `SEED_MARIA_PASSWORD` estiverem definidas. Login: `admin@loja.com` e o valor de `SEED_ADMIN_PASSWORD`.
