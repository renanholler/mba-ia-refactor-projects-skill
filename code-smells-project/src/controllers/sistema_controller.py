from flask import current_app, jsonify

from src.models import saude as saude_model


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": current_app.extensions["settings"].versao,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    settings = current_app.extensions["settings"]
    counts = saude_model.contagens()
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": settings.versao,
        "ambiente": settings.ambiente,
        "db_path": settings.db_path,
        "debug": settings.debug,
    }), 200


def reset_database():
    return jsonify({"erro": "Operação não permitida", "sucesso": False}), 403


def executar_query():
    return jsonify({"erro": "Operação não permitida", "sucesso": False}), 403
