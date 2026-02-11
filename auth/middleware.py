import hashlib
from datetime import datetime
from sqlmodel import Session, select

from config import APIKEY_SALT
from db.database import engine
from model import ApiKey


def hash_api_key(api_key: str) -> str:
    """Hash an API key with the salt using SHA256."""
    salted = f"{APIKEY_SALT}{api_key}"
    return hashlib.sha256(salted.encode()).hexdigest()


def validate_api_key(token: str) -> bool:
    """
    Validate API key and update usage stats.
    Returns True if valid, False otherwise.
    """
    if not token:
        return False

    key_hash = hash_api_key(token)

    with Session(engine) as session:
        query = select(ApiKey).where(ApiKey.key_hash == key_hash)
        api_key = session.exec(query).first()

        if not api_key:
            return False

        api_key.calls_count += 1
        api_key.last_used_at = datetime.utcnow()
        session.add(api_key)
        session.commit()

        return True


def validate_request(request) -> bool:
    """
    Validate API key from URL query param or header.
    URL: ?api_key=sk_xxx (like Tavily)
    Header: Authorization: Bearer sk_xxx
    """
    api_key = request.query_params.get("api_key")

    if not api_key:
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]

    if not api_key:
        return False

    return validate_api_key(api_key)
