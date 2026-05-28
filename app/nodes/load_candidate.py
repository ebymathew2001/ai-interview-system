from app.graph.state import InterviewState
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.models import InterviewSession


def load_candidate_node(state: InterviewState) -> dict:
    """
    Fetch candidate profile from DB using session_id in state.
    Initialise interview counters and history.
    """

    db = SessionLocal()
    try:
        db_session = db.query(InterviewSession).filter(
            InterviewSession.session_id == state["session_id"]
        ).first()

        c = db_session.candidate

        return {
            "candidate_id":    c.id,
            "candidate_name":  c.name,
            "qualification":   c.qualification,
            "experience":      c.experience,
            "skills":          c.skills,
            "role":            c.role,
            "total_questions": db_session.total_questions,
            "current_index":   0,
            "question_history": [],
            "current_question": "",
            "answer_text":      None,
            "is_complete":      False,
            "report":           None,
        }
    finally:
        db.close()