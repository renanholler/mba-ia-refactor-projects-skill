import hashlib
import secrets

from src.database import get_db

_ITERATIONS = 260_000


def hash_password(senha):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), _ITERATIONS).hex()
    return f"pbkdf2${_ITERATIONS}${salt}${digest}"


def verify_password(stored, senha):
    if stored is None or not isinstance(senha, str):
        return False
    stored = str(stored)
    if stored.startswith("pbkdf2$"):
        parts = stored.split("$")
        if len(parts) != 4:
            return False
        try:
            iterations = int(parts[1])
        except ValueError:
            return False
        salt = parts[2]
        digest = parts[3]
        check = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), iterations).hex()
        if len(check) != len(digest):
            return False
        return secrets.compare_digest(check, digest)
    if len(stored) != len(senha):
        return False
    return secrets.compare_digest(stored, senha)


def _publico(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_todos_usuarios():
    rows = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios"
    ).fetchall()
    return [_publico(row) for row in rows]


def get_usuario_por_id(id):
    row = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
        (id,),
    ).fetchone()
    if row is None:
        return None
    return _publico(row)


def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, hash_password(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def login_usuario(email, senha):
    db = get_db()
    row = db.execute(
        "SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = ?",
        (email,),
    ).fetchone()
    if row is None or not verify_password(row["senha"], senha):
        return None
    if not str(row["senha"]).startswith("pbkdf2$"):
        db.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (hash_password(senha), row["id"]),
        )
        db.commit()
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
