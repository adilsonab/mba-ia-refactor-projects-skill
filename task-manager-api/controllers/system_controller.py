from datetime import datetime

from config.constants import API_NAME, API_VERSION


def health():
    return {"status": "ok", "timestamp": str(datetime.now())}


def index():
    return {"message": API_NAME, "version": API_VERSION}
