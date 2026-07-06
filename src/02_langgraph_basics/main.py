"""02 — LangGraph Basics: the module-01 pipeline as a compiled StateGraph.

Six nodes with a conditional edge after ``validate``: invalid messages route
to ``reject``, incidents to ``escalate``, everything else to ``standard``.
All branches converge on ``format`` before END.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


class GraphState(TypedDict, total=False):
    message: str
    priority: str
    category: str
    enriched: str
    valid: bool
    route: str
    response: str
    audit: list[str]


def _audit(state: GraphState, step: str) -> list[str]:
    return [*state.get("audit", []), step]


def ingest_node(state: GraphState) -> dict[str, object]:
    return {"audit": _audit(state, "ingest")}


def classify_node(state: GraphState) -> dict[str, object]:
    text = state["message"].lower()
    category = "incident" if any(w in text for w in ("down", "crash", "block")) else "request"
    priority = "high" if category == "incident" else "normal"
    return {
        "category": category,
        "priority": priority,
        "audit": _audit(state, "classify"),
    }


def enrich_node(state: GraphState) -> dict[str, object]:
    prefix = f"[{state['priority']}/{state['category']}]"
    return {"enriched": f"{prefix} {state['message']}", "audit": _audit(state, "enrich")}


def validate_node(state: GraphState) -> dict[str, object]:
    return {"valid": len(state["message"]) >= 3, "audit": _audit(state, "validate")}


def route_after_validate(state: GraphState) -> str:
    if not state.get("valid"):
        return "reject"
    if state.get("category") == "incident":
        return "escalate"
    return "standard"


def escalate_node(state: GraphState) -> dict[str, object]:
    return {"route": "escalate", "audit": _audit(state, "escalate")}


def standard_node(state: GraphState) -> dict[str, object]:
    return {"route": "standard", "audit": _audit(state, "standard")}


def reject_node(state: GraphState) -> dict[str, object]:
    return {"route": "reject", "audit": _audit(state, "reject")}


def format_node(state: GraphState) -> dict[str, object]:
    route = state.get("route", "standard")
    if route == "reject":
        response = "rejected: message too short"
    elif route == "escalate":
        response = f"escalated: {state.get('enriched', state['message'])}"
    else:
        response = f"accepted: {state.get('enriched', state['message'])}"
    return {"response": response, "audit": _audit(state, "format")}


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("ingest", ingest_node)
    graph.add_node("classify", classify_node)
    graph.add_node("enrich", enrich_node)
    graph.add_node("validate", validate_node)
    graph.add_node("escalate", escalate_node)
    graph.add_node("standard", standard_node)
    graph.add_node("reject", reject_node)
    graph.add_node("format", format_node)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "classify")
    graph.add_edge("classify", "enrich")
    graph.add_edge("enrich", "validate")
    graph.add_conditional_edges(
        "validate",
        route_after_validate,
        {"escalate": "escalate", "standard": "standard", "reject": "reject"},
    )
    for branch in ("escalate", "standard", "reject"):
        graph.add_edge(branch, "format")
    graph.add_edge("format", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({"message": "start the morning standup"})
    print(f"message=start response={result['response']!r} audit={result['audit']}")
    blocked = app.invoke({"message": "we are blocked on production"})
    print(f"message=blocked route={blocked['route']} response={blocked['response']!r}")
    print("=== MODULE 02: LANGGRAPH BASICS COMPLETE ===")


if __name__ == "__main__":
    main()
