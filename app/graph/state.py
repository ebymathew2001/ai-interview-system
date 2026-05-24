from typing import TypedDict, Optional


class InterviewState(TypedDict):
    session_id:       str
    candidate_id:     int
    candidate_name:   str
    qualification:    str
    experience:       str
    skills:           str
    role:             str
    total_questions:  int
    current_index:    int
    # Each entry: {question, answer, score, feedback, question_index}
    question_history: list
    current_question: str
    answer_text:      Optional[str]
    is_complete:      bool
    report:           Optional[dict]