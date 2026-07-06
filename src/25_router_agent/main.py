"""25 — Router Agent: classify intent and dispatch to per-intent sub-graphs.

Deepens module 04's single conditional edge: instead of routing to a plain
handler function, ``classify`` routes to a fully independent, compiled
``StateGraph`` per intent (a "sub-graph"). Each sub-graph is a self-contained
worker that reads the same ``AgentState`` and reaches its own ``END`` — the
parent graph treats a compiled sub-graph exactly like any other node.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/25_router_agent/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, DEMO_TOOLS, get_logger  # noqa: E402

logger = get_logger(__name__)

_TOOLS_BY_NAME = {tool.name: tool for tool in DEMO_TOOLS}

_KEYWORDS: dict[str, tuple[str, ...]] = {
    "weather": ("weather", "forecast", "temperature"),
    "task": ("task", "todo", "remind"),
}

_CITY_PATTERN = re.compile(r"in ([A-Z][a-zA-Z]+)")


def classify(state: AgentState) -> dict[str, object]:
    """Inspect the latest human message and assign an intent."""
    text = str(state["messages"][-1].content).lower()
    intent = next(
        (name for name, kws in _KEYWORDS.items() if any(kw in text for kw in kws)),
        "general",
    )
    logger.info("classified intent=%r", intent)
    return {"context": {**state.get("context", {}), "intent": intent}}


def route_by_intent(state: AgentState) -> str:
    """Conditional-edge router: read state, return the intent key."""
    return state["context"]["intent"]


def build_weather_subgraph():
    """Sub-graph: look up the weather for the city mentioned in the message."""

    def handle(state: AgentState) -> dict[str, object]:
        text = str(state["messages"][-1].content)
        match = _CITY_PATTERN.search(text)
        city = match.group(1) if match else "your area"
        reply = _TOOLS_BY_NAME["get_weather"].invoke({"city": city})
        return {"messages": [AIMessage(content=reply)]}

    graph = StateGraph(AgentState)
    graph.add_node("handle", handle)
    graph.add_edge(START, "handle")
    graph.add_edge("handle", END)
    return graph.compile()


def build_task_subgraph():
    """Sub-graph: create a tracker task from the message."""

    def handle(state: AgentState) -> dict[str, object]:
        text = str(state["messages"][-1].content)
        reply = _TOOLS_BY_NAME["create_task"].invoke({"title": text})
        return {"messages": [AIMessage(content=reply)]}

    graph = StateGraph(AgentState)
    graph.add_node("handle", handle)
    graph.add_edge(START, "handle")
    graph.add_edge("handle", END)
    return graph.compile()


def build_general_subgraph():
    """Sub-graph: fallback acknowledgement for anything unclassified."""

    def handle(state: AgentState) -> dict[str, object]:
        text = str(state["messages"][-1].content)
        return {"messages": [AIMessage(content=f"Acknowledged: {text}")]}

    graph = StateGraph(AgentState)
    graph.add_node("handle", handle)
    graph.add_edge(START, "handle")
    graph.add_edge("handle", END)
    return graph.compile()


def build_graph():
    """Compile the parent graph: classify, then dispatch to a sub-graph."""
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify)
    graph.add_node("weather", build_weather_subgraph())
    graph.add_node("task", build_task_subgraph())
    graph.add_node("general", build_general_subgraph())

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_by_intent,
        {"weather": "weather", "task": "task", "general": "general"},
    )
    graph.add_edge("weather", END)
    graph.add_edge("task", END)
    graph.add_edge("general", END)
    return graph.compile()


MESSAGES: tuple[str, ...] = (
    "What's the weather in Tokyo?",
    "Create a task to update the roadmap.",
    "Thanks for all your help today!",
)


def main() -> None:
    app = build_graph()
    for text in MESSAGES:
        result = app.invoke({"messages": [HumanMessage(content=text)]})
        intent = result["context"]["intent"]
        reply = result["messages"][-1].content
        print(f"message={text!r} intent={intent} reply={reply!r}")

    print("=== TRACK3 MODULE 25: ROUTER AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
