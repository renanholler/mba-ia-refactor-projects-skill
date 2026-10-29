import secrets
from functools import wraps

from flask import current_app, jsonify, request


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not _token_matches():
            return jsonify({"error": "Não autorizado"}), 401
        return view(*args, **kwargs)

    return wrapper


def _token_matches():
    expected = current_app.config["ADMIN_TOKEN"]
    header = request.headers.get("Authorization", "")
    token = header[7:] if header.startswith("Bearer ") else ""
    if len(token) != len(expected):
        return False
    return secrets.compare_digest(token, expected)
