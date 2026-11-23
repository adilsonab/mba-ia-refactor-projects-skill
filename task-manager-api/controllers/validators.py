"""Validação de entrada: uma única regra por campo, compartilhada por create e update."""
from datetime import datetime

from flask import request

from utils.errors import ValidationError
from utils.helpers import (DATE_FORMAT, DEFAULT_COLOR, DEFAULT_PRIORITY, DEFAULT_STATUS, MAX_PRIORITY,
                           MAX_TITLE_LENGTH, MIN_PASSWORD_LENGTH, MIN_PRIORITY, MIN_TITLE_LENGTH, VALID_STATUSES,
                           is_valid_color, validate_email)

PRIORITY_MESSAGE = 'Prioridade deve ser entre 1 e 5'


def json_body():
    data = request.get_json()
    if not data or not isinstance(data, dict):
        raise ValidationError('Dados inválidos')
    return data


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def query_int(name):
    raw = request.args.get(name, '')
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValidationError(f'Parâmetro {name} inválido') from None


# ---------- tasks ----------
def _title(value):
    if not isinstance(value, str):
        raise ValidationError('Título deve ser um texto')
    if len(value) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(value) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return value


def _status(value):
    if value not in VALID_STATUSES:
        raise ValidationError('Status inválido')
    return value


def _priority(value):
    if not _is_int(value) or not MIN_PRIORITY <= value <= MAX_PRIORITY:
        raise ValidationError(PRIORITY_MESSAGE)
    return value


def _reference_id(value, label):
    if value is None:
        return None
    if not _is_int(value):
        raise ValidationError(f'{label} inválido')
    return value


def _due_date(value, message):
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError(message) from None


def _tags(value):
    if isinstance(value, list):
        if not all(isinstance(tag, str) for tag in value):
            raise ValidationError('Tags inválidas')
        return ','.join(value)
    if value is None or isinstance(value, str):
        return value or None
    raise ValidationError('Tags inválidas')


def task_create_payload(data):
    title = data.get('title')
    if not title:
        raise ValidationError('Título é obrigatório')
    description = data.get('description', '')
    if description is not None and not isinstance(description, str):
        raise ValidationError('Descrição inválida')
    return {
        'title': _title(title),
        'description': description,
        'status': _status(data.get('status', DEFAULT_STATUS)),
        'priority': _priority(data.get('priority', DEFAULT_PRIORITY)),
        'user_id': _reference_id(data.get('user_id'), 'user_id') or None,
        'category_id': _reference_id(data.get('category_id'), 'category_id') or None,
        'due_date': _due_date(data.get('due_date'), 'Formato de data inválido. Use YYYY-MM-DD'),
        'tags': _tags(data.get('tags')),
    }


def task_update_payload(data):
    changes = {}
    if 'title' in data:
        changes['title'] = _title(data['title'])
    if 'description' in data:
        if data['description'] is not None and not isinstance(data['description'], str):
            raise ValidationError('Descrição inválida')
        changes['description'] = data['description']
    if 'status' in data:
        changes['status'] = _status(data['status'])
    if 'priority' in data:
        changes['priority'] = _priority(data['priority'])
    if 'user_id' in data:
        changes['user_id'] = _reference_id(data['user_id'], 'user_id')
    if 'category_id' in data:
        changes['category_id'] = _reference_id(data['category_id'], 'category_id')
    if 'due_date' in data:
        changes['due_date'] = _due_date(data['due_date'], 'Formato de data inválido')
    if 'tags' in data:
        changes['tags'] = _tags(data['tags'])
    return changes


# ---------- usuários ----------
def _required_text(data, name, message):
    value = data.get(name)
    if not value or not isinstance(value, str):
        raise ValidationError(message)
    return value


def _email(value):
    if not validate_email(value):
        raise ValidationError('Email inválido')
    return value


def user_create_payload(data):
    name = _required_text(data, 'name', 'Nome é obrigatório')
    email = _required_text(data, 'email', 'Email é obrigatório')
    password = _required_text(data, 'password', 'Senha é obrigatória')
    _email(email)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError('Senha deve ter no mínimo 4 caracteres')
    return {'name': name, 'email': email, 'password': password, 'role': data.get('role')}


def user_update_payload(data):
    changes = {}
    if 'name' in data:
        changes['name'] = _required_text(data, 'name', 'Nome é obrigatório')
    if 'email' in data:
        changes['email'] = _email(data['email'])
    if 'password' in data:
        password = data['password']
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError('Senha muito curta')
        changes['password'] = password
    if 'role' in data:
        changes['role'] = data['role']
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Active deve ser booleano')
        changes['active'] = data['active']
    return changes


def login_payload(data):
    email, password = data.get('email'), data.get('password')
    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        raise ValidationError('Email e senha são obrigatórios')
    return email, password


# ---------- categorias ----------
def _color(value):
    if not is_valid_color(value):
        raise ValidationError('Cor inválida')
    return value


def _optional_text(value, message):
    if value is not None and not isinstance(value, str):
        raise ValidationError(message)
    return value


def category_create_payload(data):
    return {
        'name': _required_text(data, 'name', 'Nome é obrigatório'),
        'description': _optional_text(data.get('description', ''), 'Descrição inválida'),
        'color': _color(data.get('color', DEFAULT_COLOR)),
    }


def category_update_payload(data):
    changes = {}
    if 'name' in data:
        changes['name'] = _required_text(data, 'name', 'Nome é obrigatório')
    if 'description' in data:
        changes['description'] = _optional_text(data['description'], 'Descrição inválida')
    if 'color' in data:
        changes['color'] = _color(data['color'])
    return changes
