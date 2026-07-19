from abc import ABC, abstractmethod

from app.llm.models import (
    LLMRequest,
    LLMResponse,
)


class ProviderRateLimitError(Exception):

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
    ):
        super().__init__(message)
        self.retry_after = retry_after


class BaseLLMProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        ...