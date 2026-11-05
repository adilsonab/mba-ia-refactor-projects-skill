"""Data access for `pedidos` and `itens_pedido` (transactions, JOINs and aggregations)."""
from config.constants import PRODUTO_DESCONHECIDO, STATUS_PEDIDO_INICIAL
from database import get_db


class EstoqueInsuficiente(Exception):
    def __init__(self, produto_id):
        super().__init__(produto_id)
        self.produto_id = produto_id


def criar_com_itens(usuario_id, itens, total, precos):
    """Inserts the order, its items and debits stock atomically.

    Stock is debited with a conditional UPDATE, so concurrent orders can't oversell.
    Raises EstoqueInsuficiente (and rolls everything back) when stock runs out.
    """
    conn = get_db()
    with conn:  # commit on success, rollback on any exception
        cursor = conn.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PEDIDO_INICIAL, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            produto_id, quantidade = item["produto_id"], item["quantidade"]
            debito = conn.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (quantidade, produto_id, quantidade),
            )
            if debito.rowcount == 0:
                raise EstoqueInsuficiente(produto_id)
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, produto_id, quantidade, precos[produto_id]),
            )
    return pedido_id


def listar_com_itens(usuario_id=None):
    """Orders with their items in a single JOIN query (optionally filtered by user)."""
    rows = get_db().execute(
        """
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome,
               i.id AS item_id
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
                "produto_nome": row["produto_nome"] if row["produto_nome"] is not None else PRODUTO_DESCONHECIDO,
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def atualizar_status(pedido_id, status):
    conn = get_db()
    with conn:
        cursor = conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
    return cursor.rowcount


def resumo_vendas(status_pendente, status_aprovado, status_cancelado):
    """Order count, revenue and count per status in a single query."""
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
