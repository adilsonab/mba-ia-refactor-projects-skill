"""HTTP mapping: METHOD /path -> controller (same paths, methods and endpoint names as before).

Access matrix (AP-11): public | login_required (owner or admin, checked in the controller) | admin_required.
"""
from controllers import (
    pedido_controller,
    produto_controller,
    relatorio_controller,
    sistema_controller,
    usuario_controller,
)
from middlewares.auth import admin_required, login_required

ROTAS = [
    ("/", "index", sistema_controller.index, ["GET"]),

    # Product catalog: public read, admin write
    ("/produtos", "listar_produtos", produto_controller.listar_produtos, ["GET"]),
    ("/produtos/busca", "buscar_produtos", produto_controller.buscar_produtos, ["GET"]),
    ("/produtos/<int:produto_id>", "buscar_produto", produto_controller.buscar_produto, ["GET"]),
    ("/produtos", "criar_produto", admin_required(produto_controller.criar_produto), ["POST"]),
    ("/produtos/<int:produto_id>", "atualizar_produto", admin_required(produto_controller.atualizar_produto), ["PUT"]),
    ("/produtos/<int:produto_id>", "deletar_produto", admin_required(produto_controller.deletar_produto), ["DELETE"]),

    # Users: public sign-up and login; owner-or-admin detail; admin-only listing
    ("/usuarios", "listar_usuarios", admin_required(usuario_controller.listar_usuarios), ["GET"]),
    ("/usuarios/<int:usuario_id>", "buscar_usuario", login_required(usuario_controller.buscar_usuario), ["GET"]),
    ("/usuarios", "criar_usuario", usuario_controller.criar_usuario, ["POST"]),
    ("/login", "login", usuario_controller.login, ["POST"]),

    # Orders: customers create/list their own; admin lists all and changes status
    ("/pedidos", "criar_pedido", login_required(pedido_controller.criar_pedido), ["POST"]),
    ("/pedidos", "listar_todos_pedidos", admin_required(pedido_controller.listar_todos_pedidos), ["GET"]),
    ("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario",
     login_required(pedido_controller.listar_pedidos_usuario), ["GET"]),
    ("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido",
     admin_required(pedido_controller.atualizar_status_pedido), ["PUT"]),

    ("/relatorios/vendas", "relatorio_vendas", admin_required(relatorio_controller.relatorio_vendas), ["GET"]),

    ("/health", "health_check", sistema_controller.health_check, ["GET"]),
    ("/admin/reset-db", "reset_database", admin_required(sistema_controller.reset_database), ["POST"]),
]


def register_routes(app):
    for path, endpoint, view_func, methods in ROTAS:
        app.add_url_rule(path, endpoint, view_func, methods=methods)
