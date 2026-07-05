"""62 — Incident Response Agent: graph-based root-cause analysis + tools.

Capstone that integrates **Track 6** graph memory (module `08_graph_memory_neo4j`,
`InMemoryGraphStore`) with **Track 3** tool use (`DEMO_TOOLS`): given an alert on
one service, the agent walks a `DEPENDS_ON` service graph breadth-first to
localize the unhealthy root cause(s), then dispatches remediation tools
(`create_task`, `send_slack`) via a manual `ToolNode` loop.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/62_incident_response_agent/incident_agent.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import (  # noqa: E402
    DEMO_TOOLS,
    AgentState,
    InMemoryGraphStore,
    get_chat_model,
    get_logger,
)

logger = get_logger(__name__)

# Deterministic, offline health snapshot for the toy service topology.
_HEALTH: dict[str, str] = {
    "checkout": "unhealthy",
    "payments": "healthy",
    "inventory": "healthy",
    "database": "unhealthy",
    "network": "healthy",
}

_REMEDIATION_TOOLS = [t for t in DEMO_TOOLS if t.name in ("create_task", "send_slack")]
_TOOL_NODE = ToolNode(_REMEDIATION_TOOLS)


def _build_graph_store() -> InMemoryGraphStore:
    """Build the toy DEPENDS_ON service dependency graph."""
    store = InMemoryGraphStore()
    for service in _HEALTH:
        store.upsert_node(service, "Service", health=_HEALTH[service])
    store.add_relationship("checkout", "DEPENDS_ON", "payments")
    store.add_relationship("checkout", "DEPENDS_ON", "inventory")
    store.add_relationship("payments", "DEPENDS_ON", "database")
    store.add_relationship("payments", "DEPENDS_ON", "network")
    store.add_relationship("inventory", "DEPENDS_ON", "database")
    return store


_STORE = _build_graph_store()

_ALERT_SERVICE = "checkout"


def detect_incident(state: AgentState) -> dict[str, Any]:
    """Record the incoming alert."""
    logger.info("incident detected on service=%s", _ALERT_SERVICE)
    return {"context": {**state.get("context", {}), "alert_service": _ALERT_SERVICE}}


def localize_root_cause(state: AgentState) -> dict[str, Any]:
    """Breadth-first walk of the dependency graph to find unhealthy leaves."""
    start = state["context"]["alert_service"]
    visited = {start}
    queue = [start]
    trace = [start]
    root_causes: list[str] = []

    while queue:
        current = queue.pop(0)
        for neighbor in _STORE.neighbors(current, rel_type="DEPENDS_ON"):
            if neighbor.id in visited:
                continue
            visited.add(neighbor.id)
            trace.append(neighbor.id)
            if neighbor.properties.get("health") == "unhealthy":
                root_causes.append(neighbor.id)
            else:
                queue.append(neighbor.id)

    logger.info("root causes localized: %s", root_causes)
    return {"context": {**state["context"], "trace": trace, "root_causes": root_causes}}


def call_model(state: AgentState) -> dict[str, Any]:
    """Agent node: dispatch remediation tools for the localized root cause."""
    model = get_chat_model(max_tool_calls=len(_REMEDIATION_TOOLS)).bind_tools(
        _REMEDIATION_TOOLS
    )
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def route_after_model(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "report"


def report(state: AgentState) -> dict[str, Any]:
    """Convergence node: summarize the incident, root cause, and actions."""
    return {"context": {**state["context"]}}


def build_graph():
    """Compile the incident-response graph (RCA walk + remediation tool loop)."""
    graph = StateGraph(AgentState)
    graph.add_node("detect", detect_incident)
    graph.add_node("localize", localize_root_cause)
    graph.add_node("agent", call_model)
    graph.add_node("tools", _TOOL_NODE)
    graph.add_node("report", report)

    graph.add_edge(START, "detect")
    graph.add_edge("detect", "localize")
    graph.add_edge("localize", "agent")
    graph.add_conditional_edges(
        "agent", route_after_model, {"tools": "tools", "report": "report"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("report", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    root_cause_hint = "database"  # matches the injected unhealthy dependency
    request = HumanMessage(
        content=(
            f"Checkout is down. Open a task and send a slack message about the "
            f"{root_cause_hint} outage root cause."
        )
    )
    result = app.invoke({"messages": [request]})
    context = result["context"]

    print(f"alert_service={context['alert_service']}")
    print(f"dependency_trace={context['trace']}")
    print(f"root_causes={context['root_causes']}")
    final_answer = result["messages"][-1].content
    print(f"final_answer={final_answer!r}")
    print("=== TRACK9 MODULE 62: INCIDENT RESPONSE AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
