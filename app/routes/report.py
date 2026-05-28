from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import InterviewSession, Report, QuestionAnswer
from app.schemas.schemas import ReportResponse

router = APIRouter()


@router.get("/{session_id}", response_model=ReportResponse, summary="Fetch final evaluation report")
def get_report(session_id: str, db: Session = Depends(get_db))-> ReportResponse:
    db_session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if db_session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    report = db.query(Report).filter(Report.session_id == session_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    answers = (
        db.query(QuestionAnswer)
        .filter(QuestionAnswer.session_id == session_id)
        .order_by(QuestionAnswer.question_index)
        .all()
    )

    return ReportResponse(
        session_id=session_id,
        candidate_name=db_session.candidate.name,
        role=db_session.candidate.role,
        overall_score=report.overall_score,
        hire_recommendation=report.hire_recommendation,
        strengths=report.strengths,
        weaknesses=report.weaknesses,
        total_questions=db_session.total_questions,
        answers=[
            {
                "question_index": a.question_index,
                "question_text":  a.question_text,
                "answer_text":    a.answer_text,
                "score":          a.score,
                "feedback":       a.feedback,
            }
            for a in answers
        ],
    )