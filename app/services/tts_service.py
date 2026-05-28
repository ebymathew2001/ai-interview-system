import base64
import io
from fastapi import HTTPException
from sarvamai import SarvamAI
from app.core.config import settings

client = SarvamAI(api_subscription_key=settings.sarvam_api_key)


async def synthesize_speech(text: str) -> str:
    """Convert question text to audio using Sarvam TTS."""
    try:
        response = client.text_to_speech.convert(
            text=text,
            target_language_code="en-IN",
            speaker="anushka",
            model="bulbul:v2",
        )
        return response.audios[0]
    except Exception as e:
        print(f"TTS error: {e}")
        raise HTTPException(status_code=502, detail="TTS service unavailable")