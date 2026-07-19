import os

from dotenv import load_dotenv
from groq import RateLimitError as GroqRateLimitError

from app.core.voice.models import (
    SpeechToTextRequest,
    SpeechToTextResponse,
)
from app.core.voice.speech_to_text.provider import (
    BaseSpeechToTextProvider,
)
from app.llm.clients.groq_client import GroqClient

load_dotenv()


class GroqSpeechToTextProvider(
    BaseSpeechToTextProvider,
):

    MODEL = os.environ["GROQ_STT_MODEL"]

    async def transcribe(
        self,
        request: SpeechToTextRequest,
    ) -> SpeechToTextResponse:

        try:

            with open(
                request.audio_path,
                "rb",
            ) as audio:

                response = (
                    GroqClient.instance()
                    .audio.transcriptions.create(
                        file=audio,
                        model=self.MODEL,
                        language=request.language,
                    )
                )

        except GroqRateLimitError as exc:

            raise Exception(
                "Groq rate limit reached."
            ) from exc

        return SpeechToTextResponse(
            text=response.text,
        )