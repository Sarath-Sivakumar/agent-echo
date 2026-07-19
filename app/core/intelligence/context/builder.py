from datetime import datetime, timezone

from app.conversation.models import ConversationInput
from app.core.intelligence.context.models import Context
from app.memory.models import ConversationHistory


class ContextBuilder:

    async def build(
        self,
        conversation: ConversationInput,
        history: ConversationHistory,
    ) -> Context:

        return Context(
            conversation_id=conversation.conversation_id,
            channel=conversation.channel,
            user_id=conversation.user_id,
            chat_id=conversation.chat_id,
            message=conversation.content.text,
            history=history,
            current_time=datetime.now(timezone.utc),
            metadata={},
        )