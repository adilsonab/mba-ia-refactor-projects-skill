"""Hash de senha forte (scrypt/pbkdf2 com salt, via werkzeug)."""
from werkzeug.security import check_password_hash, generate_password_hash

_PREFIXOS_HASH = ("scrypt:", "pbkdf2:")


def hash_password(raw):
    return generate_password_hash(raw)


def is_hashed(stored):
    return bool(stored) and stored.startswith(_PREFIXOS_HASH)


def verify_password(stored, raw):
    return is_hashed(stored) and check_password_hash(stored, raw)
