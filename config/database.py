from pathlib import Path

# Database configuration
DATA_DIR = Path(__file__).parent.parent / "data"
DB_NAME = "mcp_scout_football.db"
DB_URL = f"sqlite:///{DATA_DIR / DB_NAME}"
