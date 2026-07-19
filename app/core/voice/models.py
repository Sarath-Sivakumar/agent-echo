from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class SpeechToTextRequest(BaseModel):
    audio_path: Path
    language: Optional[str] = None


class SpeechToTextResponse(BaseModel):
    text: str


class TextToSpeechRequest(BaseModel):
    text: str
    output_path: Path
    voice: Optional[str] = None


class TextToSpeechResponse(BaseModel):
    audio_path: Path