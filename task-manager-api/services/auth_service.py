"""Emissão e validação de tokens de acesso assinados (HMAC-SHA256 com SECRET_KEY + expiração)."""
import hashlib

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from middlewares.error_handler import UnauthorizedError
from models.user import User

_TOKEN_SALT = "task-manager-auth-token"
INVALID_TOKEN_MESSAGE = "Token inválido ou expirado"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_TOKEN_SALT,
                                  signer_kwargs={"digest_method": hashlib.sha256})


def issue_token(user):
    """O token carrega apenas o id: papel e status são sempre relidos do banco."""
    return _serializer().dumps({"uid": user.id})


def user_from_token(token):
    try:
        data = _serializer().loads(token, max_age=current_app.config["TOKEN_MAX_AGE"])
    except (BadSignature, SignatureExpired):
        raise UnauthorizedError(INVALID_TOKEN_MESSAGE) from None
    user_id = data.get("uid") if isinstance(data, dict) else None
    user = User.get_by_id(user_id) if isinstance(user_id, int) else None
    if user is None or not user.active:
        raise UnauthorizedError(INVALID_TOKEN_MESSAGE)
    return user
