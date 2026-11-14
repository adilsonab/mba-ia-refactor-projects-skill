"""Autenticação (Bearer token assinado) e autorização por papel lido do banco."""
from functools import wraps

from flask import g, request

from middlewares.error_handler import ForbiddenError, UnauthorizedError
from services import auth_service


def _bearer_token():
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise UnauthorizedError("Autenticação necessária")
    return token.strip()


def _authenticate():
    g.current_user = auth_service.user_from_token(_bearer_token())
    return g.current_user


def current_user():
    return g.get("current_user")


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        _authenticate()
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not _authenticate().is_admin():
            raise ForbiddenError("Acesso restrito a administradores")
        return view(*args, **kwargs)

    return wrapper


def optional_user():
    """Usuário autenticado ou None; usado no cadastro público (só admin pode escolher o papel)."""
    if not request.headers.get("Authorization"):
        return None
    return _authenticate()


def ensure_self_or_admin(user_id):
    user = current_user()
    if user is None or (user.id != user_id and not user.is_admin()):
        raise ForbiddenError("Acesso negado")


def ensure_admin():
    user = current_user()
    if user is None or not user.is_admin():
        raise ForbiddenError("Acesso restrito a administradores")
