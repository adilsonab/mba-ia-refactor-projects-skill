"""Casos de uso de tasks."""
import logging

import database
from models.category import Category
from models.task import Task
from models.user import User
from utils.errors import NotFoundError
from utils.helpers import calculate_percentage, utc_now

logger = logging.getLogger(__name__)


def get_task(task_id):
    task = Task.get_by_id(task_id)
    if task is None:
        raise NotFoundError('Task não encontrada')
    return task


def list_tasks():
    return Task.list_with_relations()


def _ensure_references(fields):
    if fields.get('user_id') and User.get_by_id(fields['user_id']) is None:
        raise NotFoundError('Usuário não encontrado')
    if fields.get('category_id') and Category.get_by_id(fields['category_id']) is None:
        raise NotFoundError('Categoria não encontrada')


def create_task(fields):
    _ensure_references(fields)
    task = Task(**fields)
    database.save(task)
    logger.info('Task criada: %s - %s', task.id, task.title)
    return task


def update_task(task_id, changes):
    task = get_task(task_id)
    _ensure_references(changes)
    for name, value in changes.items():
        setattr(task, name, value)
    task.updated_at = utc_now()
    database.commit()
    logger.info('Task atualizada: %s', task.id)
    return task


def delete_task(task_id):
    task = get_task(task_id)
    database.delete(task)
    logger.info('Task deletada: %s', task_id)


def search_tasks(text, status, priority, user_id):
    return Task.search(text=text, status=status, priority=priority, user_id=user_id)


def task_stats():
    total = Task.count_all()
    by_status = Task.count_by_status()
    done = by_status.get('done', 0)
    return {
        'total': total,
        'pending': by_status.get('pending', 0),
        'in_progress': by_status.get('in_progress', 0),
        'done': done,
        'cancelled': by_status.get('cancelled', 0),
        'overdue': Task.count_overdue(utc_now()),
        'completion_rate': calculate_percentage(done, total),
    }
