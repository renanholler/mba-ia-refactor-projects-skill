from database import db
import hashlib
import secrets

from utils.helpers import utc_now

_PBKDF2_ITERATIONS = 260000


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, password):
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), _PBKDF2_ITERATIONS
        ).hex()
        self.password = f"pbkdf2${_PBKDF2_ITERATIONS}${salt}${digest}"

    def check_password(self, password):
        stored = self.password or ""
        if stored.startswith("pbkdf2$"):
            return _verify_pbkdf2(stored, password)
        legacy = hashlib.md5(password.encode()).hexdigest()
        if len(stored) == len(legacy) and secrets.compare_digest(stored, legacy):
            self.set_password(password)
            return True
        return False

    def is_admin(self):
        return self.role == "admin"


def _verify_pbkdf2(stored, password):
    parts = stored.split("$")
    if len(parts) != 4:
        return False
    try:
        iterations = int(parts[1])
    except ValueError:
        return False
    salt = parts[2]
    digest = parts[3]
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), iterations
    ).hex()
    if len(check) != len(digest):
        return False
    return secrets.compare_digest(check, digest)
