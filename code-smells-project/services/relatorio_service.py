"""Sales report use case (discount rule isolated in a pure function)."""
from config.constants import (
    FAIXAS_DESCONTO,
    STATUS_PEDIDO_APROVADO,
    STATUS_PEDIDO_CANCELADO,
    STATUS_PEDIDO_INICIAL,
)
from models import pedido_model


def calcular_desconto(faturamento):
    for limite, taxa in FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * taxa
    return 0


def relatorio_vendas():
    resumo = pedido_model.resumo_vendas(STATUS_PEDIDO_INICIAL, STATUS_PEDIDO_APROVADO, STATUS_PEDIDO_CANCELADO)
    total_pedidos = resumo["total_pedidos"]
    faturamento = resumo["faturamento"]
    desconto = calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": resumo["pendentes"],
        "pedidos_aprovados": resumo["aprovados"],
        "pedidos_cancelados": resumo["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
