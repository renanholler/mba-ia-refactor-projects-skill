# Playbook de refatoração

Nove transformações obrigatórias, mais variações que o catálogo cita. Aplique só o que o relatório marcou. Preserve status HTTP e o corpo de sucesso das rotas de negócio.

## 1. SQL concatenado → query parametrizada

Antes:

```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

Depois:

```python
row = db.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
```

Node: `db.run("DELETE FROM users WHERE id = ?", [id])`. Nunca interpolar o SQL do cliente. A rota que executava SQL livre passa a responder 403.

## 2. Segredo no fonte → ambiente

Antes:

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

Depois:

```python
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
```

O fallback é só de desenvolvimento e não é o segredo antigo. Produção define a variável. A mesma chave não volta no JSON de health.

## 3. God class → MVC

Antes: um módulo com `CREATE TABLE`, `INSERT` de vários domínios e `app.post` no mesmo arquivo.

Depois: config, um model por domínio, controller por fluxo, rotas só com o registro, `app.py` / `app.js` como composition root. Veja a árvore em `mvc-guidelines.md`.

## 4. Senha na resposta e hash fraco

Antes:

```python
return {"email": self.email, "password": self.password}
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

Depois:

```python
def to_public_dict(self):
    return {"id": self.id, "email": self.email, "role": self.role}

def set_password(self, pwd):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", pwd.encode(), salt.encode(), 260_000).hex()
    self.password = f"pbkdf2$260000${salt}${digest}"
```

Node: `crypto.pbkdf2Sync` ou `crypto.scryptSync`. Login de senha antiga em texto puro pode comparar uma vez e seguir; usuário novo grava PBKDF2. O JSON público não tem `password` nem `senha`.

## 5. Estado global → ciclo de vida do request

Antes:

```python
db_connection = None
```

Depois:

```python
def get_db():
    if "db_conn" not in g:
        g.db_conn = sqlite3.connect(current_app.extensions["settings"].db_path)
        g.db_conn.row_factory = sqlite3.Row
    return g.db_conn
```

Feche no `teardown_appcontext`. Em Node, crie o cache no `app.js` e passe para o controller. Não exporte um objeto mutável do módulo de config.

## 6. N+1 → JOIN ou eager load

Antes: para cada pedido, `SELECT itens` e, para cada item, `SELECT produto`.

Depois:

```sql
SELECT p.id, p.total, i.quantidade, pr.nome AS produto_nome
FROM pedidos p
LEFT JOIN itens_pedido i ON i.pedido_id = p.id
LEFT JOIN produtos pr ON pr.id = i.produto_id
```

Agrupe as linhas no model. Em ORM: `query.options(joinedload(Task.user), joinedload(Task.category))`.

## 7. Rota gorda → rota fina e controller

Antes: o blueprint valida, consulta e monta o JSON em uma função de 80 linhas.

Depois:

```python
@task_bp.route("/tasks", methods=["GET"])
def get_tasks():
    return task_controller.list_tasks()
```

A validação repetida vira uma função. A rota de categoria sai do blueprint de relatório se esse for o único motivo de ela estar lá. As URLs não mudam.

## 8. API obsoleta → equivalente atual

Antes:

```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
task = Task.query.get(task_id)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
```

Depois:

```python
def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

created_at = db.Column(db.DateTime, default=utc_now)
task = db.session.get(Task, task_id)
# não defina SQLALCHEMY_TRACK_MODIFICATIONS
```

`replace(tzinfo=None)` só quando a coluna já persiste datetime ingênuo. Hash de senha: ver transformação 4.

## 9. Rota sensível sem identidade → token de admin

Rota sensível: `DELETE`, listagem ou detalhe de usuário, e relatório. Health, login, checkout, listagem de produto ou task e criação/atualização ficam com o contrato anterior.

Antes: qualquer cliente apaga ou lê esse dado.

Depois: `ADMIN_TOKEN` vem de `os.environ` / `process.env`. O fallback de desenvolvimento é `dev-only-change-me` e não é um segredo antigo. O cliente envia `Authorization: Bearer <token>`. Compare com `secrets.compare_digest` ou `crypto.timingSafeEqual` só quando os dois valores têm o mesmo tamanho. Token ausente ou diferente: 401, no envelope que o projeto já usa, e o handler não roda.

```python
def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = current_app.config["ADMIN_TOKEN"]
        header = request.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else ""
        if len(token) != len(expected) or not secrets.compare_digest(token, expected):
            return jsonify({"erro": "Não autorizado"}), 401
        return view(*args, **kwargs)
    return wrapper
```

Node: middleware na rota sensível, `res.status(401).send("Não autorizado")`. Não grave o token no log. Rota de SQL arbitrário ou reset que já responde 403 continua 403, com ou sem token.

## Extras curtos

- Número mágico vira constante ao lado da regra (`DISCOUNT_OVER_10000 = 0.10`).
- `except:` nu vira exceção específica, com rollback da sessão.
- Import não usado e export não lido saem.
- Parâmetro `u`, `e`, `p` no controller ganha nome. A chave do JSON de entrada permanece a que o cliente já envia (`usr`, `eml`), para o contrato não quebrar.
