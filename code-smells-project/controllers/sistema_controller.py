import logging
import sqlite3

from flask import jsonify

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
    try:
        counts = sistema_model.contagens()
    except sqlite3.Error:
        logger.exception("Health check: falha ao acessar o banco")
        return jsonify({"status": "erro", "database": "disconnected"}), 500
    return jsonify({"status": "ok", "database": "connected", "counts": counts, "versao": API_VERSION}), 200


def reset_database():
    sistema_model.resetar()
    logger.warning("Banco de dados resetado por administrador")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
