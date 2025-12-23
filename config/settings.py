# Settings for API key authentication and HTTP server
import os

# API Key authentication
APIKEY_SALT: str = os.getenv("APIKEY_SALT", "dev-salt-change-in-production")

# HTTP Server
HOST: str = os.getenv("HOST", "0.0.0.0")

PORT: int = int(os.getenv("PORT", "8000"))
