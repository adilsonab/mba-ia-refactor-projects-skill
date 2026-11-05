import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

db = SQLAlchemy()


def _enable_sqlite_foreign_keys(dbapi_connection, _record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


def init_db(app):
    """Inicializa a extensão, liga a integridade referencial no SQLite e cria as tabelas."""
    db.init_app(app)
    with app.app_context():
        import models  # noqa: F401  (registra os models no metadata)

        event.listen(db.engine, "connect", _enable_sqlite_foreign_keys)
        db.create_all()
