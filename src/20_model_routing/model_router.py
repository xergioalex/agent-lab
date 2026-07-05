"""20 — Model Routing: route by difficulty/cost to different model configs.

A classifier reads the incoming request and picks a *tier*: cheap-and-fast
for simple requests, capable-and-expensive for complex ones. This is the
same `add_conditional_edges` pattern module 11 used for ticket triage,
applied to a cost/quality trade-off instead of a topic split. Offline, each
tier maps to a differently configured `get_chat_model(...)` (the offline
`FakeToolCallingModel` stands in for, e.g., `gpt-4o-mini` vs `gpt-4o`).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/20_model_routing/model_router.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

# Requests longer than this, or matching a complexity keyword, are routed to
# the capable (slower, pricier) tier.
WORD_COUNT_THRESHOLD = 12
COMPLEX_KEYWORDS = ("architecture", "compare", "trade-off", "root cause", "design")

# Per-tier cost estimate (USD per request) — illustrative, not a live price.
COST_PER_TIER = {"cheap": 0.0002, "capable": 0.0100}


def classify_difficulty(state: AgentState) -> dict[str, object]:
    """Read the latest human message and assign a routing tier."""
    text = str(state["messages"][-1].content)
    word_count = len(text.split())
    is_complex = word_count > WORD_COUNT_THRESHOLD or any(
        keyword in text.lower() for keyword in COMPLEX_KEYWORDS
    )
    difficulty = "complex" if is_complex else "simple"
    logger.info("classified request as %r (%d words)", difficulty, word_count)
    return {"context": {**state.get("context", {}), "difficulty": difficulty}}


def route_by_difficulty(state: AgentState) -> str:
    """Conditional-edge router: pure read of state, no side effects."""
    return state["context"]["difficulty"]


def cheap_model_node(state: AgentState) -> dict[str, object]:
    """Fast, low-cost tier: short canned answer, no tool budget."""
    model = get_chat_model(responses=["Quick answer from the cheap/fast model."], max_tool_calls=0)
    reply = model.invoke(state["messages"])
    return {
        "messages": [reply],
        "context": {**state["context"], "model_tier": "cheap", "estimated_cost_usd": COST_PER_TIER["cheap"]},
    }


def capable_model_node(state: AgentState) -> dict[str, object]:
    """Slow, high-cost tier: thorough canned answer, larger tool budget."""
    model = get_chat_model(
        responses=["Detailed, carefully reasoned answer from the capable model."],
        max_tool_calls=2,
    )
    reply = model.invoke(state["messages"])
    return {
        "messages": [reply],
        "context": {**state["context"], "model_tier": "capable", "estimated_cost_usd": COST_PER_TIER["capable"]},
    }


def build_graph():
    """Compile the difficulty-routed graph."""
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_difficulty)
    graph.add_node("cheap", cheap_model_node)
    graph.add_node("capable", capable_model_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify", route_by_difficulty, {"simple": "cheap", "complex": "capable"}
    )
    graph.add_edge("cheap", END)
    graph.add_edge("capable", END)
    return graph.compile()


REQUESTS: tuple[str, ...] = (
    "What time is standup?",
    "Compare the trade-offs of a microservices architecture versus a monolith for our on-call rotation.",
)


def main() -> None:
    app = build_graph()
    total_cost = 0.0
    for request in REQUESTS:
        result = app.invoke({"messages": [HumanMessage(content=request)]})
        tier = result["context"]["model_tier"]
        cost = result["context"]["estimated_cost_usd"]
        reply = result["messages"][-1].content
        total_cost += cost
        print(f"request={request!r} tier={tier} cost_usd={cost} reply={reply!r}")

    print(f"total_cost_usd={round(total_cost, 4)}")
    print("=== TRACK2 MODULE 20: MODEL ROUTING COMPLETE ===")


if __name__ == "__main__":
    main()
