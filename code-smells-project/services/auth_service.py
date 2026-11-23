"""Token assinado (HMAC-SHA256) com expiração; o papel é sempre relido do banco."""
import hashlib

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from errors import UnauthorizedError
from models import usuario_model

TOKEN_INVALIDO = "Token inválido ou expirado"


def _serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="auth-token",
        signer_kwargs={"digest_method": hashlib.sha256},
    )


def emitir_token(usuario):
    return _serializer().dumps({"uid": usuario["id"]})


def usuario_do_token(token):
    try:
        dados = _serializer().loads(token, max_age=current_app.config["TOKEN_EXPIRES_SECONDS"])
    except (BadSignature, SignatureExpired):
        raise UnauthorizedError(TOKEN_INVALIDO) from None
    usuario = usuario_model.buscar_por_id(dados.get("uid")) if isinstance(dados, dict) else None
    if usuario is None:
        raise UnauthorizedError(TOKEN_INVALIDO)
    return usuario
