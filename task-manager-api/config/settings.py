"""Configuração da aplicação lida de variáveis de ambiente (com defaults de desenvolvimento)."""
import os
import secrets

from config.constants import DEFAULT_TOKEN_MAX_AGE_SECONDS

try:  # python-dotenv é opcional: permite usar um arquivo .env local
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _env_bool(name, default="0"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


def _env_list(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


class Config:
    # Segredo: nunca fixo no código. Sem SECRET_KEY no ambiente, gera um aleatório (apenas desenvolvimento).
    SECRET_KEY_FROM_ENV = bool(os.environ.get("SECRET_KEY"))
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    # Validade (segundos) do token assinado emitido em POST /login.
    TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", str(DEFAULT_TOKEN_MAX_AGE_SECONDS)))

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Defaults seguros (AP-10): debug desligado e bind local; expor na rede exige HOST=0.0.0.0.
    DEBUG = _env_bool("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    # CORS fechado por padrão: vazio = nenhuma origem externa. Lista separada por vírgula libera
    # só essas origens; "*" precisa ser definido explicitamente.
    CORS_ORIGINS = _env_list("CORS_ORIGINS")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Notificações por e-mail (desligadas quando SMTP_HOST/SMTP_USER não estão definidos)
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_SENDER = os.environ.get("SMTP_SENDER", "") or os.environ.get("SMTP_USER", "")
