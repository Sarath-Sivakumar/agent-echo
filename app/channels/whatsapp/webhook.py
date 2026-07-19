import logging
import time

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.channels.whatsapp.bot import (
    download_voice,
    send_message,
    send_voice,
)
from app.channels.whatsapp.models import WhatsAppWebhook
from app.conversation.manager import ConversationManager
from app.conversation.models import (
    ContentType,
    ConversationContent,
    ConversationInput,
)
from app.core.audio.converter import AudioConverter
from app.core.config.config import WHATSAPP_VERIFY_TOKEN
from app.core.storage.enums import TempResourceType
from app.core.storage.manager import TemporaryResourceManager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp"],
)

conversation_manager = ConversationManager()
resource_manager = TemporaryResourceManager()


# --- Deduplication -----------------------------------------------------------
# WhatsApp redelivers a message on any non-2xx webhook response, and can also
# deliver the same message id more than once legitimately. We keep a short-lived
# record of processed ids so we never reprocess (and re-bill Groq/TTS for) one.

_PROCESSED_TTL_SECONDS = 300
_processed_messages: dict[str, float] = {}


def _already_processed(message_id: str) -> bool:

    now = time.monotonic()

    # Drop expired entries so the dict doesn't grow unbounded.
    expired = [
        mid
        for mid, seen_at in _processed_messages.items()
        if now - seen_at > _PROCESSED_TTL_SECONDS
    ]
    for mid in expired:
        _processed_messages.pop(mid, None)

    if message_id in _processed_messages:
        return True

    _processed_messages[message_id] = now
    return False


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):

    if hub_mode != "subscribe":
        raise HTTPException(
            status_code=400,
            detail="Invalid mode",
        )

    if hub_verify_token != WHATSAPP_VERIFY_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Invalid verify token",
        )

    return int(hub_challenge)


@router.post("/webhook")
async def whatsapp_webhook(
    update: WhatsAppWebhook,
):

    if not update.entry:
        return {"status": "ignored"}

    change = update.entry[0].changes[0]
    value = change.value

    # Ignore delivery/read/status callbacks
    if value.statuses:
        print(value.statuses[0].model_dump())
        return {"status": "ignored"}

    if not value.messages:
        return {"status": "ignored"}

    message = value.messages[0]

    # Skip anything we've already handled (retry or duplicate delivery).
    if _already_processed(message.id):
        logger.info("Skipping duplicate WhatsApp message %s", message.id)
        return {"status": "duplicate"}

    voice_resource = None
    tts_resource = None
    ogg_resource = None

    try:

        content, voice_resource = await _build_content(
            message,
        )

        conversation = ConversationInput(
            conversation_id=f"whatsapp:{message.from_}",
            channel="whatsapp",
            user_id=message.from_,
            chat_id=message.from_,
            content=content,
        )

        response, tts_resource = await conversation_manager.handle_message(
            conversation,
        )

        match response.content.type:

            case ContentType.TEXT:

                await send_message(
                    chat_id=conversation.chat_id,
                    text=response.content.text,
                )

            case ContentType.AUDIO:

                if tts_resource is None:
                    raise RuntimeError(
                        "TTS resource was not created."
                    )

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

    except Exception:

        # Never surface a 5xx: WhatsApp retries on any non-2xx, which is what
        # caused the loop. Log it, ack with 200, and move on.
        logger.exception(
            "Failed to handle WhatsApp message %s",
            message.id,
        )

    finally:

        if voice_resource is not None:
            resource_manager.delete(
                voice_resource,
            )

        if tts_resource is not None:
            resource_manager.delete(
                tts_resource,
            )

        if ogg_resource is not None:
            resource_manager.delete(
                ogg_resource,
            )

    return {"status": "ok"}


async def _build_content(
    message,
):

    match message.type:

        case "text":

            return (
                ConversationContent(
                    type=ContentType.TEXT,
                    text=message.text.body,
                ),
                None,
            )

        case "audio":

            voice_resource = resource_manager.create(
                resource_type=TempResourceType.VOICE,
                suffix=".ogg",
            )

            await download_voice(
                media_id=message.audio.id,
                destination=voice_resource.path,
            )

            print("Downloaded voice:", voice_resource.path)
            print("Size:", voice_resource.path.stat().st_size)

            return (
                ConversationContent(
                    type=ContentType.AUDIO,
                    audio_path=voice_resource.path,
                ),
                voice_resource,
            )

        case _:

            raise ValueError(
                f"Unsupported WhatsApp message type: {message.type}"
            )