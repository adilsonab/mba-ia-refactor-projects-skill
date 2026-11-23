"""Autenticação (Bearer token assinado) e autorização por papel lido do banco."""
from functools import wraps

from flask import g, request

from config.constants import TIPO_ADMIN
from errors import ForbiddenError, UnauthorizedError
from services import auth_service


def _authenticate():
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise UnauthorizedError("Autenticação necessária")
    g.current_user = auth_service.usuario_do_token(token.strip())


def is_admin(usuario):
    return usuario.get("tipo") == TIPO_ADMIN


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        _authenticate()
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        _authenticate()
        if not is_admin(g.current_user):
            raise ForbiddenError("Acesso restrito a administradores")
        return view(*args, **kwargs)
    return wrapper


def ensure_self_or_admin(usuario_id):
    if g.current_user["id"] != usuario_id and not is_admin(g.current_user):
        raise ForbiddenError("Acesso negado")
