from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database import db
from utils.helpers import CLOSED_STATUSES, DEFAULT_PRIORITY, DEFAULT_STATUS, utc_now


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=DEFAULT_STATUS)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', back_populates='tasks')
    category = db.relationship('Category', back_populates='tasks')

    # ---------- regras da entidade ----------
    def is_overdue(self, now=None):
        now = now or utc_now()
        return bool(self.due_date) and self.due_date < now and self.status not in CLOSED_STATUSES

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    # ---------- acesso a dados ----------
    @staticmethod
    def _overdue_filter(now):
        return db.and_(Task.due_date.isnot(None), Task.due_date < now, Task.status.notin_(CLOSED_STATUSES))

    @classmethod
    def get_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_with_relations(cls):
        stmt = db.select(cls).options(joinedload(cls.user), joinedload(cls.category)).order_by(cls.id)
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def list_by_user(cls, user_id):
        return db.session.execute(db.select(cls).filter_by(user_id=user_id).order_by(cls.id)).scalars().all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        stmt = db.select(cls)
        if text:
            pattern = f'%{text}%'
            stmt = stmt.where(or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            stmt = stmt.where(cls.status == status)
        if priority is not None:
            stmt = stmt.where(cls.priority == priority)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        return db.session.execute(stmt.order_by(cls.id)).scalars().all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(db.select(func.count(cls.id)))

    @classmethod
    def count_by(cls, column):
        rows = db.session.execute(db.select(column, func.count(cls.id)).group_by(column)).all()
        return {key: count for key, count in rows}

    @classmethod
    def count_by_status(cls):
        return cls.count_by(cls.status)

    @classmethod
    def count_by_priority(cls):
        return cls.count_by(cls.priority)

    @classmethod
    def count_overdue(cls, now):
        return db.session.scalar(db.select(func.count(cls.id)).where(cls._overdue_filter(now)))

    @classmethod
    def list_overdue(cls, now):
        return db.session.execute(db.select(cls).where(cls._overdue_filter(now)).order_by(cls.id)).scalars().all()

    @classmethod
    def count_created_since(cls, since):
        return db.session.scalar(db.select(func.count(cls.id)).where(cls.created_at >= since))

    @classmethod
    def count_done_updated_since(cls, since):
        stmt = db.select(func.count(cls.id)).where(cls.status == 'done', cls.updated_at >= since)
        return db.session.scalar(stmt)

    @classmethod
    def totals_per_user(cls):
        """{user_id: (total, concluídas)} em uma única query agregada."""
        done = func.sum(db.case((cls.status == 'done', 1), else_=0))
        rows = db.session.execute(db.select(cls.user_id, func.count(cls.id), done).group_by(cls.user_id)).all()
        return {user_id: (total, int(completed or 0)) for user_id, total, completed in rows}

    @classmethod
    def count_per_category(cls):
        return cls.count_by(cls.category_id)
