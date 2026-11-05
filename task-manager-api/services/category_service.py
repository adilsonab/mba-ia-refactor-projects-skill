"""Casos de uso de categorias."""
import logging

from middlewares.error_handler import NotFoundError
from models.category import Category
from models.task import Task

logger = logging.getLogger(__name__)


def get_category(category_id):
    category = Category.get_by_id(category_id)
    if category is None:
        raise NotFoundError("Categoria não encontrada")
    return category


def list_categories_with_task_counts():
    counts = Task.count_by_category()
    return [(category, counts.get(category.id, 0)) for category in Category.list_all()]


def create_category(name, description, color):
    category = Category(name=name, description=description, color=color)
    category.save()
    logger.info("Categoria criada: %s", category.id)
    return category


def update_category(category, changes):
    for field, value in changes.items():
        setattr(category, field, value)
    category.save()
    return category


def delete_category(category):
    category_id = category.id
    category.delete()  # tasks da categoria ficam sem categoria (category_id = NULL)
    logger.info("Categoria deletada: %s", category_id)
