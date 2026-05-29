from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import InterviewSession, InterviewStateModel, QuestionAnswer, Report
from app.schemas.schemas import AgentRespondRequest, AgentRespondResponse
from app.graph.state import InterviewState
from app.graph.graph import interview_graph
import json

router = APIRouter()


def _save_state(db: Session, sid: str, state: InterviewState) -> None:
    row = db.query(InterviewStateModel).filter(
        InterviewStateModel.session_id == sid
    ).first()
    if row:
        row.state_json = json.dumps(state)
    else:
        db.add(InterviewStateModel(
            session_id=sid,
            state_json=json.dumps(state)
        ))
    db.commit()

def _get_state(db: Session, sid: str) -> InterviewState | None:
    row = db.query(InterviewStateModel).filter(
        InterviewStateModel.session_id == sid
    ).first()
    if row:
        return json.loads(row.state_json)
    return None

def _delete_state(db: Session, sid: str) -> None:
    db.query(InterviewStateModel).filter(
        InterviewStateModel.session_id == sid
    ).delete()
    db.commit()

@router.post("/respond", response_model=AgentRespondResponse, summary="Central interview loop")
async def agent_respond(payload: AgentRespondRequest, db: Session = Depends(get_db)) -> AgentRespondResponse:
    sid = payload.session_id

    # ── FIRST CALL:
    if _get_state(db, sid) is None:
        db_session = db.query(InterviewSession).filter(
            InterviewSession.session_id == sid
        ).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if db_session.status == "completed":
            raise HTTPException(status_code=400, detail="Interview already completed")

        initial: InterviewState = {
        "session_id":       sid,
        "candidate_id":     0,    
        "candidate_name":   "",  
        "qualification":    "",   
        "experience":       "",   
        "skills":           "",   
        "role":             "",  
        "total_questions":  0,    
        "current_index":    0,
        "question_history": [],
        "current_question": "",
        "answer_text":      None,
        "is_complete":      False,
        "report":           None,
    }
        #invoke
        state = interview_graph.invoke(initial)
        _save_state(db, sid, state)

        return AgentRespondResponse(
            question_text=state["current_question"],
            question_index=state["current_index"] + 1,
            is_complete=False,
        )

    # ── SUBSEQUENT CALLS: evaluate answer → decide next step ─────────────────
    state = _get_state(db, sid)

    if state["is_complete"]:
        raise HTTPException(status_code=400, detail="Interview already completed")
    if not payload.answer_text:
        raise HTTPException(status_code=422, detail="answer_text is required for subsequent calls")

    state = {**state, "answer_text": payload.answer_text}

    #invoke 
    state = interview_graph.invoke(state)

   # persist Q&A if new entry was added
    if state["question_history"]:
        last_qa = state["question_history"][-1]
        existing = db.query(QuestionAnswer).filter(
            QuestionAnswer.session_id == sid,
            QuestionAnswer.question_index == last_qa["question_index"]
        ).first()
        if not existing:
            db.add(QuestionAnswer(
                session_id=sid,
                question_index=last_qa["question_index"],
                question_text=last_qa["question"],
                answer_text=last_qa["answer"],
                score=last_qa["score"],
                feedback=last_qa["feedback"],
            ))
            db.commit()

    
    # interview complete
    if state["is_complete"]:
      
        rpt = state["report"]
        db.add(Report(
            session_id=sid,
            overall_score=rpt["overall_score"],
            hire_recommendation=rpt["hire_recommendation"],
            strengths=rpt["strengths"],
            weaknesses=rpt["weaknesses"],
        ))

        db_session.status = "completed"
        db_session.completed_at = datetime.now(timezone.utc)
        db.commit()

        _delete_state(db, sid)

        return AgentRespondResponse(
            question_text=None,
            question_index=None,
            is_complete=True,
        )

    
    _save_state(db, sid, state)

    return AgentRespondResponse(
        question_text=state["current_question"],
        question_index=state["current_index"] + 1,
        is_complete=False,
    )