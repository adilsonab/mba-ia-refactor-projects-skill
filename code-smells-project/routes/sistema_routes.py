"""Sistema — índice e health públicos; reset somente admin. (POST /admin/query foi removido por segurança.)"""
from flask import Blueprint

from controllers import sistema_controller as c
from middlewares.auth import admin_required

bp = Blueprint("sistema", __name__)

bp.add_url_rule("/", "index", c.index, methods=["GET"])
bp.add_url_rule("/health", "health_check", c.health_check, methods=["GET"])
bp.add_url_rule("/admin/reset-db", "reset_database", admin_required(c.reset_database), methods=["POST"])
