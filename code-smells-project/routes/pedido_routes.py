"""Pedidos — criar/listar os próprios (autenticado, dono ou admin); visão global e status somente admin."""
from flask import Blueprint

from controllers import pedido_controller as c
from controllers import relatorio_controller
from middlewares.auth import admin_required, login_required

bp = Blueprint("pedidos", __name__)

bp.add_url_rule("/pedidos", "criar_pedido", login_required(c.criar_pedido), methods=["POST"])
bp.add_url_rule("/pedidos", "listar_todos_pedidos", admin_required(c.listar_todos_pedidos), methods=["GET"])
bp.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario",
                login_required(c.listar_pedidos_usuario), methods=["GET"])
bp.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido",
                admin_required(c.atualizar_status_pedido), methods=["PUT"])
bp.add_url_rule("/relatorios/vendas", "relatorio_vendas",
                admin_required(relatorio_controller.relatorio_vendas), methods=["GET"])
