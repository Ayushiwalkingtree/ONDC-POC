from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionEventRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    message_id: str
    action: str
    direction: Literal["command", "callback"]
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
