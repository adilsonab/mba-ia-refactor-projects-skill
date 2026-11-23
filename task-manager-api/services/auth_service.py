"""Autenticação: login e tokens assinados (HMAC-SHA256) com expiração."""
import hashlib
import logging

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

import database
from models.user import User
from utils.errors import ForbiddenError, UnauthorizedError

logger = logging.getLogger(__name__)


def _serializer():
    return URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt='auth-token',
        signer_kwargs={'digest_method': hashlib.sha256},
    )


def issue_token(user):
    return _serializer().dumps({'uid': user.id})


def user_from_token(token):
    try:
        payload = _serializer().loads(token, max_age=current_app.config['TOKEN_MAX_AGE'])
    except (BadSignature, SignatureExpired):
        raise UnauthorizedError('Token inválido ou expirado') from None
    user = User.get_by_id(payload.get('uid')) if isinstance(payload, dict) else None
    if user is None or not user.active:          # papel e status sempre relidos do banco
        raise UnauthorizedError('Token inválido ou expirado')
    return user


def login(email, password):
    user = User.get_by_email(email)
    if user is None or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        raise ForbiddenError('Usuário inativo')
    if user.password_needs_rehash():              # migração transparente do hash MD5 legado
        user.set_password(password)
        database.commit()
        logger.info('Hash de senha migrado para o usuário %s', user.id)
    return user, issue_token(user)
