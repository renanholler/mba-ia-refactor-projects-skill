from datetime import datetime, timedelta, timezone
import re

VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PASSWORD_LENGTH = 4
MIN_PRIORITY = 1
MAX_PRIORITY = 5
HIGH_PRIORITY_MAX = 2
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"
RECENT_WINDOW_DAYS = 7
CLOSED_STATUSES = ("done", "cancelled")


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    if re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email):
        return True
    return False


def recent_since():
    return utc_now() - timedelta(days=RECENT_WINDOW_DAYS)


def title_error(title, required):
    if required and not title:
        return "Título é obrigatório"
    if title is None:
        return None
    if len(title) < MIN_TITLE_LENGTH:
        return "Título muito curto"
    if len(title) > MAX_TITLE_LENGTH:
        return "Título muito longo"
    return None

