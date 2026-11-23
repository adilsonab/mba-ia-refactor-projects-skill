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

    # Secure defaults (AP-10): debug off, local bind; exposing on the network requires HOST=0.0.0.0.
    DEBUG = _env_flag("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    APP_ENV = os.environ.get("APP_ENV", "producao")

    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

    # CORS closed by default: empty = no foreign origin is allowed. Comma-separated allowlist
    # (e.g. "https://loja.exemplo.com") opens only those origins; "*" must be set explicitly.
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]

    # Validity (seconds) of the signed access token issued by POST /login.
    TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", str(TOKEN_MAX_AGE_PADRAO)))

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
