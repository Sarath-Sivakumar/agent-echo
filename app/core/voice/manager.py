from app.core.voice.models import (
    SpeechToTextRequest,
    SpeechToTextResponse,
    TextToSpeechRequest,
    TextToSpeechResponse,
)
from app.core.voice.speech_to_text.provider import (
    BaseSpeechToTextProvider,
)
from app.core.voice.text_to_speech.provider import (
    BaseTextToSpeechProvider,
)


class VoiceManager:

    def __init__(
        self,
        speech_to_text_provider: BaseSpeechToTextProvider,
        text_to_speech_provider: BaseTextToSpeechProvider,
    ) -> None:

        self.speech_to_text = speech_to_text_provider
        self.text_to_speech = text_to_speech_provider

    async def transcribe(
        self,
        request: SpeechToTextRequest,
    ) -> SpeechToTextResponse:

        return await self.speech_to_text.transcribe(
            request,
        )

    async def synthesize(
        self,
        request: TextToSpeechRequest,
    ) -> TextToSpeechResponse:

        return await self.text_to_speech.synthesize(
            request,
        )