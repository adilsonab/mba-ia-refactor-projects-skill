from sqlalchemy import func, select

from config.constants import ADMIN_ROLE
from database import db
from utils.helpers import utcnow
from utils.security import hash_password, verify_password


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    # Excluir um usuario exclui as tasks dele (mesmo comportamento anterior, agora declarado no model).
    tasks = db.relationship("Task", back_populates="user", cascade="save-update, merge, delete")

    def to_dict(self):
        # O hash da senha nunca e serializado.
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, raw_password):
        self.password = hash_password(raw_password)

    def check_password(self, raw_password):
        """Confere a senha; hashes legados (MD5) sao migrados para o algoritmo atual."""
        ok, needs_rehash = verify_password(self.password, raw_password)
        if ok and needs_rehash:
            self.set_password(raw_password)
        return ok

    def is_admin(self):
        return self.role == ADMIN_ROLE

    @classmethod
    def get_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def get_by_email(cls, email):
        return db.session.scalars(select(cls).where(cls.email == email)).first()

    @classmethod
    def list_all(cls):
        return db.session.scalars(select(cls).order_by(cls.id)).all()

    @classmethod
    def count(cls):
        return db.session.scalar(select(func.count(cls.id)))

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)  # o cascade remove as tasks na mesma transacao
        db.session.commit()
