from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


class GroqClient:

    _client: Groq | None = None

    @classmethod
    def instance(cls) -> Groq:

        if cls._client is None:
            cls._client = Groq(
                api_key=os.environ["GROQ_API_KEY4"],
            )

        return cls._client