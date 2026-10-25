import os
from dataclasses import dataclass
from typing import Optional


def _flag(name, default):
    raw = os.environ.get(name, default)
    return raw.strip().lower() in ("1", "true", "yes")


def _optional(name):
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return None
    return raw


@dataclass(frozen=True)
class Settings:
    secret_key: str
    debug: bool
    host: str
    port: int
    db_path: str
    ambiente: str
    versao: str
    seed_admin_password: Optional[str]
    seed_joao_password: Optional[str]
    seed_maria_password: Optional[str]


def load_settings():
    return Settings(
        secret_key=os.environ.get("SECRET_KEY") or "dev-only-change-me",
        debug=_flag("DEBUG", "true"),
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        db_path=os.environ.get("DATABASE_PATH", "loja.db"),
        ambiente=os.environ.get("AMBIENTE", "producao"),
        versao="1.0.0",
        seed_admin_password=_optional("SEED_ADMIN_PASSWORD"),
        seed_joao_password=_optional("SEED_JOAO_PASSWORD"),
        seed_maria_password=_optional("SEED_MARIA_PASSWORD"),
    )
