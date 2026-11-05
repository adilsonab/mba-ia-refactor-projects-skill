"""Validação de entrada centralizada (mesmas regras em create e update)."""
from datetime import datetime

from flask import request

from config.constants import (
    DEFAULT_CATEGORY_COLOR,
    DEFAULT_PRIORITY,
    DEFAULT_ROLE,
    DEFAULT_TASK_STATUS,
    DUE_DATE_FORMAT,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    TAGS_SEPARATOR,
    TASK_STATUSES,
    USER_ROLES,
)
from middlewares.error_handler import ValidationError
from utils.helpers import validate_email

PRIORITY_ERROR = f"Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}"
DATE_ERROR = "Formato de data inválido. Use YYYY-MM-DD"
PASSWORD_ERROR = f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres"


def json_body(allow_empty=False):
    data = request.get_json()
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise ValidationError("Dados inválidos")
    return data


def query_int(name, message):
    raw = request.args.get(name, "")
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValidationError(message) from None


# ---- tasks -----------------------------------------------------------------
def _title(value):
    if not isinstance(value, str):
        raise ValidationError("Título inválido")
    if len(value) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(value) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")
    return value


def _optional_text(value, message):
    if value is not None and not isinstance(value, str):
        raise ValidationError(message)
    return value


def _status(value):
    if not isinstance(value, str) or value not in TASK_STATUSES:
        raise ValidationError("Status inválido")
    return value


def _priority(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(PRIORITY_ERROR)
    if isinstance(value, float):
        if not value.is_integer():
            raise ValidationError(PRIORITY_ERROR)
        value = int(value)
    if not MIN_PRIORITY <= value <= MAX_PRIORITY:
        raise ValidationError(PRIORITY_ERROR)
    return value


def _due_date(value):
    if not value:
        return None
    if not isinstance(value, str):
        raise ValidationError(DATE_ERROR)
    try:
        return datetime.strptime(value, DUE_DATE_FORMAT)
    except ValueError:
        raise ValidationError(DATE_ERROR) from None


def _tags(value):
    if isinstance(value, list):
        return TAGS_SEPARATOR.join(str(tag) for tag in value)
    if value is None or isinstance(value, str):
        return value
    raise ValidationError("Tags inválidas")


def task_create_payload(data):
    title = data.get("title")
    if not title:
        raise ValidationError("Título é obrigatório")
    fields = {
        "title": _title(title),
        "description": _optional_text(data.get("description", ""), "Descrição inválida"),
        "status": _status(data.get("status", DEFAULT_TASK_STATUS)),
        "priority": _priority(data.get("priority", DEFAULT_PRIORITY)),
        "user_id": data.get("user_id"),
        "category_id": data.get("category_id"),
        "due_date": _due_date(data.get("due_date")),
        "tags": _tags(data.get("tags")) or None,
    }
    return fields


def task_update_payload(data):
    changes = {}
    if "title" in data:
        changes["title"] = _title(data["title"])
    if "description" in data:
        changes["description"] = _optional_text(data["description"], "Descrição inválida")
    if "status" in data:
        changes["status"] = _status(data["status"])
    if "priority" in data:
        changes["priority"] = _priority(data["priority"])
    if "user_id" in data:
        changes["user_id"] = data["user_id"]
    if "category_id" in data:
        changes["category_id"] = data["category_id"]
    if "due_date" in data:
        changes["due_date"] = _due_date(data["due_date"])
    if "tags" in data:
        changes["tags"] = _tags(data["tags"])
    return changes


# ---- usuários --------------------------------------------------------------
def _name(value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Nome é obrigatório")
    return value


def _email(value):
    if not validate_email(value):
        raise ValidationError("Email inválido")
    return value


def _password(value):
    if not isinstance(value, str) or len(value) < MIN_PASSWORD_LENGTH:
        raise ValidationError(PASSWORD_ERROR)
    return value


def _role(value):
    if not isinstance(value, str) or value not in USER_ROLES:
        raise ValidationError("Role inválido")
    return value


def user_create_payload(data):
    if not data.get("name"):
        raise ValidationError("Nome é obrigatório")
    if not data.get("email"):
        raise ValidationError("Email é obrigatório")
    if not data.get("password"):
        raise ValidationError("Senha é obrigatória")
    return {
        "name": _name(data["name"]),
        "email": _email(data["email"]),
        "password": _password(data["password"]),
        "role": _role(data.get("role", DEFAULT_ROLE)),
    }


def user_update_payload(data):
    changes = {}
    if "name" in data:
        changes["name"] = _name(data["name"])
    if "email" in data:
        changes["email"] = _email(data["email"])
    if "password" in data:
        changes["password"] = _password(data["password"])
    if "role" in data:
        changes["role"] = _role(data["role"])
    if "active" in data:
        if not isinstance(data["active"], bool):
            raise ValidationError("Campo active inválido")
        changes["active"] = data["active"]
    return changes


def login_payload(data):
    email, password = data.get("email"), data.get("password")
    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        raise ValidationError("Email e senha são obrigatórios")
    return email, password


# ---- categorias ------------------------------------------------------------
def category_create_payload(data):
    if not data.get("name"):
        raise ValidationError("Nome é obrigatório")
    return {
        "name": _name(data["name"]),
        "description": _optional_text(data.get("description", ""), "Descrição inválida"),
        "color": _optional_text(data.get("color", DEFAULT_CATEGORY_COLOR), "Cor inválida"),
    }


def category_update_payload(data):
    changes = {}
    if "name" in data:
        changes["name"] = _name(data["name"])
    if "description" in data:
        changes["description"] = _optional_text(data["description"], "Descrição inválida")
    if "color" in data:
        changes["color"] = _optional_text(data["color"], "Cor inválida")
    return changes
