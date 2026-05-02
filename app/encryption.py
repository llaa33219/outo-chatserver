from cryptography.fernet import Fernet
from sqlalchemy import TypeDecorator, String
from app.config import get_settings

settings = get_settings()

_fernet: Fernet = None


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.ENCRYPTION_KEY
        if not key:
            raise ValueError("ENCRYPTION_KEY not set in .env")
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


class EncryptedString(TypeDecorator):
    """Transparently encrypt/decrypt string values in the database."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            f = get_fernet()
            return f.encrypt(value.encode()).decode()
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            f = get_fernet()
            return f.decrypt(value.encode()).decode()
        return value
