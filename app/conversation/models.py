from enum import StrEnum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class ContentType(StrEnum):
    TEXT = "text"
    AUDIO = "audio"


class ConversationContent(BaseModel):
    type: ContentType

    text: Optional[str] = None

    audio_path: Optional[Path] = None


class ConversationInput(BaseModel):
    conversation_id: str

    channel: str

    user_id: str

    chat_id: str

    content: ConversationContent


class ConversationOutput(BaseModel):
    content: ConversationContent