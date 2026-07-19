import asyncio
from pathlib import Path

from app.core.voice.models import (
    SpeechToTextRequest,
)
from app.core.voice.speech_to_text.groq_provider import (
    GroqSpeechToTextProvider,
)


async def main():

    provider = GroqSpeechToTextProvider()

    response = await provider.transcribe(
        SpeechToTextRequest(
            audio_path=Path("sample.ogg"),
        )
    )

    print("\nTranscription:")
    print("-" * 50)
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())