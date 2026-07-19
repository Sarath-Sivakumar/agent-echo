from abc import ABC, abstractmethod

from app.core.voice.models import (
    SpeechToTextRequest,
    SpeechToTextResponse,
)


class BaseSpeechToTextProvider(ABC):

    @abstractmethod
    async def transcribe(
        self,
        request: SpeechToTextRequest,
    ) -> SpeechToTextResponse:
        pass