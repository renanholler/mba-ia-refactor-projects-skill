from flask import current_app, jsonify, request
from sqlalchemy.orm import subqueryload

from database import db
from models.task import Task
from models.user import User
from utils.helpers import (
    MIN_PASSWORD_LENGTH,
    VALID_ROLES,
    format_date,
    validate_email,
)


def list_users():
    users = User.query.options(subqueryload(User.tasks)).all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "active": user.active,
            "created_at": str(user.created_at),
            "task_count": len(user.tasks),
        })
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data["tasks"] = [task.to_dict() for task in tasks]
    return jsonify(data), 200


def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400
    if not password:
        return jsonify({"error": "Senha é obrigatória"}), 400
    if not validate_email(email):
        return jsonify({"error": "Email inválido"}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": "Senha deve ter no mínimo 4 caracteres"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email já cadastrado"}), 409
    if role not in VALID_ROLES:
        return jsonify({"error": "Role inválido"}), 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao criar usuário")
        return jsonify({"error": "Erro ao criar usuário"}), 500

    current_app.logger.info("Usuário criado: %s - %s", user.id, user.name)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        if not validate_email(data["email"]):
            return jsonify({"error": "Email inválido"}), 400
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "Email já cadastrado"}), 409
        user.email = data["email"]

    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            return jsonify({"error": "Senha muito curta"}), 400
        user.set_password(data["password"])

    if "role" in data:
        if data["role"] not in VALID_ROLES:
            return jsonify({"error": "Role inválido"}), 400
        user.role = data["role"]

    if "active" in data:
        user.active = data["active"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao atualizar usuário")
        return jsonify({"error": "Erro ao atualizar"}), 500

    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    for task in tasks:
        db.session.delete(task)

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao deletar usuário")
        return jsonify({"error": "Erro ao deletar"}), 500

    current_app.logger.info("Usuário deletado: %s", user_id)
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    result = []
    for task in Task.query.filter_by(user_id=user_id).all():
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "created_at": str(task.created_at),
            "due_date": format_date(task.due_date),
            "overdue": task.is_overdue(),
        })
    return jsonify(result), 200


def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401
    if not user.active:
        db.session.rollback()
        return jsonify({"error": "Usuário inativo"}), 403

    db.session.commit()
    return jsonify({
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
    }), 200
