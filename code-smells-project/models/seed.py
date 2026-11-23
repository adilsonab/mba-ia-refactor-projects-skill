"""Inicialização do banco: schema, seed de desenvolvimento e migração de senhas legadas."""
import logging

from database import connect, create_schema
from models.passwords import hash_password, is_hashed

logger = logging.getLogger(__name__)

PRODUTOS_SEED = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# Credenciais APENAS de desenvolvimento (gravadas com hash). Ver README.
USUARIOS_SEED = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]


def init_db(db_path):
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        create_schema(conn)
        if conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                PRODUTOS_SEED,
            )
            conn.executemany(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                [(nome, email, hash_password(senha), tipo) for nome, email, senha, tipo in USUARIOS_SEED],
            )
            logger.info("Banco inicializado com dados de exemplo")
        _migrar_senhas_legadas(conn)
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def _migrar_senhas_legadas(conn):
    """Converte senhas em texto puro (bancos criados pela versão antiga) para hash."""
    legados = [row for row in conn.execute("SELECT id, senha FROM usuarios") if not is_hashed(row["senha"])]
    for row in legados:
        conn.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (hash_password(row["senha"] or ""), row["id"]))
    if legados:
        logger.warning("%d senha(s) legada(s) em texto puro migrada(s) para hash", len(legados))
