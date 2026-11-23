from routes import pedido_routes, produto_routes, sistema_routes, usuario_routes


def register_routes(app):
    for module in (sistema_routes, produto_routes, usuario_routes, pedido_routes):
        app.register_blueprint(module.bp)
