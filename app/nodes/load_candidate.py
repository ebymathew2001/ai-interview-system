from app.graph.state import InterviewState
from app.core.config import settings


def load_candidate_node(state: InterviewState) -> InterviewState:
    """
    Initialise interview counters and history.
    Candidate profile data is already present in state (populated by the route
    from the DB before this node is called).
    """
    return {
        **state,
        "total_questions": settings.total_questions,
        "current_index":   0,
        "question_history": [],
        "current_question": "",
        "answer_text":      None,
        "is_complete":      False,
        "report":           None,
    }