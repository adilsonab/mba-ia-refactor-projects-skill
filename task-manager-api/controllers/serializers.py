"""Formato das respostas (presenters). Campos sensíveis nunca saem daqui."""
from utils.helpers import utc_now


def task_detail(task, now=None):
    data = task.to_dict()
    data['overdue'] = task.is_overdue(now or utc_now())
    return data


def task_list_item(task, now):
    data = task_detail(task, now)
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def user_task_item(task, now):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'overdue': task.is_overdue(now),
    }


def user_with_task_count(user, task_count):
    data = user.to_dict()
    data['task_count'] = task_count
    return data


def category_with_task_count(category, task_count):
    data = category.to_dict()
    data['task_count'] = task_count
    return data
