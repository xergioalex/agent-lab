"""64 — Mini DailyBot Brain: the capstone of capstones.

Deepens `src/10_full_brain_simulation` (on-ramp integrated brain) into the full
offline "mini AI operating system" that wires together every subsystem the
curriculum built:

- **Routing** (Track 1, module `11_graph_branching`) — a coordinator classifies
  which subsystems a request needs.
- **Memory** (Track 4, module `06_memory_basics`) — a session log persisted
  across turns.
- **RAG** (Track 5, `InMemoryVectorStore`) — retrieval over a policy corpus.
- **Graph** (Track 6, `InMemoryGraphStore`) — an org-chart dependency walk.
- **Tools** (Track 3, `DEMO_TOOLS`) — a manual `ToolNode` loop for actions.
- **Multi-agent cooperation** (Track 7, module `09_multi_agent_systems`) —
  independent specialist nodes contributing to one shared plan.
- **Observability** (Track 8) — every step is logged via `get_logger` with a
  structured, deterministic summary of which subsystems fired.

One end-to-end multi-step request exercises all subsystems in a single run;
a follow-up turn proves memory persists across turns.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/64_mini_dailybot_brain/main.py`.
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

# -- knowledge sources (RAG + graph), mirroring 63_company_brain's shape -----

_POLICY_DOCS: tuple[tuple[str, str], ...] = (
    ("vacation", "Vacation requests must go through the HR portal two weeks ahead."),
    ("deploy", "Production deploys require two approvals and a passing CI run."),
)


def _build_vector_store() -> InMemoryVectorStore:
    store = InMemoryVectorStore()
    ids, texts = zip(*_POLICY_DOCS)
    store.add_texts(list(texts), ids=list(ids))
    return store


def _build_graph_store() -> InMemoryGraphStore:
    store = InMemoryGraphStore()
    store.upsert_node("carol", "Person", name="Carol")
    store.upsert_node("engineering", "Department", name="Engineering")
    store.add_relationship("engineering", "LED_BY", "carol")
    return store


_VECTOR_STORE = _build_vector_store()
_GRAPH_STORE = _build_graph_store()
_ACTION_TOOLS = [t for t in DEMO_TOOLS if t.name in ("create_task", "send_slack")]
_TOOL_NODE = ToolNode(_ACTION_TOOLS)

_SPECIALIST_KEYWORDS: dict[str, tuple[str, ...]] = {
    "memory": ("remind", "before", "earlier", "just ask"),
    "graph": ("engineering", "leads", "manager"),
    "rag": ("policy", "deploy", "vacation"),
    "tools": ("task", "follow up", "create"),
}


def _needed_subsystems(text: str) -> list[str]:
    lowered = text.lower()
    return [
        name
        for name, keywords in _SPECIALIST_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]


def plan(state: AgentState) -> dict[str, Any]:
    """Coordinator: route the request to the subsystems it actually needs."""
    text = str(state["messages"][-1].content)
    needed = _needed_subsystems(text)
    logger.info("brain plan: query=%r needed=%s", text, needed)
    return {
        "context": {
            **state.get("context", {}),
            "query": text,
            "needed": needed,
            "findings": {},
        }
    }


def memory_specialist(state: AgentState) -> dict[str, Any]:
    """Recall from the persistent session log."""
    context = state["context"]
    if "memory" not in context["needed"]:
        return {}
    log = context.get("memory_log", [])
    finding = log[-1] if log else "no prior turns recorded yet"
    return {"context": {**context, "findings": {**context["findings"], "memory": finding}}}


def graph_specialist(state: AgentState) -> dict[str, Any]:
    """Walk the org graph for a leadership fact."""
    context = state["context"]
    if "graph" not in context["needed"]:
        return {}
    lead = _GRAPH_STORE.neighbors("engineering", "LED_BY")
    finding = f"Engineering is led by {lead[0].properties['name']}" if lead else "unknown"
    return {"context": {**context, "findings": {**context["findings"], "graph": finding}}}


def rag_specialist(state: AgentState) -> dict[str, Any]:
    """Retrieve a policy passage relevant to the request."""
    context = state["context"]
    if "rag" not in context["needed"]:
        return {}
    hits = _VECTOR_STORE.similarity_search(context["query"], k=1)
    finding = hits[0].document.text if hits else "no matching policy found"
    return {"context": {**context, "findings": {**context["findings"], "rag": finding}}}


def route_to_tools(state: AgentState) -> str:
    """Only enter the tool-calling loop when the plan actually requires it."""
    return "agent" if "tools" in state["context"]["needed"] else "aggregate"


def call_model(state: AgentState) -> dict[str, Any]:
    """Manual tool-calling agent node (no deprecated react agent)."""
    model = get_chat_model(max_tool_calls=len(_ACTION_TOOLS)).bind_tools(_ACTION_TOOLS)
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def route_after_model(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "aggregate"


def aggregate(state: AgentState) -> dict[str, Any]:
    """Observability + synthesis: merge findings, log a structured summary."""
    context = state["context"]
    findings = context["findings"]
    tool_messages = [m for m in state["messages"] if getattr(m, "type", "") == "tool"]
    parts = [f"[{name}] {text}" for name, text in findings.items()]
    if tool_messages:
        parts.append(
            "[tools] " + " | ".join(str(m.content) for m in tool_messages)
        )
    answer = " || ".join(parts) if parts else "No subsystem had relevant knowledge."

    log = list(context.get("memory_log", []))
    log.append(f"Q: {context['query']} -> A: {answer}")

    logger.info(
        "brain summary: subsystems=%s tool_calls=%d",
        list(findings.keys()) + (["tools"] if tool_messages else []),
        len(tool_messages),
    )
    return {
        "messages": [AIMessage(content=answer)],
        "context": {**context, "memory_log": log, "tool_calls": len(tool_messages)},
    }


def build_graph():
    """Compile the mini DailyBot brain graph: routing + specialists + tools."""
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("memory_specialist", memory_specialist)
    graph.add_node("graph_specialist", graph_specialist)
    graph.add_node("rag_specialist", rag_specialist)
    graph.add_node("agent", call_model)
    graph.add_node("tools", _TOOL_NODE)
    graph.add_node("aggregate", aggregate)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "memory_specialist")
    graph.add_edge("memory_specialist", "graph_specialist")
    graph.add_edge("graph_specialist", "rag_specialist")
    graph.add_conditional_edges(
        "rag_specialist", route_to_tools, {"agent": "agent", "aggregate": "aggregate"}
    )
    graph.add_conditional_edges(
        "agent", route_after_model, {"tools": "tools", "aggregate": "aggregate"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("aggregate", END)
    return graph.compile()


REQUESTS: tuple[str, ...] = (
    "Tell me who leads engineering, look up the deploy policy, and create a "
    "task to follow up on the outage.",
    "What did I just ask you to do?",
)


def main() -> None:
    print("=== Mini DailyBot Brain: full offline run ===")
    app = build_graph()
    memory_log: list[str] = []
    for request in REQUESTS:
        result = app.invoke(
            {
                "messages": [HumanMessage(content=request)],
                "context": {"memory_log": memory_log},
            }
        )
        memory_log = result["context"]["memory_log"]
        needed = result["context"]["needed"]
        tool_calls = result["context"]["tool_calls"]
        answer = result["messages"][-1].content
        print(
            f"request={request!r} needed_subsystems={needed} "
            f"tool_calls={tool_calls} answer={answer!r}"
        )

    print(f"memory_log_entries={len(memory_log)}")
    print("=== TRACK9 MODULE 64: MINI DAILYBOT BRAIN COMPLETE ===")


if __name__ == "__main__":
    main()
