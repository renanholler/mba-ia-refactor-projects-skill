from src.database import get_db

_COLUNAS = """
    SELECT
        p.id AS pedido_id,
        p.usuario_id,
        p.status,
        p.total,
        p.criado_em,
        i.produto_id,
        i.quantidade,
        i.preco_unitario,
        pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def criar_pedido(usuario_id, itens):
    db = get_db()
    try:
        total = 0
        conferidos = []
        for item in itens:
            produto = db.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
                (item["produto_id"],),
            ).fetchone()
            if produto is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            total = total + (produto["preco"] * item["quantidade"])
            conferidos.append((item, produto))

        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid
        for item, produto in conferidos:
            db.execute(
                """
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        db.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        db.rollback()
        raise


def get_pedidos_usuario(usuario_id):
    rows = get_db().execute(
        _COLUNAS + " WHERE p.usuario_id = ? ORDER BY p.id, i.id",
        (usuario_id,),
    ).fetchall()
    return _agrupar(rows)


def get_todos_pedidos():
    rows = get_db().execute(_COLUNAS + " ORDER BY p.id, i.id").fetchall()
    return _agrupar(rows)


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    db.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()


def _agrupar(rows):
    pedidos = []
    indice = {}
    for row in rows:
        pedido_id = row["pedido_id"]
        if pedido_id not in indice:
            pedido = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            indice[pedido_id] = pedido
            pedidos.append(pedido)
        if row["produto_id"] is None:
            continue
        nome = row["produto_nome"]
        indice[pedido_id]["itens"].append({
            "produto_id": row["produto_id"],
            "produto_nome": nome if nome else "Desconhecido",
            "quantidade": row["quantidade"],
            "preco_unitario": row["preco_unitario"],
        })
    return pedidos
