from flask import jsonify

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import HIGH_PRIORITY_MAX, calculate_percentage, recent_since, utc_now


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()

    priority_counts = {priority: Task.query.filter_by(priority=priority).count() for priority in range(1, 6)}

    all_tasks = Task.query.all()
    overdue_list = []
    for task in all_tasks:
        if not task.is_overdue():
            continue
        overdue_list.append({
            "id": task.id,
            "title": task.title,
            "due_date": str(task.due_date),
            "days_overdue": (utc_now() - task.due_date).days,
        })

    window_start = recent_since()
    recent_tasks = Task.query.filter(Task.created_at >= window_start).count()
    recent_done = Task.query.filter(
        Task.status == "done",
        Task.updated_at >= window_start,
    ).count()

    tasks_by_user = {}
    for task in all_tasks:
        tasks_by_user.setdefault(task.user_id, []).append(task)

    user_stats = []
    for user in User.query.all():
        user_tasks = tasks_by_user.get(user.id, [])
        total = len(user_tasks)
        completed = sum(1 for task in user_tasks if task.status == "done")
        user_stats.append({
            "user_id": user.id,
            "user_name": user.name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": calculate_percentage(completed, total),
        })

    report = {
        "generated_at": str(utc_now()),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "done": done,
            "cancelled": cancelled,
        },
        "tasks_by_priority": {
            "critical": priority_counts[1],
            "high": priority_counts[2],
            "medium": priority_counts[3],
            "low": priority_counts[4],
            "minimal": priority_counts[5],
        },
        "overdue": {
            "count": len(overdue_list),
            "tasks": overdue_list,
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = 0
    pending = 0
    in_progress = 0
    cancelled = 0
    overdue = 0
    high_priority = 0

    for task in tasks:
        if task.status == "done":
            done += 1
        elif task.status == "pending":
            pending += 1
        elif task.status == "in_progress":
            in_progress += 1
        elif task.status == "cancelled":
            cancelled += 1
        if task.priority <= HIGH_PRIORITY_MAX:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    report = {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": calculate_percentage(done, total),
        },
    }
    return jsonify(report), 200
