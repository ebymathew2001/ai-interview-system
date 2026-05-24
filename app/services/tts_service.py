import base64
import io
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
        audio_bytes = base64.b64decode(response.audios[0])
        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print(f"TTS error: {e}")
        return ""