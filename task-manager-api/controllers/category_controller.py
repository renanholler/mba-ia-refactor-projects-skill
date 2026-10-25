from flask import current_app, jsonify, request
from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from utils.helpers import DEFAULT_COLOR


def list_categories():
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id)).group_by(Task.category_id).all()
    )
    result = []
    for category in Category.query.all():
        data = category.to_dict()
        data["task_count"] = counts.get(category.id, 0)
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", DEFAULT_COLOR)

    try:
        db.session.add(category)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao criar categoria")
        return jsonify({"error": "Erro ao criar categoria"}), 500

    return jsonify(category.to_dict()), 201


def update_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404

    data = request.get_json()
    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao atualizar categoria")
        return jsonify({"error": "Erro ao atualizar"}), 500

    return jsonify(category.to_dict()), 200


def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404

    try:
        db.session.delete(category)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao deletar categoria")
        return jsonify({"error": "Erro ao deletar"}), 500

    return jsonify({"message": "Categoria deletada"}), 200
