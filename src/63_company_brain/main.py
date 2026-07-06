"""63 — Company Brain: memory + RAG + graph + cooperating specialist agents.

Capstone that integrates **Track 4** memory (module `06_memory_basics`),
**Track 5** RAG (`InMemoryVectorStore`), **Track 6** graph memory
(`InMemoryGraphStore`), and **Track 7** multi-agent cooperation
(module `09_multi_agent_systems`): a coordinator plans which knowledge
sources a request needs, then three specialist nodes — memory, graph, and
RAG — each inspect the shared plan and contribute a finding only when their
domain is relevant, before an aggregator merges everything into one answer.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/63_company_brain/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import (  # noqa: E402
    AgentState,
    InMemoryGraphStore,
    InMemoryVectorStore,
    get_logger,
)

logger = get_logger(__name__)

# -- knowledge sources -------------------------------------------------------

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
    store.upsert_node("alice", "Person", name="Alice")
    store.upsert_node("bob", "Person", name="Bob")
    store.upsert_node("carol", "Person", name="Carol")
    store.upsert_node("engineering", "Department", name="Engineering")
    store.add_relationship("alice", "REPORTS_TO", "bob")
    store.add_relationship("bob", "REPORTS_TO", "carol")
    store.add_relationship("engineering", "LED_BY", "carol")
    return store


_VECTOR_STORE = _build_vector_store()
_GRAPH_STORE = _build_graph_store()

_SPECIALIST_KEYWORDS: dict[str, tuple[str, ...]] = {
    "memory": ("earlier", "before", "remember", "previously"),
    "graph": ("manager", "reports", "alice", "team", "engineering"),
    "rag": ("policy", "vacation", "deploy"),
}


def _needed_specialists(text: str) -> list[str]:
    lowered = text.lower()
    return [
        name
        for name, keywords in _SPECIALIST_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]


def plan(state: AgentState) -> dict[str, Any]:
    """Coordinator: decide which specialists this request needs."""
    text = str(state["messages"][-1].content)
    needed = _needed_specialists(text)
    logger.info("planned specialists=%s", needed)
    return {
        "context": {
            **state.get("context", {}),
            "query": text,
            "needed": needed,
            "findings": {},
        }
    }


def memory_specialist(state: AgentState) -> dict[str, Any]:
    """Contribute a finding from session memory if the plan requires it."""
    context = state["context"]
    if "memory" not in context["needed"]:
        return {}
    log = context.get("memory_log", [])
    finding = "; ".join(log) if log else "no prior turns recorded yet"
    return {"context": {**context, "findings": {**context["findings"], "memory": finding}}}


def graph_specialist(state: AgentState) -> dict[str, Any]:
    """Contribute an org-chart finding via the dependency/report graph."""
    context = state["context"]
    if "graph" not in context["needed"]:
        return {}
    text = context["query"].lower()
    if "engineering" in text or "team" in text:
        lead = _GRAPH_STORE.neighbors("engineering", "LED_BY")
        finding = f"Engineering is led by {lead[0].properties['name']}" if lead else "unknown"
    else:
        manager = _GRAPH_STORE.neighbors("alice", "REPORTS_TO")
        finding = f"Alice reports to {manager[0].properties['name']}" if manager else "unknown"
    return {"context": {**context, "findings": {**context["findings"], "graph": finding}}}


def rag_specialist(state: AgentState) -> dict[str, Any]:
    """Contribute a policy finding via retrieval over the vector store."""
    context = state["context"]
    if "rag" not in context["needed"]:
        return {}
    hits = _VECTOR_STORE.similarity_search(context["query"], k=1)
    finding = hits[0].document.text if hits else "no matching policy found"
    return {"context": {**context, "findings": {**context["findings"], "rag": finding}}}


def aggregate(state: AgentState) -> dict[str, Any]:
    """Merge every specialist's contribution into one final answer."""
    context = state["context"]
    findings = context["findings"]
    if findings:
        answer = " | ".join(f"[{name}] {text}" for name, text in findings.items())
    else:
        answer = "No specialist had relevant knowledge for this request."
    log = list(context.get("memory_log", []))
    log.append(f"Q: {context['query']} -> A: {answer}")
    return {
        "messages": [AIMessage(content=answer)],
        "context": {**context, "memory_log": log},
    }


def build_graph():
    """Compile the company-brain coordinator + cooperating specialists graph."""
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("memory_specialist", memory_specialist)
    graph.add_node("graph_specialist", graph_specialist)
    graph.add_node("rag_specialist", rag_specialist)
    graph.add_node("aggregate", aggregate)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "memory_specialist")
    graph.add_edge("memory_specialist", "graph_specialist")
    graph.add_edge("graph_specialist", "rag_specialist")
    graph.add_edge("rag_specialist", "aggregate")
    graph.add_edge("aggregate", END)
    return graph.compile()


REQUESTS: tuple[str, ...] = (
    "Who is Alice's manager, and what is the vacation policy?",
    "Remind me what I asked before about Alice.",
)


def main() -> None:
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
        answer = result["messages"][-1].content
        print(f"request={request!r} needed={needed} answer={answer!r}")

    print(f"memory_log_entries={len(memory_log)}")
    print("=== TRACK9 MODULE 63: COMPANY BRAIN COMPLETE ===")


if __name__ == "__main__":
    main()
