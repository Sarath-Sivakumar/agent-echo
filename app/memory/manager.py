from app.memory.models import (
    ConversationHistory,
    MemoryMessage,
)
from app.memory.storage import InMemoryStorage
from app.memory.policy import MemoryPolicy


class MemoryManager:

    def __init__(self):
        self.storage = InMemoryStorage()
        self.policy = MemoryPolicy()

    def get_history(
        self,
        conversation_id: str,
    ) -> ConversationHistory:

        history = self.storage.get_history(conversation_id)
        return self.policy.prepare(history)

    def add_user_message(
        self,
        conversation_id: str,
        content: str,
    ) -> None:

        self.storage.append_message(
            conversation_id,
            MemoryMessage(
                role="user",
                content=content,
            ),
        )

    def add_assistant_message(
        self,
        conversation_id: str,
        content: str,
    ) -> None:

        self.storage.append_message(
            conversation_id,
            MemoryMessage(
                role="assistant",
                content=content,
            ),
        )

    def clear(
        self,
        conversation_id: str,
    ) -> None:

        self.storage.clear(
            conversation_id
        )