import os
import tempfile
from sarvamai import SarvamAI
from app.core.config import settings
from pathlib import Path
import tempfile

client = SarvamAI(api_subscription_key=settings.sarvam_api_key)


async def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """Convert candidate audio to text using Sarvam STT."""
    suffix = os.path.splitext(filename)[-1] or ".webm"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = None 

    try:
        with open(tmp_path, "rb") as f:
            response = client.speech_to_text.transcribe(
                file=f,
                model="saarika:v2.5",
                language_code="en-IN",
            )
        return response.transcript
    except Exception as e:
        print(f"STT error: {e}")
        return "Could not transcribe audio. Please try again."
    finally:
        if tmp_path:  
            Path(tmp_path).unlink(missing_ok=True)