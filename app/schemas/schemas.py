from typing import Optional
from pydantic import BaseModel


# ── Session ──────────────────────────────────────────────────────────────────

class CandidateCreate(BaseModel):
    name:          str
    qualification: str
    experience:    str
    skills:        str
    role:          str


class SessionCreateResponse(BaseModel):
    session_id:      str
    candidate_id:    int
    total_questions: int


class CandidateProfileResponse(BaseModel):
    candidate_id:  int
    name:          str
    qualification: str
    experience:    str
    skills:        str
    role:          str
    session_id:    str
    status:        str


# ── Agent ────────────────────────────────────────────────────────────────────

class AgentRespondRequest(BaseModel):
    session_id:     str
    answer_text:    Optional[str] = None
    question_index: Optional[int] = None


class AgentRespondResponse(BaseModel):
    question_text:  Optional[str]
    question_index: Optional[int]
    is_complete:    bool


# ── Audio ────────────────────────────────────────────────────────────────────

class AudioToTextResponse(BaseModel):
    transcript: str


class TextToAudioRequest(BaseModel):
    text: str


class TextToAudioResponse(BaseModel):
    audio_base64: str
    text:         str


# ── Report ───────────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    session_id:         str
    candidate_name:     str
    role:               str
    overall_score:      float
    hire_recommendation: str
    strengths:          str
    weaknesses:         str
    total_questions:    int
    answers:            list[dict]