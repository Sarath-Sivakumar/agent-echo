from pydantic import BaseModel


class PromptMessage(BaseModel):
    role: str
    content: str


class Prompt(BaseModel):
    messages: list[PromptMessage]