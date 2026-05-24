import json
from langchain_groq import ChatGroq
from app.graph.state import InterviewState
from app.graph.prompts import REPORT_GENERATION_PROMPT
from app.core.config import settings


def generate_report_node(state: InterviewState) -> InterviewState:
    """Generate the final hire/reject report with LLM analysis."""
    history = state["question_history"]
    avg     = sum(qa["score"] for qa in history) / len(history) if history else 0.0

    qa_summary = "\n".join(
        f"Q{qa['question_index']}: {qa['question']}\n"
        f"A: {qa['answer']}\n"
        f"Score: {qa['score']}/10 — {qa['feedback']}"
        for qa in history
    )

    llm = ChatGroq(
        groq_api_key=settings.groq_api_key,
        model_name=settings.llm_model,
        temperature=0.2,
    )
    prompt = REPORT_GENERATION_PROMPT.format(
        name=state["candidate_name"],
        role=state["role"],
        qualification=state["qualification"],
        experience=state["experience"],
        skills=state["skills"],
        qa_summary=qa_summary,
        avg_score=avg,
    )
    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content.strip())
        rec        = result.get("hire_recommendation", "maybe")
        strengths  = result.get("strengths",  "Technical knowledge demonstrated")
        weaknesses = result.get("weaknesses", "Further evaluation recommended")
    except (json.JSONDecodeError, KeyError):
        rec, strengths, weaknesses = "maybe", "Completed the interview", "Further evaluation needed"

    return {
        **state,
        "report": {
            "overall_score":       round(avg, 2),
            "hire_recommendation": rec,
            "strengths":           strengths,
            "weaknesses":          weaknesses,
        },
    }