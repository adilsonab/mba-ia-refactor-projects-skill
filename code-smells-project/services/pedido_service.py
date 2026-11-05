"""Order use cases: creation (stock + total rules), listing and status changes."""
from config.constants import STATUS_PEDIDO_APROVADO, STATUS_PEDIDO_CANCELADO, STATUS_PEDIDO_VALIDOS
from errors import ValidationError
from models import pedido_model, produto_model


class PedidoService:
    def __init__(self, notifier):
        self.notifier = notifier

    def criar(self, usuario_id, itens):
        produtos = produto_model.buscar_por_ids(item["produto_id"] for item in itens)

        total = 0
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                raise ValidationError(f"Produto {item['produto_id']} não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
            total += produto["preco"] * item["quantidade"]

        precos = {produto_id: produto["preco"] for produto_id, produto in produtos.items()}
        try:
            pedido_id = pedido_model.criar_com_itens(usuario_id, itens, total, precos)
        except pedido_model.EstoqueInsuficiente as exc:
            raise ValidationError(f"Estoque insuficiente para {produtos[exc.produto_id]['nome']}") from exc

        self.notifier.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar(self, usuario_id=None):
        return pedido_model.listar_com_itens(usuario_id)

    def atualizar_status(self, pedido_id, novo_status):
        if novo_status not in STATUS_PEDIDO_VALIDOS:
            raise ValidationError("Status inválido")
        pedido_model.atualizar_status(pedido_id, novo_status)
        if novo_status == STATUS_PEDIDO_APROVADO:
            self.notifier.pedido_aprovado(pedido_id)
        elif novo_status == STATUS_PEDIDO_CANCELADO:
            self.notifier.pedido_cancelado(pedido_id)
