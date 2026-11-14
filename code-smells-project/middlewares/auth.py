"""Authentication (signed Bearer token) and role-based authorization (role read from the database)."""
from functools import wraps

from flask import g, request

from config.constants import TIPO_ADMIN
from errors import ForbiddenError, UnauthorizedError
from services import auth_service


def _token_bearer():
    esquema, _, token = request.headers.get("Authorization", "").partition(" ")
    if esquema.lower() != "bearer" or not token.strip():
        raise UnauthorizedError("Autenticação necessária")
    return token.strip()


def _autenticar():
    g.usuario_atual = auth_service.usuario_do_token(_token_bearer())
    return g.usuario_atual


def is_admin(usuario):
    return usuario is not None and usuario["tipo"] == TIPO_ADMIN


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        _autenticar()
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not is_admin(_autenticar()):
            raise ForbiddenError("Acesso restrito a administradores")
        return view(*args, **kwargs)

    return wrapper


def _como_id(valor):
    """Accepts 2 or "2" (the original API accepted both in the JSON body)."""
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    if isinstance(valor, str) and valor.strip().isdigit():
        return int(valor)
    return None


def exigir_dono_ou_admin(usuario_id):
    usuario = g.get("usuario_atual")
    if usuario is None or (usuario["id"] != _como_id(usuario_id) and not is_admin(usuario)):
        raise ForbiddenError("Acesso negado")
