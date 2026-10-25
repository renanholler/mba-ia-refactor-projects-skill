from datetime import datetime

from flask import current_app, jsonify, request
from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import DEFAULT_PRIORITY, title_error, utc_now


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return jsonify([_list_item(task) for task in tasks]), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return jsonify(data), 200


def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    title = data.get("title")
    error = title_error(title, required=True)
    if error:
        return jsonify({"error": error}), 400

    description = data.get("description", "")
    status = data.get("status", "pending")
    priority = data.get("priority", DEFAULT_PRIORITY)
    user_id = data.get("user_id")
    category_id = data.get("category_id")
    due_date = data.get("due_date")
    tags = data.get("tags")

    task = Task()
    if not task.validate_status(status):
        return jsonify({"error": "Status inválido"}), 400
    if not task.validate_priority(priority):
        return jsonify({"error": "Prioridade deve ser entre 1 e 5"}), 400

    if user_id:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

    if category_id:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({"error": "Categoria não encontrada"}), 404

    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        parsed = _parse_due_date(due_date)
        if parsed is None:
            return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400
        task.due_date = parsed

    if tags:
        _assign_tags(task, tags)

    try:
        db.session.add(task)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao criar task")
        return jsonify({"error": "Erro ao criar task"}), 500

    current_app.logger.info("Task criada: %s - %s", task.id, task.title)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "title" in data:
        error = title_error(data["title"], required=False)
        if error:
            return jsonify({"error": error}), 400
        task.title = data["title"]

    if "description" in data:
        task.description = data["description"]

    if "status" in data:
        if not task.validate_status(data["status"]):
            return jsonify({"error": "Status inválido"}), 400
        task.status = data["status"]

    if "priority" in data:
        if not task.validate_priority(data["priority"]):
            return jsonify({"error": "Prioridade deve ser entre 1 e 5"}), 400
        task.priority = data["priority"]

    if "user_id" in data:
        if data["user_id"]:
            user = db.session.get(User, data["user_id"])
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404
        task.user_id = data["user_id"]

    if "category_id" in data:
        if data["category_id"]:
            category = db.session.get(Category, data["category_id"])
            if not category:
                return jsonify({"error": "Categoria não encontrada"}), 404
        task.category_id = data["category_id"]

    if "due_date" in data:
        if data["due_date"]:
            parsed = _parse_due_date(data["due_date"])
            if parsed is None:
                return jsonify({"error": "Formato de data inválido"}), 400
            task.due_date = parsed
        else:
            task.due_date = None

    if "tags" in data:
        _assign_tags(task, data["tags"])

    task.updated_at = utc_now()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao atualizar task")
        return jsonify({"error": "Erro ao atualizar"}), 500

    current_app.logger.info("Task atualizada: %s", task.id)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    try:
        db.session.delete(task)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao deletar task")
        return jsonify({"error": "Erro ao deletar"}), 500

    current_app.logger.info("Task deletada: %s", task_id)
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    term = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    tasks = Task.query
    if term:
        like = f"%{term}%"
        tasks = tasks.filter(db.or_(Task.title.like(like), Task.description.like(like)))
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return jsonify([task.to_dict() for task in tasks.all()]), 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()
    overdue_count = sum(1 for task in Task.query.all() if task.is_overdue())
    stats = {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "cancelled": cancelled,
        "overdue": overdue_count,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200


def _list_item(task):
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    data["user_name"] = task.user.name if task.user else None
    data["category_name"] = task.category.name if task.category else None
    return data


def _parse_due_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def _assign_tags(task, tags):
    if type(tags) == list:
        task.tags = ",".join(tags)
    else:
        task.tags = tags
