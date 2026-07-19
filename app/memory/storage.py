from app.memory.models import (
    ConversationHistory,
    MemoryMessage,
)


class InMemoryStorage:

    def __init__(self):
        self._storage: dict[str, ConversationHistory] = {}

    def get_history(
        self,
        conversation_id: str,
    ) -> ConversationHistory:

        return self._storage.setdefault(
            conversation_id,
            ConversationHistory(),
        )

    def append_message(
        self,
        conversation_id: str,
        message: MemoryMessage,
    ) -> None:

        history = self.get_history(conversation_id)
        history.messages.append(message)

    def clear(
        self,
        conversation_id: str,
    ) -> None:

        self._storage.pop(conversation_id, None)