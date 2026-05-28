import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Candidate, InterviewSession, QuestionAnswer
from app.schemas.schemas import (
    CandidateCreate,
    SessionCreateResponse,
    CandidateProfileResponse,
)

router = APIRouter()


@router.post("/create", response_model=SessionCreateResponse, summary="Register candidate and open session")
def create_session(payload: CandidateCreate, db: Session = Depends(get_db))-> SessionCreateResponse:
    candidate = Candidate(**payload.model_dump())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    session_id = str(uuid.uuid4())
    db_session = InterviewSession(
        session_id=session_id,
        candidate_id=candidate.id,
        total_questions=settings.total_questions,
        status="in_progress",
    )
    db.add(db_session)
    db.commit()

    return SessionCreateResponse(
        session_id=session_id,
        candidate_id=candidate.id,
        total_questions=settings.total_questions,
    )


@router.get("/{session_id}", response_model=CandidateProfileResponse, summary="Fetch candidate profile for a session")
def get_session(session_id: str, db: Session = Depends(get_db)) -> CandidateProfileResponse:
    db_session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    c = db_session.candidate
    return CandidateProfileResponse(
        candidate_id=c.id,
        name=c.name,
        qualification=c.qualification,
        experience=c.experience,
        skills=c.skills,
        role=c.role,
        session_id=session_id,
        status=db_session.status,
        total_questions=db_session.total_questions,
    )

