import hashlib
import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from utils.helpers import ADMIN_ROLE, DEFAULT_ROLE, utc_now

_MODERN_HASH_PREFIXES = ('scrypt:', 'pbkdf2:')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # tasks pertencem ao usuário: excluídas junto, na mesma transação
    tasks = db.relationship('Task', back_populates='user', cascade='all, delete-orphan')

    def to_dict(self):
        """Representação pública (nunca inclui o hash da senha)."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    # ---------- senha ----------
    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        stored = self.password or ''
        if stored.startswith(_MODERN_HASH_PREFIXES):
            return check_password_hash(stored, raw)
        legacy = hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()  # migração de hashes MD5 antigos
        return hmac.compare_digest(stored, legacy)

    def password_needs_rehash(self):
        return not (self.password or '').startswith(_MODERN_HASH_PREFIXES)

    def is_admin(self):
        return self.role == ADMIN_ROLE

    # ---------- acesso a dados ----------
    @classmethod
    def get_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def get_by_email(cls, email):
        return db.session.execute(db.select(cls).filter_by(email=email)).scalar_one_or_none()

    @classmethod
    def list_all(cls):
        return db.session.execute(db.select(cls).order_by(cls.id)).scalars().all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(db.select(db.func.count(cls.id)))
