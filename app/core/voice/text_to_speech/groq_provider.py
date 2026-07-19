import io
import os
import wave

from app.core.config.config import (
    GROQ_TTS_DEFAULT_VOICE,
    GROQ_TTS_MODEL,
    GROQ_TTS_RESPONSE_FORMAT,
)
from app.llm.clients.groq_client import GroqClient
from app.core.voice.models import (
    TextToSpeechRequest,
    TextToSpeechResponse,
)
from app.core.voice.text_to_speech.provider import (
    BaseTextToSpeechProvider,
)
from app.core.voice.text_to_speech.text_prep import prepare_for_tts


def _concat_wav(parts: list[bytes]) -> bytes:
    """Concatenate multiple WAV byte blobs that share the same format."""

    output = io.BytesIO()
    writer: wave.Wave_write | None = None
    try:
        for part in parts:
            reader = wave.open(io.BytesIO(part), "rb")
            if writer is None:
                writer = wave.open(output, "wb")
                writer.setparams(reader.getparams())
            writer.writeframes(reader.readframes(reader.getnframes()))
            reader.close()
    finally:
        if writer is not None:
            writer.close()
    return output.getvalue()


class GroqTextToSpeechProvider(BaseTextToSpeechProvider):

    async def synthesize(
        self,
        request: TextToSpeechRequest,
    ) -> TextToSpeechResponse:

        # Strip markdown and split into <4000-char chunks BEFORE calling Groq.
        chunks = prepare_for_tts(request.text)

        print("\n" + "=" * 80)
        print("TTS REQUEST")
        print("=" * 80)
        print(f"Raw characters   : {len(request.text)}")
        print(f"Speakable chunks : {len(chunks)}")
        print(f"Response format  : {GROQ_TTS_RESPONSE_FORMAT}")
        print("=" * 80)
        if chunks:
            print(chunks[0][:500])
        print("=" * 80)

        request.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not chunks:
            raise ValueError("No speakable text to synthesize.")

        client = GroqClient.instance()

        audio_parts: list[bytes] = []

        for index, chunk in enumerate(chunks, start=1):

            print(f"  -> synthesizing chunk {index}/{len(chunks)} ({len(chunk)} chars)")

            response = client.audio.speech.create(
                model=GROQ_TTS_MODEL,
                input=chunk,
                voice=request.voice or GROQ_TTS_DEFAULT_VOICE,
                response_format=GROQ_TTS_RESPONSE_FORMAT,
            )

            audio_parts.append(response.read())

        if len(audio_parts) == 1:
            # Single chunk: write bytes straight through (format-agnostic).
            data = audio_parts[0]
        else:
            # Multiple chunks. wave-based stitching only works for WAV.
            # For ogg/mp3/flac we can't naively concatenate byte blobs, so
            # rather than produce a corrupt file we send only the first chunk.
            # (Replies are kept short by the system prompt, so this is rare.)
            fmt = GROQ_TTS_RESPONSE_FORMAT.lower()

            if fmt == "wav":
                data = _concat_wav(audio_parts)
            else:
                print(
                    f"  !! {len(audio_parts)} chunks but format is {fmt!r}; "
                    "sending first chunk only (cannot concat non-WAV)."
                )
                data = audio_parts[0]

        with open(request.output_path, "wb") as file:
            file.write(data)

        print("Bytes written:", len(data))
        print("Exists:", request.output_path.exists())

        if request.output_path.exists():
            print(
                "Size:",
                os.path.getsize(request.output_path),
                "bytes",
            )

        return TextToSpeechResponse(
            audio_path=request.output_path,
        )