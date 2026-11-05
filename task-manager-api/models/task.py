from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import joinedload

from config.constants import CLOSED_STATUSES, STATUS_DONE, TAGS_SEPARATOR
from database import db
from utils.helpers import utcnow


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship("User", back_populates="tasks")
    category = db.relationship("Category", back_populates="tasks")

    # ---- regras da entidade -------------------------------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "tags": self.tags.split(TAGS_SEPARATOR) if self.tags else [],
        }

    def is_overdue(self, now=None):
        now = now or utcnow()
        return bool(self.due_date) and self.due_date < now and self.status not in CLOSED_STATUSES

    @classmethod
    def overdue_condition(cls, now):
        return and_(cls.due_date.is_not(None), cls.due_date < now, cls.status.not_in(CLOSED_STATUSES))

    # ---- acesso a dados -----------------------------------------------------
    @classmethod
    def get_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_all_with_relations(cls):
        stmt = select(cls).options(joinedload(cls.user), joinedload(cls.category)).order_by(cls.id)
        return db.session.scalars(stmt).unique().all()

    @classmethod
    def list_by_user(cls, user_id):
        return db.session.scalars(select(cls).where(cls.user_id == user_id).order_by(cls.id)).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        stmt = select(cls)
        if text:
            pattern = f"%{text}%"  # enviado como bind parameter pelo ORM (sem interpolação no SQL)
            stmt = stmt.where(or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            stmt = stmt.where(cls.status == status)
        if priority is not None:
            stmt = stmt.where(cls.priority == priority)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        return db.session.scalars(stmt.order_by(cls.id)).all()

    @classmethod
    def list_overdue(cls, now):
        return db.session.scalars(select(cls).where(cls.overdue_condition(now)).order_by(cls.id)).all()

    @classmethod
    def count(cls, *conditions):
        return db.session.scalar(select(func.count(cls.id)).where(*conditions))

    @classmethod
    def count_by_status(cls, user_id=None):
        stmt = select(cls.status, func.count(cls.id)).group_by(cls.status)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        return dict(db.session.execute(stmt).all())

    @classmethod
    def count_by_priority(cls):
        stmt = select(cls.priority, func.count(cls.id)).group_by(cls.priority)
        return dict(db.session.execute(stmt).all())

    @classmethod
    def count_by_user(cls):
        stmt = select(cls.user_id, func.count(cls.id)).where(cls.user_id.is_not(None)).group_by(cls.user_id)
        return dict(db.session.execute(stmt).all())

    @classmethod
    def count_by_category(cls):
        stmt = (
            select(cls.category_id, func.count(cls.id))
            .where(cls.category_id.is_not(None))
            .group_by(cls.category_id)
        )
        return dict(db.session.execute(stmt).all())

    @classmethod
    def completion_by_user(cls):
        """{user_id: (total, concluidas)} em uma unica query."""
        done = func.sum(case((cls.status == STATUS_DONE, 1), else_=0))
        stmt = select(cls.user_id, func.count(cls.id), done).where(cls.user_id.is_not(None)).group_by(cls.user_id)
        return {user_id: (total, int(completed or 0)) for user_id, total, completed in db.session.execute(stmt).all()}

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
