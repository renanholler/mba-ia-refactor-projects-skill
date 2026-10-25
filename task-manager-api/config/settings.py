import os


def _flag(name, default):
    raw = os.environ.get(name, default)
    return raw.strip().lower() in ("1", "true", "yes")


def load_settings():
    return {
        "secret_key": os.environ.get("SECRET_KEY") or "dev-only-change-me",
        "database_uri": os.environ.get("DATABASE_URL") or "sqlite:///tasks.db",
        "debug": _flag("DEBUG", "true"),
        "host": os.environ.get("HOST", "0.0.0.0"),
        "port": int(os.environ.get("PORT", "5000")),
    }
