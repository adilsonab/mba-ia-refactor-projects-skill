from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, 'connect')
def _enable_sqlite_foreign_keys(dbapi_connection, _record):
    """Integridade referencial no SQLite (desligada por padrão no driver)."""
    if dbapi_connection.__class__.__module__.startswith('sqlite3'):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.close()


def save(*objects):
    """Grava um ou mais objetos em uma única transação."""
    try:
        for obj in objects:
            db.session.add(obj)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def commit():
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def delete(obj):
    try:
        db.session.delete(obj)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
