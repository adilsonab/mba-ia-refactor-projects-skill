from database import db
from utils.helpers import DEFAULT_COLOR, utc_now


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=utc_now)

    tasks = db.relationship('Task', back_populates='category')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': str(self.created_at),
        }

    @classmethod
    def get_by_id(cls, category_id):
        return db.session.get(cls, category_id)

    @classmethod
    def list_all(cls):
        return db.session.execute(db.select(cls).order_by(cls.id)).scalars().all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(db.select(db.func.count(cls.id)))

    def delete_unlinking_tasks(self):
        """Desvincula as tasks (category_id = NULL) e remove a categoria na mesma transação."""
        from models.task import Task  # import local: evita ciclo entre models
        try:
            db.session.execute(db.update(Task).where(Task.category_id == self.id).values(category_id=None))
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
