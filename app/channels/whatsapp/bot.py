from pathlib import Path

from app.channels.whatsapp.client import WhatsAppClient

client = WhatsAppClient()


async def send_message(
    chat_id: str,
    text: str,
) -> None:

    await client.send_text(
        to=chat_id,
        text=text,
    )


async def send_voice(
    chat_id: str,
    voice: Path,
) -> None:

    print("\nUploading WhatsApp voice...")
    print("Path:", voice)
    print("Exists:", voice.exists())

    media_id = await client.upload_media(
        file=voice,
        mime_type="audio/ogg",
    )

    print("Media ID:", media_id)

    await client.send_voice(
        to=chat_id,
        media_id=media_id,
    )


async def download_voice(
    media_id: str,
    destination: Path,
) -> None:

    media_url = await client.get_media_url(
        media_id=media_id,
    )

    await client.download_media(
        media_url=media_url,
        destination=destination,
    )