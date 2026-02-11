import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Database configuration
DATA_DIR = Path(__file__).parent.parent / "data"
DB_NAME = "mcp_eleven.db"

# Use Azure SQL if DATABASE_URL is set, otherwise use SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Azure SQL connection string format for SQLAlchemy
    DB_URL = DATABASE_URL
else:
    # Local SQLite
    DB_URL = f"sqlite:///{DATA_DIR / DB_NAME}"
