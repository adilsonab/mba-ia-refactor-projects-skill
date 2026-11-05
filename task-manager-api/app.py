"""Composition root: cria o app, carrega config, inicializa banco, dependências, rotas e error handlers."""
import logging

from flask import Flask
from flask_cors import CORS

from config import Config
from database import db, init_db  # noqa: F401  (`db` reexportado para `from app import app, db` no seed.py)
from middlewares.error_handler import register_error_handlers
from routes import register_routes
from services.notification_service import build_notification_service


def configure_logging(level):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    configure_logging(app.config["LOG_LEVEL"])
    if not app.config["SECRET_KEY_FROM_ENV"]:
        app.logger.warning("SECRET_KEY não definida; usando chave aleatória (apenas desenvolvimento).")

    CORS(app, origins=app.config["CORS_ORIGINS"])
    init_db(app)
    app.extensions["notification_service"] = build_notification_service(app.config)

    register_routes(app)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
