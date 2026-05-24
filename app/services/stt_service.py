import os
import tempfile
from openai import OpenAI
from app.core.config import settings

# Groq exposes Whisper through an OpenAI-compatible endpoint
_client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)


async def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """Transcribe audio using Whisper-large-v3 via Groq."""
    suffix = os.path.splitext(filename)[-1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            result = _client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
            )
        return result.text.strip()
    finally:
        os.unlink(tmp_path)