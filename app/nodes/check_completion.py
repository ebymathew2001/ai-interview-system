from app.graph.state import InterviewState


def check_completion_node(state: InterviewState) -> dict:
    """Mark the interview complete once all questions have been answered."""
    return {
        "is_complete": state["current_index"] >= state["total_questions"]
    }