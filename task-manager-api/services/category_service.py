"""Casos de uso de categorias."""
import logging

import database
from models.category import Category
from models.task import Task
from utils.errors import NotFoundError

logger = logging.getLogger(__name__)


def get_category(category_id):
    category = Category.get_by_id(category_id)
    if category is None:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories_with_task_count():
    counts = Task.count_per_category()
    return [(category, counts.get(category.id, 0)) for category in Category.list_all()]


def create_category(fields):
    category = Category(**fields)
    database.save(category)
    return category


def update_category(category_id, changes):
    category = get_category(category_id)
    for name, value in changes.items():
        setattr(category, name, value)
    database.commit()
    return category


def delete_category(category_id):
    get_category(category_id).delete_unlinking_tasks()
    logger.info('Categoria deletada: %s', category_id)
