"""Usuários — cadastro e login públicos; listagem admin; detalhe do próprio usuário (ou admin)."""
from flask import Blueprint

from controllers import usuario_controller as c
from middlewares.auth import admin_required, login_required

bp = Blueprint("usuarios", __name__)

bp.add_url_rule("/usuarios", "listar_usuarios", admin_required(c.listar_usuarios), methods=["GET"])
bp.add_url_rule("/usuarios/<int:usuario_id>", "buscar_usuario", login_required(c.buscar_usuario), methods=["GET"])
bp.add_url_rule("/usuarios", "criar_usuario", c.criar_usuario, methods=["POST"])
bp.add_url_rule("/login", "login", c.login, methods=["POST"])
