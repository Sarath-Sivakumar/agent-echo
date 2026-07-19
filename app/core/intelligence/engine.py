from app.conversation.models import (
    ContentType,
    ConversationContent,
    ConversationInput,
    ConversationOutput,
)

from app.core.intelligence.context.builder import ContextBuilder
from app.core.intelligence.prompt.builder import PromptBuilder

from app.llm.manager import LLMManager
from app.llm.models import LLMRequest
from app.llm.modes import LLMMode

from app.memory.manager import MemoryManager


class IntelligenceEngine:

    def __init__(self):

        self.memory = MemoryManager()

        self.context_builder = ContextBuilder()

        self.prompt_builder = PromptBuilder()

        self.llm = LLMManager()

    async def process(
        self,
        conversation: ConversationInput,
    ) -> ConversationOutput:

        self.memory.add_user_message(
            conversation.conversation_id,
            conversation.content.text or "",
        )

        history = self.memory.get_history(
            conversation.conversation_id,
        )

        context = await self.context_builder.build(
            conversation,
            history,
        )

        prompt = await self.prompt_builder.build(
            context,
        )

        request = LLMRequest(
            messages=prompt.messages,
            mode=LLMMode.CHAT,
        )

        response = await self.llm.generate(
            request,
        )

        self.memory.add_assistant_message(
            conversation.conversation_id,
            response.text,
        )

        return ConversationOutput(
            content=ConversationContent(
                type=ContentType.TEXT,
                text=response.text,
            )
        )