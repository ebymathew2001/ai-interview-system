from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import InterviewSession, QuestionAnswer, Report
from app.schemas.schemas import AgentRespondRequest, AgentRespondResponse
from app.graph.state import InterviewState
from app.nodes.load_candidate    import load_candidate_node
from app.nodes.generate_question import generate_question_node
from app.nodes.evaluate_answer   import evaluate_answer_node
from app.nodes.check_completion  import check_completion_node
from app.nodes.generate_report   import generate_report_node

router = APIRouter()

# In-memory state store.  Key: session_id  Value: InterviewState
_states: dict[str, InterviewState] = {}


@router.post("/respond", response_model=AgentRespondResponse, summary="Central interview loop")
async def agent_respond(payload: AgentRespondRequest, db: Session = Depends(get_db)):
    sid = payload.session_id

    # ── FIRST CALL: no answer, no existing state ─────────────────────────────
    if sid not in _states:
        db_session = db.query(InterviewSession).filter(
            InterviewSession.session_id == sid
        ).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if db_session.status == "completed":
            raise HTTPException(status_code=400, detail="Interview already completed")

        c = db_session.candidate
        initial: InterviewState = {
            "session_id":       sid,
            "candidate_id":     c.id,
            "candidate_name":   c.name,
            "qualification":    c.qualification,
            "experience":       c.experience,
            "skills":           c.skills,
            "role":             c.role,
            "total_questions":  db_session.total_questions,
            "current_index":    0,
            "question_history": [],
            "current_question": "",
            "answer_text":      None,
            "is_complete":      False,
            "report":           None,
        }

        state = load_candidate_node(initial)
        state = generate_question_node(state)
        _states[sid] = state

        return AgentRespondResponse(
            question_text=state["current_question"],
            question_index=state["current_index"] + 1,
            is_complete=False,
        )

    # ── SUBSEQUENT CALLS: evaluate answer → decide next step ─────────────────
    state = _states[sid]

    if state["is_complete"]:
        raise HTTPException(status_code=400, detail="Interview already completed")
    if not payload.answer_text:
        raise HTTPException(status_code=422, detail="answer_text is required for subsequent calls")

    state = {**state, "answer_text": payload.answer_text}
    state = evaluate_answer_node(state)

    # Persist the evaluated Q&A row immediately
    last_qa = state["question_history"][-1]
    db.add(QuestionAnswer(
        session_id=sid,
        question_index=last_qa["question_index"],
        question_text=last_qa["question"],
        answer_text=last_qa["answer"],
        score=last_qa["score"],
        feedback=last_qa["feedback"],
    ))
    db.commit()

    state = check_completion_node(state)

    if state["is_complete"]:
        # Generate and persist report
        state = generate_report_node(state)
        rpt = state["report"]

        db.add(Report(
            session_id=sid,
            overall_score=rpt["overall_score"],
            hire_recommendation=rpt["hire_recommendation"],
            strengths=rpt["strengths"],
            weaknesses=rpt["weaknesses"],
        ))

        db_sess = db.query(InterviewSession).filter(
            InterviewSession.session_id == sid
        ).first()
        db_sess.status = "completed"
        db_sess.completed_at = datetime.utcnow()
        db.commit()

        del _states[sid]

        return AgentRespondResponse(
            question_text=None,
            question_index=None,
            is_complete=True,
        )

    state = generate_question_node(state)
    _states[sid] = state

    return AgentRespondResponse(
        question_text=state["current_question"],
        question_index=state["current_index"] + 1,
        is_complete=False,
    )