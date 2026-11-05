"""Casos de uso de usuários e autenticação."""
import logging

from config.constants import LEGACY_TOKEN_PREFIX
from middlewares.error_handler import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from models.task import Task
from models.user import User

logger = logging.getLogger(__name__)


def get_user(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        raise NotFoundError("Usuário não encontrado")
    return user


def list_users_with_task_counts():
    counts = Task.count_by_user()
    return [(user, counts.get(user.id, 0)) for user in User.list_all()]


def get_user_tasks(user):
    return Task.list_by_user(user.id)


def _ensure_email_available(email, current_user_id=None):
    existing = User.get_by_email(email)
    if existing is not None and existing.id != current_user_id:
        raise ConflictError("Email já cadastrado")


def create_user(name, email, password, role):
    _ensure_email_available(email)
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    user.save()
    logger.info("Usuário criado: %s", user.id)
    return user


def update_user(user, changes):
    if "email" in changes:
        _ensure_email_available(changes["email"], current_user_id=user.id)
    password = changes.pop("password", None)
    if password is not None:
        user.set_password(password)
    for field, value in changes.items():
        setattr(user, field, value)
    user.save()
    return user


def delete_user(user):
    user_id = user.id
    user.delete()  # tasks do usuário removidas na mesma transação (cascade no model)
    logger.info("Usuário deletado: %s", user_id)


def authenticate(email, password):
    user = User.get_by_email(email)
    if user is None:
        raise UnauthorizedError("Credenciais inválidas")
    previous_hash = user.password
    if not user.check_password(password):
        raise UnauthorizedError("Credenciais inválidas")
    if user.password != previous_hash:  # hash legado migrado no login
        user.save()
    if not user.active:
        raise ForbiddenError("Usuário inativo")
    return user


def issue_token(user):
    # Token legado mantido por compatibilidade de contrato (não é verificado). Ver pendências.
    return LEGACY_TOKEN_PREFIX + str(user.id)
