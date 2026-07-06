"""10 — Full Brain Simulation: integrated routing, memory, RAG, graph, and tools.

A compact capstone that wires every on-ramp subsystem into one coordinator
graph. Module 64 deepens this into the full Mini DailyBot Brain.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import (  # noqa: E402
    DEMO_TOOLS,
    AgentState,
    InMemoryGraphStore,
    InMemoryVectorStore,
    get_chat_model,
    get_logger,
)

logger = get_logger(__name__)

_POLICY_DOCS: tuple[tuple[str, str], ...] = (
    ("deploy", "Production deploys require two approvals and a passing CI run."),
    ("vacation", "Vacation requests must go through the HR portal two weeks ahead."),
)

_VECTOR = InMemoryVectorStore()
_IDS, _TEXTS = zip(*_POLICY_DOCS)
_VECTOR.add_texts(list(_TEXTS), ids=list(_IDS))

_GRAPH = InMemoryGraphStore()
_GRAPH.upsert_node("engineering", "Department", name="Engineering")
_GRAPH.upsert_node("carol", "Person", name="Carol")
_GRAPH.add_relationship("engineering", "LED_BY", "carol")

_ACTION_TOOLS = [t for t in DEMO_TOOLS if t.name in ("create_task", "send_slack")]
_TOOL_NODE = ToolNode(_ACTION_TOOLS)

_KEYWORDS: dict[str, tuple[str, ...]] = {
    "memory": ("earlier", "before", "remember"),
    "graph": ("engineering", "leads", "manager"),
    "rag": ("policy", "deploy", "vacation"),
    "tools": ("task", "create", "follow"),
}


def _needed(text: str) -> list[str]:
    lowered = text.lower()
    return [name for name, kws in _KEYWORDS.items() if any(k in lowered for k in kws)]


def plan(state: AgentState) -> dict[str, Any]:
    text = str(state["messages"][-1].content)
    needed = _needed(text)
    logger.info("brain plan: needed=%s", needed)
    return {
        "context": {
            **state.get("context", {}),
            "query": text,
            "needed": needed,
            "findings": {},
        }
    }


def memory_node(state: AgentState) -> dict[str, Any]:
    ctx = state["context"]
    if "memory" not in ctx["needed"]:
        return {}
    log = ctx.get("memory_log", [])
    finding = log[-1] if log else "no prior turns"
    return {"context": {**ctx, "findings": {**ctx["findings"], "memory": finding}}}


def graph_node(state: AgentState) -> dict[str, Any]:
    ctx = state["context"]
    if "graph" not in ctx["needed"]:
        return {}
    lead = _GRAPH.neighbors("engineering", "LED_BY")
    finding = f"Engineering led by {lead[0].properties['name']}" if lead else "unknown"
    return {"context": {**ctx, "findings": {**ctx["findings"], "graph": finding}}}


def rag_node(state: AgentState) -> dict[str, Any]:
    ctx = state["context"]
    if "rag" not in ctx["needed"]:
        return {}
    hits = _VECTOR.similarity_search(ctx["query"], k=1)
    finding = hits[0].document.text if hits else "no policy found"
    return {"context": {**ctx, "findings": {**ctx["findings"], "rag": finding}}}


def route_tools(state: AgentState) -> str:
    return "agent" if "tools" in state["context"]["needed"] else "aggregate"


def call_model(state: AgentState) -> dict[str, Any]:
    model = get_chat_model(max_tool_calls=1).bind_tools(_ACTION_TOOLS)
    return {"messages": [model.invoke(state["messages"])]}


def route_model(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "aggregate"


def aggregate(state: AgentState) -> dict[str, Any]:
    ctx = state["context"]
    parts = [f"[{k}] {v}" for k, v in ctx["findings"].items()]
    tool_msgs = [m for m in state["messages"] if getattr(m, "type", "") == "tool"]
    if tool_msgs:
        parts.append("[tools] " + " | ".join(str(m.content) for m in tool_msgs))
    answer = " || ".join(parts) if parts else "no relevant subsystem matched"
    log = list(ctx.get("memory_log", []))
    log.append(f"Q: {ctx['query']} -> {answer}")
    return {
        "messages": [AIMessage(content=answer)],
        "context": {**ctx, "memory_log": log},
    }


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("memory", memory_node)
    graph.add_node("graph", graph_node)
    graph.add_node("rag", rag_node)
    graph.add_node("agent", call_model)
    graph.add_node("tools", _TOOL_NODE)
    graph.add_node("aggregate", aggregate)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "memory")
    graph.add_edge("memory", "graph")
    graph.add_edge("graph", "rag")
    graph.add_conditional_edges("rag", route_tools, {"agent": "agent", "aggregate": "aggregate"})
    graph.add_conditional_edges("agent", route_model, {"tools": "tools", "aggregate": "aggregate"})
    graph.add_edge("tools", "agent")
    graph.add_edge("aggregate", END)
    return graph.compile()


REQUEST = (
    "Who leads engineering, what is the deploy policy, and create a task to follow up?"
)


def main() -> None:
    print("=== Full Brain Simulation ===")
    app = build_graph()
    result = app.invoke(
        {"messages": [HumanMessage(content=REQUEST)], "context": {"memory_log": []}}
    )
    needed = result["context"]["needed"]
    answer = result["messages"][-1].content
    print(f"needed_subsystems={needed}")
    print(f"answer={answer!r}")
    print("=== MODULE 10: FULL BRAIN SIMULATION COMPLETE ===")


if __name__ == "__main__":
    main()
