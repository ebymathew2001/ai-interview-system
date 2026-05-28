import json
from langchain_groq import ChatGroq
from app.graph.state import InterviewState
from app.graph.prompts import ANSWER_EVALUATION_PROMPT
from app.core.config import settings


def evaluate_answer_node(state: InterviewState) -> InterviewState:
    """Evaluate the candidate's answer with LLM scoring."""
    llm = ChatGroq(
        groq_api_key=settings.groq_api_key,
        model_name=settings.llm_model,
        temperature=0.1,
    )
    prompt = ANSWER_EVALUATION_PROMPT.format(
        role=state["role"],
        skills=state["skills"],
        question=state["current_question"],
        answer=state["answer_text"] or "(no answer provided)",
    )
    response = llm.invoke(prompt)

    try:
        result   = json.loads(response.content.strip())
        score    = max(0.0, min(10.0, float(result.get("score", 5.0))))
        feedback = result.get("feedback", "Answer received.")
    except (json.JSONDecodeError, ValueError, KeyError):
        score, feedback = 5.0, "Answer evaluated."

    next_index = state["current_index"] + 1

    qa_entry = {
        "question":       state["current_question"],
        "answer":         state["answer_text"] or "",
        "score":          score,
        "feedback":       feedback,
        "question_index": next_index,
    }
    return {
        "question_history": state["question_history"] + [qa_entry],
        "current_index":    next_index,
        "answer_text":      None,
    }