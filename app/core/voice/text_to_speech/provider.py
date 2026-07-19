from abc import ABC, abstractmethod

from app.core.voice.models import (
    TextToSpeechRequest,
    TextToSpeechResponse,
)


class BaseTextToSpeechProvider(ABC):

    @abstractmethod
    async def synthesize(
        self,
        request: TextToSpeechRequest,
    ) -> TextToSpeechResponse:
        ...