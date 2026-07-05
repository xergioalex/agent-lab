"""11 — Graph Branching: multi-way conditional routing that converges.

Demonstrates ``add_conditional_edges`` with a routing function that inspects
state and dispatches to one of several handler nodes (a support-ticket
triage graph), all of which converge back into a single ``notify`` node.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/11_graph_branching/branching.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

# Categories the router can dispatch to, keyed by keyword match against the
# latest human message. Order matters: first match wins.
_KEYWORDS: dict[str, tuple[str, ...]] = {
    "bug": ("bug", "crash", "error", "broken"),
    "feature": ("feature", "request", "wish", "idea"),
    "question": ("how", "what", "why", "?"),
}


def classify(state: AgentState) -> dict[str, object]:
    """Inspect the latest human message and assign a triage category."""
    messages = state.get("messages", [])
    text = str(messages[-1].content).lower() if messages else ""
    category = "general"
    for name, keywords in _KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            category = name
            break
    logger.info("classified ticket as %r", category)
    return {"context": {**state.get("context", {}), "category": category}}


def route_by_category(state: AgentState) -> str:
    """Conditional-edge routing function: read state, return the next node name."""
    return state.get("context", {}).get("category", "general")


def _handler(category: str, action: str):
    """Build a handler node that logs a scratchpad note for its branch."""

    def _node(state: AgentState) -> dict[str, object]:
        note = f"[{category}] {action}"
        return {"scratchpad": [note]}

    return _node


def notify(state: AgentState) -> dict[str, object]:
    """Convergence node: every branch lands here before the run ends."""
    category = state.get("context", {}).get("category", "general")
    last_note = state.get("scratchpad", [])[-1] if state.get("scratchpad") else "n/a"
    reply = AIMessage(content=f"Routed as '{category}'. Action taken: {last_note}")
    return {"messages": [reply]}


def build_graph():
    """Compile the ticket-triage graph with a 4-way conditional branch."""
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify)
    graph.add_node("bug", _handler("bug", "filed to engineering backlog"))
    graph.add_node("feature", _handler("feature", "added to product roadmap"))
    graph.add_node("question", _handler("question", "answered from knowledge base"))
    graph.add_node("general", _handler("general", "forwarded to support queue"))
    graph.add_node("notify", notify)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_by_category,
        {
            "bug": "bug",
            "feature": "feature",
            "question": "question",
            "general": "general",
        },
    )
    for branch in ("bug", "feature", "question", "general"):
        graph.add_edge(branch, "notify")
    graph.add_edge("notify", END)
    return graph.compile()


TICKETS: tuple[str, ...] = (
    "The app crashes when I click save, this is a bug.",
    "Feature request: dark mode please.",
    "How do I reset my password?",
    "Just wanted to say thanks for the great support.",
)


def main() -> None:
    app = build_graph()
    for ticket in TICKETS:
        result = app.invoke({"messages": [HumanMessage(content=ticket)]})
        category = result["context"]["category"]
        reply = result["messages"][-1].content
        print(f"ticket={ticket!r} category={category} reply={reply!r}")

    print("=== TRACK1 MODULE 11: GRAPH BRANCHING COMPLETE ===")


if __name__ == "__main__":
    main()
