"""System-level data access: health counts and the administrative reset."""
from database import get_db


def contagens():
    row = get_db().execute(
        """
        SELECT (SELECT COUNT(*) FROM produtos) AS produtos,
               (SELECT COUNT(*) FROM usuarios) AS usuarios,
               (SELECT COUNT(*) FROM pedidos) AS pedidos
        """
    ).fetchone()
    return dict(row)


def limpar_todas_tabelas():
    conn = get_db()
    with conn:
        for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            conn.execute(f"DELETE FROM {tabela}")  # fixed table names, no external input
