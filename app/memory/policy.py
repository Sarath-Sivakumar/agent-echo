from app.memory.models import ConversationHistory


class MemoryPolicy:

    MAX_MESSAGES = 20

    def prepare(
        self,
        history: ConversationHistory,
    ) -> ConversationHistory:

        if len(history.messages) <= self.MAX_MESSAGES:
            return history

        return ConversationHistory(
            messages=history.messages[-self.MAX_MESSAGES :]
        )