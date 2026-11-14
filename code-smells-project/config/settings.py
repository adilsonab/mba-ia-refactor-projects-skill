"""Application configuration read from environment variables (safe development defaults)."""
import os
import secrets

from config.constants import TOKEN_MAX_AGE_PADRAO


def _env_flag(name, default="0"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


class Config:
    # Never hardcode a real secret: without SECRET_KEY a random key is generated per boot.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SECRET_KEY_FROM_ENV = bool(os.environ.get("SECRET_KEY"))

    DEBUG = _env_flag("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    APP_ENV = os.environ.get("APP_ENV", "producao")

    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

    # Comma-separated list of allowed origins; "*" keeps the original (open) behaviour.
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]

    # Validity (seconds) of the signed access token issued by POST /login.
    TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", str(TOKEN_MAX_AGE_PADRAO)))

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
