from pydantic import BaseModel

from app.core.intelligence.prompt.models import PromptMessage
from app.llm.modes import LLMMode


class LLMRequest(BaseModel):
    messages: list[PromptMessage]
    mode: LLMMode = LLMMode.CHAT


class LLMResponse(BaseModel):
    text: str