"""04 — Routing & Branches: four-way intent router with convergence.

Routes blocker, billing, technical, and general intents to dedicated handler
nodes, then merges at ``synthesize`` before END.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

_INTENTS: dict[str, tuple[str, ...]] = {
    "blocker": ("block", "blocked", "stuck", "down"),
    "billing": ("invoice", "billing", "payment", "charge"),
    "technical": ("api", "error", "bug", "latency"),
}


def classify_intent(state: AgentState) -> dict[str, object]:
    text = str(state["messages"][-1].content).lower()
    intent = "general"
    for name, keywords in _INTENTS.items():
        if any(keyword in text for keyword in keywords):
            intent = name
            break
    logger.info("intent=%s", intent)
    return {"context": {**state.get("context", {}), "intent": intent}}


def route_intent(state: AgentState) -> str:
    return state.get("context", {}).get("intent", "general")


def _handler(intent: str, action: str):
    def _node(state: AgentState) -> dict[str, object]:
        return {"scratchpad": [f"[{intent}] {action}"]}

    return _node


def synthesize(state: AgentState) -> dict[str, object]:
    intent = state.get("context", {}).get("intent", "general")
    note = state.get("scratchpad", [])[-1] if state.get("scratchpad") else "n/a"
    reply = AIMessage(content=f"intent={intent} action={note}")
    return {"messages": [reply]}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_intent)
    graph.add_node("blocker", _handler("blocker", "paged on-call and opened incident"))
    graph.add_node("billing", _handler("billing", "routed to finance queue"))
    graph.add_node("technical", _handler("technical", "escalated to platform team"))
    graph.add_node("general", _handler("general", "answered from support playbook"))
    graph.add_node("synthesize", synthesize)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_intent,
        {
            "blocker": "blocker",
            "billing": "billing",
            "technical": "technical",
            "general": "general",
        },
    )
    for branch in ("blocker", "billing", "technical", "general"):
        graph.add_edge(branch, "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()


REQUESTS: tuple[str, ...] = (
    "we are blocked on the release",
    "my invoice looks wrong",
    "api latency is spiking",
    "thanks for the help",
)


def main() -> None:
    app = build_graph()
    for request in REQUESTS:
        result = app.invoke({"messages": [HumanMessage(content=request)]})
        print(result["messages"][-1].content)
    print("=== MODULE 04: ROUTING AND BRANCHES COMPLETE ===")


if __name__ == "__main__":
    main()
