"""Composition root: cria o app, carrega config, inicializa banco, dependências, rotas e handlers."""
import logging
from datetime import datetime

from flask import Flask
from flask_cors import CORS

import models  # noqa: F401  (registra os models antes do create_all)
from config.settings import Config
from database import db
from middlewares.error_handler import register_error_handlers
from routes import register_routes
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    logging.basicConfig(level=app.config['LOG_LEVEL'], format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    if not app.config['SECRET_KEY_FROM_ENV']:
        logger.warning('SECRET_KEY não definida; usando chave aleatória (tokens expiram a cada reinício).')

    if app.config['CORS_ORIGINS']:                     # CORS fechado por padrão
        origins = '*' if app.config['CORS_ORIGINS'] == ['*'] else app.config['CORS_ORIGINS']
        CORS(app, origins=origins)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.extensions['notifications'] = NotificationService.from_config(app.config)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    register_routes(app)
    register_error_handlers(app)
    return app


app = create_app()   # mantém `from app import app, db` (usado pelo seed.py)

if __name__ == '__main__':
    logger.info('Iniciando em http://%s:%s (debug=%s)', app.config['HOST'], app.config['PORT'],
                'on' if app.config['DEBUG'] else 'off')
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
