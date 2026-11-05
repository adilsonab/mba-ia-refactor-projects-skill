"""Casos de uso de tasks."""
import logging

from config.constants import STATUS_DONE
from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, utcnow

logger = logging.getLogger(__name__)


def _coerce_id(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def resolve_user_id(value):
    """Valida a referência a um usuário. Valor vazio desassocia (None)."""
    if not value:
        return None
    user_id = _coerce_id(value)
    if user_id is None or User.get_by_id(user_id) is None:
        raise NotFoundError("Usuário não encontrado")
    return user_id


def resolve_category_id(value):
    if not value:
        return None
    category_id = _coerce_id(value)
    if category_id is None or Category.get_by_id(category_id) is None:
        raise NotFoundError("Categoria não encontrada")
    return category_id


def get_task(task_id):
    task = Task.get_by_id(task_id)
    if task is None:
        raise NotFoundError("Task não encontrada")
    return task


def list_tasks():
    return Task.list_all_with_relations()


def search_tasks(text=None, status=None, priority=None, user_id=None):
    return Task.search(text=text, status=status, priority=priority, user_id=user_id)


def create_task(fields):
    task = Task(
        title=fields["title"],
        description=fields["description"],
        status=fields["status"],
        priority=fields["priority"],
        user_id=resolve_user_id(fields.get("user_id")),
        category_id=resolve_category_id(fields.get("category_id")),
        due_date=fields.get("due_date"),
        tags=fields.get("tags"),
    )
    task.save()
    logger.info("Task criada: %s", task.id)
    return task


def update_task(task, changes):
    if "user_id" in changes:
        changes["user_id"] = resolve_user_id(changes["user_id"])
    if "category_id" in changes:
        changes["category_id"] = resolve_category_id(changes["category_id"])
    for field, value in changes.items():
        setattr(task, field, value)
    task.updated_at = utcnow()
    task.save()
    logger.info("Task atualizada: %s", task.id)
    return task


def delete_task(task):
    task_id = task.id
    task.delete()
    logger.info("Task deletada: %s", task_id)


def task_stats():
    total = Task.count()
    by_status = Task.count_by_status()
    done = by_status.get(STATUS_DONE, 0)
    return {
        "total": total,
        "pending": by_status.get("pending", 0),
        "in_progress": by_status.get("in_progress", 0),
        "done": done,
        "cancelled": by_status.get("cancelled", 0),
        "overdue": Task.count(Task.overdue_condition(utcnow())),
        "completion_rate": calculate_percentage(done, total),
    }
