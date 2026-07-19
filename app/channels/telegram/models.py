from typing import Optional

from pydantic import BaseModel, Field


class Chat(BaseModel):
    id: int


class User(BaseModel):
    id: int
    first_name: str
    username: Optional[str] = None


class Voice(BaseModel):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class Message(BaseModel):
    message_id: int

    from_user: User = Field(alias="from")

    chat: Chat

    text: Optional[str] = None

    voice: Optional[Voice] = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: Message | None = None