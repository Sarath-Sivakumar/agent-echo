from app.conversation.models import (
    ContentType,
    ConversationInput,
    ConversationOutput,
)
from app.core.runtime.runtime import EchoRuntime
from app.core.storage.enums import TempResourceType
from app.core.storage.manager import TemporaryResourceManager
from app.core.storage.models import TemporaryResource
from app.core.voice.manager import VoiceManager
from app.core.voice.speech_to_text.groq_provider import GroqSpeechToTextProvider
from app.core.voice.models import (
    SpeechToTextRequest,
    TextToSpeechRequest,
)
from app.core.voice.text_to_speech.groq_provider import GroqTextToSpeechProvider


class ConversationManager:

    def __init__(self):

        self.runtime = EchoRuntime()

        self.resources = TemporaryResourceManager()

        self.voice = VoiceManager(
            speech_to_text_provider=GroqSpeechToTextProvider(),
            text_to_speech_provider=GroqTextToSpeechProvider(),
        )

    async def handle_message(
        self,
        conversation: ConversationInput,
    ) -> tuple[ConversationOutput, TemporaryResource | None]:

        tts_resource = None

        if conversation.content.type == ContentType.AUDIO:

            transcription = await self.voice.transcribe(
                SpeechToTextRequest(
                    audio_path=conversation.content.audio_path,
                )
            )

            conversation.content.text = transcription.text

        response = await self.runtime.execute(
            conversation,
        )

        if conversation.content.type == ContentType.AUDIO:

            print("\n" + "=" * 80)
            print("TEXT GOING TO TTS")
            print("=" * 80)
            print(f"Characters : {len(response.content.text)}")
            print()
            print(response.content.text[:500])
            print("=" * 80)

            try:

                tts_resource = self.resources.create(
                    resource_type=TempResourceType.TTS,
                    suffix=".wav",
                )

                tts = await self.voice.synthesize(
                    TextToSpeechRequest(
                        text=response.content.text,
                        output_path=tts_resource.path,
                    )
                )

                response.content.type = ContentType.AUDIO
                response.content.audio_path = tts.audio_path

            except Exception as ex:

                # TTS failed (e.g. length limit, bad audio). Don't crash the
                # webhook — fall back to a plain text reply instead.
                print("TTS synthesis failed, falling back to text:", ex)

                if tts_resource is not None:
                    self.resources.delete(tts_resource)
                    tts_resource = None

                response.content.type = ContentType.TEXT

        return response, tts_resource