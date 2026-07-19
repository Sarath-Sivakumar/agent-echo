from app.llm.models import (
    LLMRequest,
    LLMResponse,
)
from app.llm.providers.groq_provider import GroqProvider


class LLMService:

    def __init__(self) -> None:
        self.provider = GroqProvider()

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        return await self.provider.generate(
            request
        )