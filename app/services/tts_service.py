import base64

# Text-to-Speech is handled by the browser's built-in Web Speech API
# (speechSynthesis). The frontend reads the `text` field of the response and
# calls speechSynthesis.speak() directly — no server-side audio generation needed.
# This keeps the stack simple and avoids heavy TTS dependencies.

async def synthesize_speech(text: str) -> str:
    """Return an empty base64 string; frontend uses the Web Speech API."""
    return base64.b64encode(b"").decode("utf-8")