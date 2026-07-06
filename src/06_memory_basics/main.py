"""06 — Memory Basics: episodic event log wired into a LangGraph.

``write_event`` persists structured events; ``recall`` reads them back into
the graph state before ``respond`` synthesizes an answer that cites memory.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

_SESSION_LOG: list[dict[str, Any]] = []


def write_event(state: AgentState) -> dict[str, object]:
    text = str(state["messages"][-1].content)
    event = {"event": "user_message", "text": text}
    if "login" in text.lower():
        event = {"event": "login", "user": "demo-user"}
    _SESSION_LOG.append(event)
    logger.info("wrote event=%s", event)
    return {"context": {**state.get("context", {}), "last_event": event}}


def recall(state: AgentState) -> dict[str, object]:
    return {"context": {**state["context"], "memory": list(_SESSION_LOG)}}


def respond(state: AgentState) -> dict[str, object]:
    memory = state["context"]["memory"]
    summary = "; ".join(f"{e['event']}" for e in memory)
    reply = AIMessage(content=f"memory_entries={len(memory)} events=[{summary}]")
    return {"messages": [reply]}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("write_event", write_event)
    graph.add_node("recall", recall)
    graph.add_node("respond", respond)
    graph.add_edge(START, "write_event")
    graph.add_edge("write_event", "recall")
    graph.add_edge("recall", "respond")
    graph.add_edge("respond", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content="user login successful")]})
    print(result["messages"][-1].content)
    print(f"stored={_SESSION_LOG}")
    print("=== MODULE 06: MEMORY BASICS COMPLETE ===")


if __name__ == "__main__":
    main()
