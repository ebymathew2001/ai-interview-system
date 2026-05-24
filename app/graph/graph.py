from langgraph.graph import StateGraph, END
from app.graph.state import InterviewState
from app.nodes.load_candidate   import load_candidate_node
from app.nodes.generate_question import generate_question_node
from app.nodes.evaluate_answer  import evaluate_answer_node
from app.nodes.check_completion import check_completion_node
from app.nodes.generate_report  import generate_report_node


def _route_after_check(state: InterviewState) -> str:
    return "generate_report" if state["is_complete"] else "generate_question"


def build_interview_graph() -> StateGraph:
    wf = StateGraph(InterviewState)

    wf.add_node("load_candidate",    load_candidate_node)
    wf.add_node("generate_question", generate_question_node)
    wf.add_node("evaluate_answer",   evaluate_answer_node)
    wf.add_node("check_completion",  check_completion_node)
    wf.add_node("generate_report",   generate_report_node)

    wf.set_entry_point("load_candidate")
    wf.add_edge("load_candidate",    "generate_question")
    wf.add_edge("generate_question", END)           # pause; caller returns question to user
    wf.add_edge("evaluate_answer",   "check_completion")
    wf.add_conditional_edges(
        "check_completion",
        _route_after_check,
        {"generate_question": "generate_question", "generate_report": "generate_report"},
    )
    wf.add_edge("generate_report", END)

    return wf


interview_graph = build_interview_graph()