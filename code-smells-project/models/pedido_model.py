"""Acesso a dados de pedidos e itens (criação transacional, listagem sem N+1, agregação)."""
from config.constants import STATUS_INICIAL_PEDIDO
from database import get_db, transaction
from errors import ValidationError
from models import produto_model


def criar_com_itens(usuario_id, itens, total):
    """Grava pedido + itens + débito de estoque em uma única transação.

    `itens`: lista de dicts com produto_id, quantidade, preco_unitario e nome.
    """
    with transaction() as conn:
        cursor = conn.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_INICIAL_PEDIDO, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            if not produto_model.debitar_estoque(conn, item["produto_id"], item["quantidade"]):
                raise ValidationError("Estoque insuficiente para " + item["nome"])
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
    return pedido_id


def listar(usuario_id=None):
    """Pedidos com itens em uma única query (LEFT JOIN), opcionalmente filtrados por usuário."""
    rows = get_db().execute(
        """
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
        WHERE (? IS NULL OR p.usuario_id = ?)
        ORDER BY p.id, i.id
        """,
        (usuario_id, usuario_id),
    ).fetchall()

    pedidos = {}
    for row in rows:
        pedido = pedidos.get(row["id"])
        if pedido is None:
            pedido = pedidos[row["id"]] = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["item_id"] is not None:
            pedido["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] if row["produto_nome"] is not None else "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def existe(pedido_id):
    return get_db().execute("SELECT 1 FROM pedidos WHERE id = ?", (pedido_id,)).fetchone() is not None


def atualizar_status(pedido_id, novo_status):
    cursor = get_db().execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    return cursor.rowcount > 0


def resumo_vendas(status_pendente, status_aprovado, status_cancelado):
    """Todas as agregações do relatório em uma única query."""
    row = get_db().execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS pendentes,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS aprovados,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
        """,
        (status_pendente, status_aprovado, status_cancelado),
    ).fetchone()
    return dict(row)
