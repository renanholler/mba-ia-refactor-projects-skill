from src.database import get_db


def _para_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_todos_produtos():
    rows = get_db().execute("SELECT * FROM produtos").fetchall()
    return [_para_dict(row) for row in rows]


def get_produto_por_id(id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    if row is None:
        return None
    return _para_dict(row)


def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar_produto(id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        """
        UPDATE produtos
        SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
        WHERE id = ?
        """,
        (nome, descricao, preco, estoque, categoria, id),
    )
    db.commit()


def deletar_produto(id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (id,))
    db.commit()


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = f"%{termo}%"
        params.extend([like, like])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max:
        query += " AND preco <= ?"
        params.append(preco_max)
    rows = get_db().execute(query, params).fetchall()
    return [_para_dict(row) for row in rows]
