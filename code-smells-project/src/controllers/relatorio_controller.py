from flask import jsonify

from src.models import relatorio as relatorio_model


def relatorio_vendas():
    relatorio = relatorio_model.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
