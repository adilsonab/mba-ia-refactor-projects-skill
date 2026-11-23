import re
from datetime import datetime, timezone

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def utcnow():
    """Data/hora atual em UTC, "naive" para manter o formato dos dados já gravados no SQLite."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return isinstance(email, str) and EMAIL_PATTERN.match(email) is not None


def is_valid_color(color):
    """Cor no formato #RRGGBB (o helper original só checava tamanho 7 e o '#')."""
    return isinstance(color, str) and HEX_COLOR_PATTERN.match(color) is not None
