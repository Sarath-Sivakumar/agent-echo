from pathlib import Path

from telegram import Bot

from app.core.config.config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_message(
    chat_id: int | str,
    text: str,
) -> None:

    await bot.send_message(
        chat_id=chat_id,
        text=text,
    )


async def send_voice(
    chat_id: int | str,
    voice: Path,
) -> None:

    print("\nSending audio...")
    print("Path:", voice)
    print("Exists:", voice.exists())

    with open(voice, "rb") as audio_file:
        await bot.send_voice(
            chat_id=chat_id,
            voice=audio_file,
        )


async def download_voice(
    file_id: str,
    destination: Path,
) -> None:

    telegram_file = await bot.get_file(file_id)

    await telegram_file.download_to_drive(
        custom_path=str(destination),
    )