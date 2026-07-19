from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.memory.models import ConversationHistory


class Context(BaseModel):
    conversation_id: str

    channel: str

    user_id: str

    chat_id: str

    message: str | None = None

    history: ConversationHistory

    current_time: datetime

    metadata: dict[str, Any] = Field(default_factory=dict)