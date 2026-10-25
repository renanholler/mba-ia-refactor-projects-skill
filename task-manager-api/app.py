from datetime import datetime

from flask import Flask
from flask_cors import CORS

from config.settings import load_settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp

settings = load_settings()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = settings["database_uri"]
app.config["SECRET_KEY"] = settings["secret_key"]
app.config["PROPAGATE_EXCEPTIONS"] = False

CORS(app)
db.init_app(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)
app.register_blueprint(category_bp)
register_error_handlers(app)


@app.route("/health")
def health():
    return {"status": "ok", "timestamp": str(datetime.now())}


@app.route("/")
def index():
    return {"message": "Task Manager API", "version": "1.0"}


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=settings["debug"], host=settings["host"], port=settings["port"])
