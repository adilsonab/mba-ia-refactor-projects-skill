"""Constantes de negócio e funções utilitárias puras."""
import re
from datetime import datetime, timezone

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
CLOSED_STATUSES = ('done', 'cancelled')
DEFAULT_STATUS = 'pending'
VALID_ROLES = ['user', 'admin', 'manager']
DEFAULT_ROLE = 'user'
ADMIN_ROLE = 'admin'
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
MIN_PRIORITY = 1
MAX_PRIORITY = 5
HIGH_PRIORITY_THRESHOLD = 2          # prioridade <= 2 conta como "alta" no relatório do usuário
RECENT_ACTIVITY_DAYS = 7
DEFAULT_COLOR = '#000000'
DATE_FORMAT = '%Y-%m-%d'

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')
COLOR_PATTERN = re.compile(r'^#[0-9a-fA-F]{6}$')


def utc_now():
    """UTC "naive" (compatível com os datetimes já gravados no SQLite e com o formato str() das respostas)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return isinstance(email, str) and EMAIL_PATTERN.match(email) is not None


def is_valid_color(color):
    return isinstance(color, str) and COLOR_PATTERN.match(color) is not None
