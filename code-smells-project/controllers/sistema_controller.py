"""Index, health check and the (admin-only) administrative reset."""
import logging

from flask import current_app, jsonify

from config.constants import API_VERSION
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


def reset_database():  # admin only (admin_required in views/routes.py)
    sistema_model.limpar_todas_tabelas()
    logger.warning("Banco de dados resetado via /admin/reset-db")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
