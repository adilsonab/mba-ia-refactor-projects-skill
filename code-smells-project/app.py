"""Composition root: builds the Flask app, wires dependencies and keeps `python app.py` working."""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Config
from database import close_db, init_db
from middlewares.error_handler import register_error_handlers
from services.notification_service import NotificationService
from services.pedido_service import PedidoService
from views.routes import register_routes

logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    if not app.config["SECRET_KEY_FROM_ENV"]:
        logger.warning("SECRET_KEY não definida; usando chave aleatória (apenas desenvolvimento).")

    CORS(app, origins=app.config["CORS_ORIGINS"])

    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    notifier = NotificationService(logging.getLogger("notificacoes"))
    app.extensions["pedido_service"] = PedidoService(notifier)

    register_routes(app)
    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    logger.info("Servidor iniciado em http://%s:%s (debug=%s)",
                app.config["HOST"], app.config["PORT"], app.config["DEBUG"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
