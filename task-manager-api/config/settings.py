"""Configuração lida do ambiente (arquivo .env opcional) com defaults seguros."""
import logging
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _csv(name):
    return [item.strip() for item in os.environ.get(name, '').split(',') if item.strip()]


def _flag(name, default='0'):
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


class Config:
    # Segredo: obrigatório em produção. Sem ele, gera um aleatório por boot (tokens não sobrevivem a reinícios).
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SECRET_KEY_FROM_ENV = bool(os.environ.get('SECRET_KEY'))

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = _flag('FLASK_DEBUG')                      # desligado por padrão
    HOST = os.environ.get('HOST', '127.0.0.1')        # expor na rede exige HOST=0.0.0.0 explícito
    PORT = int(os.environ.get('PORT', '5000'))
    CORS_ORIGINS = _csv('CORS_ORIGINS')               # [] = CORS fechado; '*' só se definido explicitamente

    TOKEN_MAX_AGE = int(os.environ.get('TOKEN_MAX_AGE', '3600'))  # segundos
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
