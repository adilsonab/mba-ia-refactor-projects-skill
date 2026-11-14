"""Access tokens signed with SECRET_KEY (HMAC-SHA256, itsdangerous) with expiration."""
import hashlib

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from errors import UnauthorizedError
from models import usuario_model

_TOKEN_SALT = "loja-auth-token"
TOKEN_INVALIDO = "Token inválido ou expirado"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_TOKEN_SALT,
                                  signer_kwargs={"digest_method": hashlib.sha256})


def emitir_token(usuario):
    """The token carries only the user id: the role (`tipo`) is always re-read from the database."""
    return _serializer().dumps({"uid": usuario["id"]})


def usuario_do_token(token):
    try:
        dados = _serializer().loads(token, max_age=current_app.config["TOKEN_MAX_AGE"])
    except (BadSignature, SignatureExpired):
        raise UnauthorizedError(TOKEN_INVALIDO) from None
    usuario_id = dados.get("uid") if isinstance(dados, dict) else None
    usuario = usuario_model.buscar_por_id(usuario_id) if isinstance(usuario_id, int) else None
    if usuario is None:
        raise UnauthorizedError(TOKEN_INVALIDO)
    return usuario
