import os

APIKEY_SALT: str = os.getenv("APIKEY_SALT", "dev-salt-change-in-production")
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
