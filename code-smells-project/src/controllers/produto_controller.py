from flask import jsonify, request

from src.models import produto as produto_model

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
NOME_MIN_LENGTH = 2
NOME_MAX_LENGTH = 200


def listar_produtos():
    produtos = produto_model.get_todos_produtos()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_model.get_produto_por_id(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def criar_produto():
    erro, campos = validar_produto(request.get_json())
    if erro:
        return erro
    novo_id = produto_model.criar_produto(
        campos["nome"],
        campos["descricao"],
        campos["preco"],
        campos["estoque"],
        campos["categoria"],
    )
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    if not produto_model.get_produto_por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    erro, campos = validar_produto(request.get_json())
    if erro:
        return erro
    produto_model.atualizar_produto(
        id,
        campos["nome"],
        campos["descricao"],
        campos["preco"],
        campos["estoque"],
        campos["categoria"],
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not produto_model.get_produto_por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_model.deletar_produto(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)
    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)
    resultados = produto_model.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def validar_produto(dados):
    if not dados:
        return (jsonify({"erro": "Dados inválidos"}), 400), None
    if "nome" not in dados:
        return (jsonify({"erro": "Nome é obrigatório"}), 400), None
    if "preco" not in dados:
        return (jsonify({"erro": "Preço é obrigatório"}), 400), None
    if "estoque" not in dados:
        return (jsonify({"erro": "Estoque é obrigatório"}), 400), None

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        return (jsonify({"erro": "Preço não pode ser negativo"}), 400), None
    if estoque < 0:
        return (jsonify({"erro": "Estoque não pode ser negativo"}), 400), None
    if len(nome) < NOME_MIN_LENGTH:
        return (jsonify({"erro": "Nome muito curto"}), 400), None
    if len(nome) > NOME_MAX_LENGTH:
        return (jsonify({"erro": "Nome muito longo"}), 400), None
    if categoria not in CATEGORIAS_VALIDAS:
        return (
            jsonify({"erro": "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)}),
            400,
        ), None

    return None, {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }
