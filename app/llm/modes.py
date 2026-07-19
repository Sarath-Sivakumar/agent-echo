from enum import Enum


class LLMMode(str, Enum):
    CHAT = "chat"
    PLANNER = "planner"
    REFLECTION = "reflection"
    MEMORY = "memory"
    SUMMARIZER = "summarizer"