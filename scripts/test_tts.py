import asyncio

from app.core.storage.enums import TempResourceType
from app.core.storage.manager import TemporaryResourceManager
from app.core.voice.models import TextToSpeechRequest
from app.core.voice.text_to_speech.groq_provider import (
    GroqTextToSpeechProvider,
)


async def main():

    resource_manager = TemporaryResourceManager()

    provider = GroqTextToSpeechProvider()

    speech = resource_manager.create(
        resource_type=TempResourceType.TTS,
        suffix=".wav",
    )

    response = await provider.synthesize(
        TextToSpeechRequest(
            text=(
                "Hello! This is Echo speaking. "
                "Welcome to the first text to speech test."
            ),
            output_path=speech.path,
        )
    )

    print(f"Generated audio: {response.audio_path}")


if __name__ == "__main__":
    asyncio.run(main())