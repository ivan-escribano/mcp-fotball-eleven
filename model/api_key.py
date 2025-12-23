from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class ApiKey(SQLModel, table=True):
    """Model to store API keys for service access."""

    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="Client/pilot name")
    key_hash: str = Field(
        unique=True, description="SHA256 hash of the API key")
    calls_count: int = Field(default=0, description="Call counter")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(default=None)
