"""Autenticação por `Authorization: Bearer <token>` e autorização por papel (lido do banco)."""
from functools import wraps

from flask import g, request

from services import auth_service
from utils.errors import ForbiddenError, UnauthorizedError


def _authenticate():
    scheme, _, token = request.headers.get('Authorization', '').partition(' ')
    if scheme.lower() != 'bearer' or not token.strip():
        raise UnauthorizedError('Autenticação necessária')
    g.current_user = auth_service.user_from_token(token.strip())
    return g.current_user


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
            raise ForbiddenError('Acesso restrito a administradores')
        return view(*args, **kwargs)
    return wrapper


def optional_user():
    """Usuário autenticado ou None (cadastro público só aceita `role` vindo de um admin)."""
    if not request.headers.get('Authorization'):
        return None
    try:
        return _authenticate()
    except UnauthorizedError:
        return None


def ensure_self_or_admin(user_id):
    current = g.current_user
    if current.id != user_id and not current.is_admin():
        raise ForbiddenError('Acesso negado')
