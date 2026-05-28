from langchain_groq import ChatGroq
from app.graph.state import InterviewState
from app.graph.prompts import QUESTION_GENERATION_PROMPT
from app.core.config import settings


def generate_question_node(state: InterviewState) -> dict:
    """Generate the next interview question via LLM."""
    history_lines = "\n".join(
        f"Q{qa['question_index']}: {qa['question']}"
        for qa in state["question_history"]
    ) or "No previous questions."

    prompt = QUESTION_GENERATION_PROMPT.format(
        name=state["candidate_name"],
        role=state["role"],
        qualification=state["qualification"],
        experience=state["experience"],
        skills=state["skills"],
        current_index=state["current_index"] + 1,
        total_questions=state["total_questions"],
        history=history_lines,
    )

    llm = ChatGroq(
        groq_api_key=settings.groq_api_key,
        model_name=settings.llm_model,
        temperature=0.7,
    )
    response = llm.invoke(prompt)

    return {
        **state,
        "current_question": response.content.strip(),
    }