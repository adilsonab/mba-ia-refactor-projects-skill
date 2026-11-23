"""Casos de uso de usuários."""
import logging

import database
from models.task import Task
from models.user import User
from utils.errors import ConflictError, NotFoundError, ValidationError
from utils.helpers import VALID_ROLES

logger = logging.getLogger(__name__)


def get_user(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')
    return user


def list_users_with_task_count():
    totals = Task.totals_per_user()
    return [(user, totals.get(user.id, (0, 0))[0]) for user in User.list_all()]


def list_user_tasks(user_id):
    get_user(user_id)
    return Task.list_by_user(user_id)


def _ensure_email_available(email, current_user_id=None):
    existing = User.get_by_email(email)
    if existing is not None and existing.id != current_user_id:
        raise ConflictError('Email já cadastrado')


def _ensure_valid_role(role):
    if role not in VALID_ROLES:
        raise ValidationError('Role inválido')


def create_user(name, email, password, role):
    _ensure_email_available(email)
    _ensure_valid_role(role)
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    database.save(user)
    logger.info('Usuário criado: %s', user.id)
    return user


def update_user(user_id, changes):
    user = get_user(user_id)
    if 'email' in changes:
        _ensure_email_available(changes['email'], current_user_id=user_id)
    if 'role' in changes:
        _ensure_valid_role(changes['role'])
    for name in ('name', 'email', 'role', 'active'):
        if name in changes:
            setattr(user, name, changes[name])
    if 'password' in changes:
        user.set_password(changes['password'])
    database.commit()
    return user


def delete_user(user_id):
    user = get_user(user_id)
    database.delete(user)          # tasks do usuário removidas em cascata na mesma transação
    logger.info('Usuário deletado: %s', user_id)
