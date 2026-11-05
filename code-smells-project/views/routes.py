"""HTTP mapping: METHOD /path -> controller (same paths, methods and endpoint names as before)."""
from controllers import (
    pedido_controller,
    produto_controller,
    relatorio_controller,
    sistema_controller,
    usuario_controller,
)

ROTAS = [
    ("/", "index", sistema_controller.index, ["GET"]),

    ("/produtos", "listar_produtos", produto_controller.listar_produtos, ["GET"]),
    ("/produtos/busca", "buscar_produtos", produto_controller.buscar_produtos, ["GET"]),
    ("/produtos/<int:produto_id>", "buscar_produto", produto_controller.buscar_produto, ["GET"]),
    ("/produtos", "criar_produto", produto_controller.criar_produto, ["POST"]),
    ("/produtos/<int:produto_id>", "atualizar_produto", produto_controller.atualizar_produto, ["PUT"]),
    ("/produtos/<int:produto_id>", "deletar_produto", produto_controller.deletar_produto, ["DELETE"]),

    ("/usuarios", "listar_usuarios", usuario_controller.listar_usuarios, ["GET"]),
    ("/usuarios/<int:usuario_id>", "buscar_usuario", usuario_controller.buscar_usuario, ["GET"]),
    ("/usuarios", "criar_usuario", usuario_controller.criar_usuario, ["POST"]),
    ("/login", "login", usuario_controller.login, ["POST"]),

    ("/pedidos", "criar_pedido", pedido_controller.criar_pedido, ["POST"]),
    ("/pedidos", "listar_todos_pedidos", pedido_controller.listar_todos_pedidos, ["GET"]),
    ("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", pedido_controller.listar_pedidos_usuario, ["GET"]),
    ("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", pedido_controller.atualizar_status_pedido, ["PUT"]),

    ("/relatorios/vendas", "relatorio_vendas", relatorio_controller.relatorio_vendas, ["GET"]),

    ("/health", "health_check", sistema_controller.health_check, ["GET"]),
    ("/admin/reset-db", "reset_database", sistema_controller.reset_database, ["POST"]),
]


def register_routes(app):
    for path, endpoint, view_func, methods in ROTAS:
        app.add_url_rule(path, endpoint, view_func, methods=methods)
