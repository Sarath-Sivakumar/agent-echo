import os

from dotenv import load_dotenv
from groq import RateLimitError as GroqRateLimitError

from app.llm.models import (
    LLMRequest,
    LLMResponse,
)
from app.llm.modes import LLMMode
from app.llm.provider import (
    BaseLLMProvider,
    ProviderRateLimitError,
)
from app.llm.clients.groq_client import GroqClient

load_dotenv()


class GroqProvider(BaseLLMProvider):

    DEFAULT_MODEL = os.environ["GROQ_MODEL1"]

    MODE_SETTINGS = {
        LLMMode.CHAT: {
            "temperature": 0.4,
            "max_tokens": 150,
        },
        LLMMode.PLANNER: {
            "temperature": 0.0,
            "max_tokens": 700,
        },
        LLMMode.REFLECTION: {
            "temperature": 0.0,
            "max_tokens": 600,
        },
        LLMMode.MEMORY: {
            "temperature": 0.1,
            "max_tokens": 500,
        },
        LLMMode.SUMMARIZER: {
            "temperature": 0.2,
            "max_tokens": 600,
        },
    }

    @property
    def name(self) -> str:
        return "Groq"

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        settings = self.MODE_SETTINGS[request.mode]

        print("\n" + "=" * 80)
        print("GROQ REQUEST")
        print("=" * 80)
        print(f"Model : {self.DEFAULT_MODEL}")
        print(f"Text : {request.messages}")
        print(f"Mode  : {request.mode}")

        total_chars = 0

        for index, message in enumerate(request.messages):

            chars = len(message.content)
            total_chars += chars

            print(
                f"[{index}] {message.role:<10}"
                f"{chars:>6} chars"
            )

        print("-" * 80)
        print(f"Total chars : {total_chars}")
        print(f"Approx tokens: {total_chars // 4}")
        print("=" * 80)

        try:

            response = GroqClient.instance().chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    message.model_dump()
                    for message in request.messages
                ],
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"],
            )

        except GroqRateLimitError as exc:

            raise ProviderRateLimitError(
                "Groq rate limit reached.",
                retry_after=self._retry_after(exc),
            ) from exc

        return LLMResponse(
            text=response.choices[0].message.content
        )

    @staticmethod
    def _retry_after(
        exc,
    ) -> float | None:

        try:
            header = exc.response.headers.get(
                "retry-after"
            )
            return float(header) if header else None
        except Exception:
            return None