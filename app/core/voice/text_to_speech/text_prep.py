"""Utilities for preparing LLM text for text-to-speech.

Groq's TTS endpoint rejects input of 4000+ characters and reads any markdown
syntax (``**``, ``|``, ``#`` ...) out loud verbatim. These helpers strip
markdown down to plain spoken text and split long text into safe chunks.
"""

import re

# Groq TTS hard limit is "< 4000 chars". Stay comfortably under it.
TTS_CHUNK_LIMIT = 3500

# Absolute cap on how much we will ever synthesize, so a runaway response
# can't trigger dozens of API calls. Anything beyond this is truncated.
TTS_MAX_TOTAL_CHARS = 24000

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?।])\s+")


def strip_markdown(text: str) -> str:
    """Convert markdown-ish LLM output into plain text suitable for speech."""

    lines = text.splitlines()
    out: list[str] = []
    in_code = False

    for line in lines:
        stripped = line.strip()

        # Fenced code blocks: keep contents, drop the fences.
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            out.append(line)
            continue

        # Horizontal rules: ---, ***, ___, ===
        if re.fullmatch(r"([-*_=])\1{2,}", stripped.replace(" ", "")):
            continue

        # Table separator rows: |---|:--:|
        if "|" in stripped and "-" in stripped and re.fullmatch(r"[\|\s:\-]+", stripped):
            continue

        # Table content rows: flatten "| a | b |" -> "a, b"
        if "|" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            line = ", ".join(c for c in cells if c)

        out.append(line)

    text = "\n".join(out)

    # Images ![alt](url) -> alt ; links [text](url) -> text
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Headings, blockquotes, list markers
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # Emphasis and inline code
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Tidy whitespace
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(text: str, limit: int = TTS_CHUNK_LIMIT) -> list[str]:
    """Split text into chunks no longer than ``limit`` characters."""

    text = text.strip()
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue

        if len(para) > limit:
            flush()
            for sentence in _SENTENCE_SPLIT.split(para):
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(sentence) > limit:
                    flush()
                    for i in range(0, len(sentence), limit):
                        chunks.append(sentence[i:i + limit])
                elif len(current) + len(sentence) + 1 > limit:
                    flush()
                    current = sentence
                else:
                    current = f"{current} {sentence}".strip()
            flush()
        elif len(current) + len(para) + 2 > limit:
            flush()
            current = para
        else:
            current = f"{current}\n\n{para}".strip() if current else para

    flush()
    return chunks


def prepare_for_tts(text: str, limit: int = TTS_CHUNK_LIMIT) -> list[str]:
    """Strip markdown, cap total length, and chunk for the TTS endpoint."""

    cleaned = strip_markdown(text)
    if not cleaned:
        cleaned = (text or "").strip()

    if len(cleaned) > TTS_MAX_TOTAL_CHARS:
        cleaned = cleaned[:TTS_MAX_TOTAL_CHARS].rstrip()

    return chunk_text(cleaned, limit)