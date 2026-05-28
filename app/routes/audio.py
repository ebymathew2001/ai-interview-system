from fastapi import APIRouter, UploadFile, File
from app.schemas.schemas import AudioToTextResponse, TextToAudioRequest, TextToAudioResponse
from app.services.stt_service import transcribe_audio
from app.services.tts_service import synthesize_speech

router = APIRouter()


@router.post("/audio-to-text", response_model=AudioToTextResponse, summary="Convert recorded audio to transcript")
async def audio_to_text(audio: UploadFile = File(...))-> AudioToTextResponse:
    raw_bytes = await audio.read()
    transcript = await transcribe_audio(raw_bytes, audio.filename or "recording.webm")
    return AudioToTextResponse(transcript=transcript)


@router.post("/text-to-audio", response_model=TextToAudioResponse, summary="Convert question text to audio")
async def text_to_audio(payload: TextToAudioRequest) -> TextToAudioResponse:
    audio_b64 = await synthesize_speech(payload.text)
    return TextToAudioResponse(audio_base64=audio_b64, text=payload.text)