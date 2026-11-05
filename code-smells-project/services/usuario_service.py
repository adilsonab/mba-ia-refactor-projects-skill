"""User use cases: registration (hashed password) and authentication."""
from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import TIPO_USUARIO_PADRAO
from models import usuario_model


def criar(nome, email, senha):
    return usuario_model.criar(nome, email, generate_password_hash(senha), TIPO_USUARIO_PADRAO)


def autenticar(email, senha):
    """Returns the matching user or None. Passwords are never compared in SQL."""
    for usuario in usuario_model.buscar_por_email(email):
        if usuario["senha"] and check_password_hash(usuario["senha"], senha):
            return usuario
    return None
