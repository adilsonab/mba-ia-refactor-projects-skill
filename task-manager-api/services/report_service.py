"""Relatórios agregados (consultas com GROUP BY em vez de contagens em loop)."""
from datetime import timedelta

from config.constants import (
    HIGH_PRIORITY_MAX,
    PRIORITY_LABELS,
    RECENT_ACTIVITY_DAYS,
    STATUS_DONE,
    TASK_STATUSES,
)
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, utcnow


def summary_report():
    now = utcnow()
    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
    by_status = Task.count_by_status()
    by_priority = Task.count_by_priority()
    overdue_tasks = Task.list_overdue(now)
    completion = Task.completion_by_user()

    user_productivity = []
    for user in User.list_all():
        total, completed = completion.get(user.id, (0, 0))
        user_productivity.append({
            "user_id": user.id,
            "user_name": user.name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": calculate_percentage(completed, total),
        })

    return {
        "generated_at": str(now),
        "overview": {
            "total_tasks": Task.count(),
            "total_users": User.count(),
            "total_categories": Category.count(),
        },
        "tasks_by_status": {status: by_status.get(status, 0) for status in TASK_STATUSES},
        "tasks_by_priority": {label: by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()},
        "overdue": {
            "count": len(overdue_tasks),
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": str(task.due_date),
                    "days_overdue": (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        "recent_activity": {
            "tasks_created_last_7_days": Task.count(Task.created_at >= since),
            "tasks_completed_last_7_days": Task.count(Task.status == STATUS_DONE, Task.updated_at >= since),
        },
        "user_productivity": user_productivity,
    }


def user_report(user):
    now = utcnow()
    by_status = Task.count_by_status(user_id=user.id)
    total = Task.count(Task.user_id == user.id)
    done = by_status.get(STATUS_DONE, 0)
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": by_status.get("pending", 0),
            "in_progress": by_status.get("in_progress", 0),
            "cancelled": by_status.get("cancelled", 0),
            "overdue": Task.count(Task.user_id == user.id, Task.overdue_condition(now)),
            "high_priority": Task.count(Task.user_id == user.id, Task.priority <= HIGH_PRIORITY_MAX),
            "completion_rate": calculate_percentage(done, total),
        },
    }
