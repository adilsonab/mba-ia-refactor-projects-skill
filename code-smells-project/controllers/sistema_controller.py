"""Index, health check and the (token-protected) administrative reset."""
import hmac
import logging

from flask import current_app, jsonify, request

from config.constants import API_VERSION
from errors import ForbiddenError
from models import sistema_model

logger = logging.getLogger(__name__)


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": API_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": sistema_model.contagens(),
        "versao": API_VERSION,
        "ambiente": current_app.config["APP_ENV"],
    }), 200


def _exigir_token_admin():
    esperado = current_app.config.get("ADMIN_TOKEN")
    recebido = request.headers.get("X-Admin-Token", "")
    if not esperado or not hmac.compare_digest(recebido.encode(), esperado.encode()):
        raise ForbiddenError("Não autorizado")


def reset_database():
    _exigir_token_admin()
    sistema_model.limpar_todas_tabelas()
    logger.warning("Banco de dados resetado via /admin/reset-db")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
