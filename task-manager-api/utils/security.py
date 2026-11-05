"""Hash de senhas com salt (werkzeug) e verificação de hashes MD5 legados."""
import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

_LEGACY_MD5 = re.compile(r"^[0-9a-f]{32}$")


def hash_password(raw_password):
    return generate_password_hash(raw_password)


def verify_password(stored_hash, raw_password):
    """Retorna (senha_confere, precisa_rehash). Hashes MD5 antigos são aceitos uma vez e migrados."""
    if not stored_hash:
        return False, False
    if _LEGACY_MD5.match(stored_hash):
        legacy = hashlib.md5(raw_password.encode()).hexdigest()
        ok = hmac.compare_digest(stored_hash, legacy)
        return ok, ok
    return check_password_hash(stored_hash, raw_password), False
