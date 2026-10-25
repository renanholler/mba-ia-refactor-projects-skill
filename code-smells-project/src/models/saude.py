from src.database import get_db


def contagens():
    db = get_db()
    produtos = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    return {
        "produtos": produtos,
        "usuarios": usuarios,
        "pedidos": pedidos,
    }
