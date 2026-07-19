from app.conversation.models import (
    ConversationInput,
    ConversationOutput,
)
from app.core.intelligence.engine import IntelligenceEngine


class EchoRuntime:

    def __init__(self) -> None:
        self.engine = IntelligenceEngine()

    async def execute(
        self,
        conversation: ConversationInput,
    ) -> ConversationOutput:

        print("Echo Runtime")

        return await self.engine.process(
            conversation
        )