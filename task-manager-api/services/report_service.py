"""Relatórios agregados."""
from datetime import timedelta

from models.category import Category
from models.task import Task
from models.user import User
from services.user_service import get_user
from utils.helpers import (HIGH_PRIORITY_THRESHOLD, RECENT_ACTIVITY_DAYS, VALID_STATUSES, calculate_percentage,
                           utc_now)

PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}


def summary_report():
    now = utc_now()
    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
    by_status = Task.count_by_status()
    by_priority = Task.count_by_priority()
    overdue_tasks = Task.list_overdue(now)
    totals = Task.totals_per_user()

    user_productivity = []
    for user in User.list_all():
        total, completed = totals.get(user.id, (0, 0))
        user_productivity.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.count_all(),
            'total_users': User.count_all(),
            'total_categories': Category.count_all(),
        },
        'tasks_by_status': {status: by_status.get(status, 0) for status in VALID_STATUSES},
        'tasks_by_priority': {label: by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()},
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(since),
            'tasks_completed_last_7_days': Task.count_done_updated_since(since),
        },
        'user_productivity': user_productivity,
    }


def user_report(user_id):
    user = get_user(user_id)
    tasks = Task.list_by_user(user_id)
    now = utc_now()
    status_counts = {status: 0 for status in VALID_STATUSES}
    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
    total = len(tasks)
    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': status_counts['done'],
            'pending': status_counts['pending'],
            'in_progress': status_counts['in_progress'],
            'cancelled': status_counts['cancelled'],
            'overdue': sum(1 for task in tasks if task.is_overdue(now)),
            'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD),
            'completion_rate': calculate_percentage(status_counts['done'], total),
        },
    }
