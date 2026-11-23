"""Casos de uso de pedidos: cálculo do total, checagem de estoque e mudança de status."""
from config.constants import STATUS_NOTIFICADOS, STATUS_PEDIDO
from errors import NotFoundError, ValidationError
from models import pedido_model, produto_model


class PedidoService:
    def __init__(self, notifier):
        self.notifier = notifier

    def criar(self, usuario_id, itens):
        produtos = produto_model.buscar_por_ids(item["produto_id"] for item in itens)

        total = 0
        itens_precificados = []
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                raise ValidationError("Produto " + str(item["produto_id"]) + " não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"])
            total = total + (produto["preco"] * item["quantidade"])
            itens_precificados.append({
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
                "nome": produto["nome"],
            })

        # O débito é revalidado de forma atômica dentro da transação (concorrência).
        pedido_id = pedido_model.criar_com_itens(usuario_id, itens_precificados, total)
        self.notifier.notificar_pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar_todos(self):
        return pedido_model.listar()

    def listar_por_usuario(self, usuario_id):
        return pedido_model.listar(usuario_id)

    def atualizar_status(self, pedido_id, novo_status):
        if novo_status not in STATUS_PEDIDO:
            raise ValidationError("Status inválido")
        if not pedido_model.atualizar_status(pedido_id, novo_status):
            raise NotFoundError("Pedido não encontrado")
        if novo_status in STATUS_NOTIFICADOS:
            self.notifier.notificar_status_pedido(pedido_id, novo_status)
