from fastapi import APIRouter

from app.conversation.manager import ConversationManager
from app.conversation.models import (
    ContentType,
    ConversationContent,
    ConversationInput,
)
from app.core.storage.enums import TempResourceType
from app.core.storage.manager import TemporaryResourceManager
from app.core.audio.converter import AudioConverter
from app.channels.telegram.bot import (
    download_voice,
    send_message,
    send_voice,
)
from app.channels.telegram.models import TelegramUpdate

router = APIRouter(
    prefix="/telegram",
    tags=["Telegram"],
)

conversation_manager = ConversationManager()
resource_manager = TemporaryResourceManager()

# Shown when the model returns nothing at all, so we never send empty text
# (Telegram rejects empty messages with BadRequest) or synthesize silence.
EMPTY_REPLY_FALLBACK = "Sorry, I couldn't generate a response. Please try again."


@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):

    if update.message is None:
        return {"status": "ignored"}

    message = update.message

    voice_resource = None
    tts_resource = None
    ogg_resource = None

    try:

        content, voice_resource = await _build_content(
            message,
        )

        conversation = ConversationInput(
            conversation_id=f"telegram:{message.chat.id}",
            channel="telegram",
            user_id=str(message.from_user.id),
            chat_id=str(message.chat.id),
            content=content,
        )

        response, tts_resource = await conversation_manager.handle_message(
            conversation,
        )

        reply_text = (response.content.text or "").strip()

        match response.content.type:

            case ContentType.TEXT:

                await send_message(
                    chat_id=conversation.chat_id,
                    text=reply_text or EMPTY_REPLY_FALLBACK,
                )

            case ContentType.AUDIO:

                if tts_resource is None:
                    raise RuntimeError(
                        "TTS resource was not returned."
                    )

                # Groq gives WAV; Telegram voice notes need OGG/Opus.
                try:

                    ogg_resource = resource_manager.create(
                        resource_type=TempResourceType.TTS,
                        suffix=".ogg",
                    )

                    AudioConverter.wav_to_ogg(
                        source=tts_resource.path,
                        destination=ogg_resource.path,
                    )

                    await send_voice(
                        chat_id=conversation.chat_id,
                        voice=ogg_resource.path,
                    )

                except (FileNotFoundError, OSError) as ex:

                    # ffmpeg/soundfile missing or conversion failed: fall back
                    # to text so the user still gets an answer.
                    print("Voice conversion failed, sending text:", ex)

                    await send_message(
                        chat_id=conversation.chat_id,
                        text=reply_text or EMPTY_REPLY_FALLBACK,
                    )

        return {"status": "ok"}

    except Exception as ex:

        # Return HTTP 200 even on failure. A 500 makes Telegram redeliver the
        # same update, which re-runs the whole STT/LLM/TTS chain and can spam
        # Groq calls and pollute conversation history. Log and swallow instead.
        print("Webhook handler error:", ex)
        return {"status": "error"}

    finally:

        if voice_resource is not None:
            resource_manager.delete(voice_resource)

        if tts_resource is not None:
            resource_manager.delete(tts_resource)

        if ogg_resource is not None:
            resource_manager.delete(ogg_resource)


async def _build_content(message):

    if message.text is not None:
        return (
            ConversationContent(
                type=ContentType.TEXT,
                text=message.text,
            ),
            None,
        )

    if message.voice is not None:

        voice_resource = resource_manager.create(
            resource_type=TempResourceType.VOICE,
            suffix=".ogg",
        )

        await download_voice(
            file_id=message.voice.file_id,
            destination=voice_resource.path,
        )

        return (
            ConversationContent(
                type=ContentType.AUDIO,
                audio_path=voice_resource.path,
            ),
            voice_resource,
        )

    raise ValueError("Unsupported message type")