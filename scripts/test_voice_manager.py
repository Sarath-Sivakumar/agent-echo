import asyncio
from pathlib import Path

from app.core.voice.manager import VoiceManager
from app.core.voice.models import SpeechToTextRequest
from app.core.voice.speech_to_text.groq_provider import (
    GroqSpeechToTextProvider,
)


async def main():

    manager = VoiceManager(
        speech_to_text_provider=GroqSpeechToTextProvider(),
        text_to_speech_provider=None,
    )

    response = await manager.transcribe(
        SpeechToTextRequest(
            audio_path=Path("sample.ogg"),
        )
    )

    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())