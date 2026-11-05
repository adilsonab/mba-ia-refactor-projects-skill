"""Configuração da aplicação lida de variáveis de ambiente (com defaults de desenvolvimento)."""
import os
import secrets

try:  # python-dotenv é opcional: permite usar um arquivo .env local
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _env_bool(name, default="0"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


def _env_list(name, default):
    raw = os.environ.get(name, default).strip()
    if raw == "*":
        return "*"
    return [item.strip() for item in raw.split(",") if item.strip()]


class Config:
    # Segredo: nunca fixo no código. Sem SECRET_KEY no ambiente, gera um aleatório (apenas desenvolvimento).
    SECRET_KEY_FROM_ENV = bool(os.environ.get("SECRET_KEY"))
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = _env_bool("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = _env_list("CORS_ORIGINS", "*")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Notificações por e-mail (desligadas quando SMTP_HOST/SMTP_USER não estão definidos)
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_SENDER = os.environ.get("SMTP_SENDER", "") or os.environ.get("SMTP_USER", "")
