"""Centralized error handling: domain errors -> 4xx, unexpected errors -> generic 500 (details only in the log)."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"erro": err.message, "sucesso": False}), err.status_code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):
            return err
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
