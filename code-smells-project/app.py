import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import load_settings
from src.database import init_db, register_db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import register_routes


def create_app():
    settings = load_settings()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["ADMIN_TOKEN"] = settings.admin_token
    app.config["DEBUG"] = settings.debug
    app.config["PROPAGATE_EXCEPTIONS"] = False
    app.extensions["settings"] = settings
    app.logger.setLevel(logging.INFO)
    CORS(app)
    init_db(settings)
    register_db(app)
    register_error_handlers(app)
    register_routes(app)
    return app


app = create_app()

if __name__ == "__main__":
    settings = app.extensions["settings"]
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.port}")
    print("=" * 50)
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
