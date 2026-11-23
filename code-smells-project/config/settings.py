"""Configuração lida do ambiente, com defaults seguros (debug off, bind local, CORS fechado)."""
import os
import secrets


def _csv(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


def _bool(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY_FROM_ENV = bool(os.environ.get("SECRET_KEY"))
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _bool("DEBUG") or _bool("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    CORS_ORIGINS = _csv("CORS_ORIGINS")  # [] = nenhuma origem externa; ["*"] só se definido explicitamente
    TOKEN_EXPIRES_SECONDS = int(os.environ.get("TOKEN_EXPIRES_SECONDS", "3600"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
