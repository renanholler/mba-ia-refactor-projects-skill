# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e carrega cursos, uma matrícula e o usuário Leonan no boot. A senha desse usuário vem de `SEED_USER_PASSWORD`; se a variável não existir, o boot gera um valor aleatório. O checkout de `api.http` não depende dessa senha.

Exemplos de requisições estão em `api.http`.
