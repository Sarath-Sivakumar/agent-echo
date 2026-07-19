from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]

WHATSAPP_ACCESS_TOKEN = os.environ["WHATSAPP_ACCESS_TOKEN"]

WHATSAPP_GRAPH_API = os.environ["WHATSAPP_GRAPH_API"]

WHATSAPP_VERIFY_TOKEN = os.environ["WHATSAPP_VERIFY_TOKEN"]

WHATSAPP_PHONE_NUMBER_ID = os.environ["WHATSAPP_PHONE_NUMBER_ID"]

# GROQ_API_KEY: str = os.environ["GROQ_API_KEY"]

# GROQ_MODEL: str = os.environ["GROQ_MODEL1"]

GROQ_STT_MODEL: str = os.environ["GROQ_STT_MODEL"]

GROQ_TTS_MODEL: str = os.environ["GROQ_TTS_MODEL"]

GROQ_TTS_DEFAULT_VOICE: str = os.environ.get(
    "GROQ_TTS_DEFAULT_VOICE",
    "troy",
)

GROQ_TTS_RESPONSE_FORMAT: str = os.environ.get(
    "GROQ_TTS_RESPONSE_FORMAT",
    "wav",
)