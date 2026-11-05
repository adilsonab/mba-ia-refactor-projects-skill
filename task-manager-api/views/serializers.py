"""Formato das respostas (camada View). Mantém exatamente as chaves do contrato original."""
from utils.helpers import utcnow


def task_detail(task, now=None):
    data = task.to_dict()
    data["overdue"] = task.is_overdue(now or utcnow())
    return data


def task_list(tasks):
    now = utcnow()
    result = []
    for task in tasks:
        data = task_detail(task, now)
        data["user_name"] = task.user.name if task.user else None
        data["category_name"] = task.category.name if task.category else None
        result.append(data)
    return result


def task_basic_list(tasks):
    return [task.to_dict() for task in tasks]


def user_task_list(tasks):
    now = utcnow()
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "created_at": str(task.created_at),
            "due_date": str(task.due_date) if task.due_date else None,
            "overdue": task.is_overdue(now),
        }
        for task in tasks
    ]


def user_list(users_with_counts):
    result = []
    for user, task_count in users_with_counts:
        data = user.to_dict()
        data["task_count"] = task_count
        result.append(data)
    return result


def user_detail(user, tasks):
    data = user.to_dict()
    data["tasks"] = task_basic_list(tasks)
    return data


def login_response(user, token):
    return {"message": "Login realizado com sucesso", "user": user.to_dict(), "token": token}


def category_list(categories_with_counts):
    result = []
    for category, task_count in categories_with_counts:
        data = category.to_dict()
        data["task_count"] = task_count
        result.append(data)
    return result
