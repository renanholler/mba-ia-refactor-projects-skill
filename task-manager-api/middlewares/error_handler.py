from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return error

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Falha inesperada")
        db.session.rollback()
        return jsonify({"error": "Erro interno"}), 500
