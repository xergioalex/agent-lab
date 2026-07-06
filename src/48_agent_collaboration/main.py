"""48 — Agent Collaboration: two specialist agents cooperating on shared state.

A ``researcher`` agent gathers findings for a topic and a ``writer`` agent
drafts a short brief from those findings; a ``converge`` node combines both
contributions into one final message. Both agents read and write the shared
``AgentState``:

- ``scratchpad`` is reducer-backed (``operator.add``), so every agent may
  append its own log line without clobbering the others' entries.
- ``context`` is a plain dict with **no reducer** — a node's returned
  ``context`` value *replaces* the whole field. Each agent therefore spreads
  the previous context (``**state.get("context", {})``) before adding its own
  namespaced key, which is what keeps the two agents' writes disjoint instead
  of one silently erasing the other's.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/48_agent_collaboration/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

# A small canned knowledge base standing in for a real research step — keeps
# the module deterministic and offline while modeling a realistic hand-off.
_FINDINGS: dict[str, str] = {
    "reducers": "Reducers merge concurrent partial state updates deterministically.",
    "fan-out": "Send() schedules multiple node invocations within one super-step.",
    "blackboard": "A blackboard is a shared store agents read and post facts to.",
}

TOPICS: tuple[str, ...] = ("reducers", "fan-out", "blackboard")


def researcher(state: AgentState) -> dict[str, Any]:
    """Gather a finding for the current topic and post it under its own key."""
    context = state.get("context", {})
    topic = context["topic"]
    finding = _FINDINGS.get(topic, "No data found.")
    note = f"[researcher] found: {finding}"
    logger.info(note)
    return {
        # Spreading the previous context preserves `topic` for the writer.
        "context": {**context, "research": finding},
        "scratchpad": [note],
    }


def writer(state: AgentState) -> dict[str, Any]:
    """Draft a one-line brief from the researcher's finding, in its own key."""
    context = state.get("context", {})
    research = context["research"]
    draft = f"Brief: {research}"
    note = f"[writer] drafted: {draft}"
    logger.info(note)
    return {
        "context": {**context, "draft": draft},
        "scratchpad": [note],
    }


def converge(state: AgentState) -> dict[str, Any]:
    """Combine both agents' disjoint contributions into one final message."""
    context = state.get("context", {})
    topic = context["topic"]
    draft = context["draft"]
    message = AIMessage(content=f"Final brief for '{topic}': {draft}")
    return {"messages": [message]}


def build_graph():
    """Compile the sequential researcher -> writer -> converge cooperation loop."""
    graph = StateGraph(AgentState)
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("converge", converge)

    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "converge")
    graph.add_edge("converge", END)
    return graph.compile()


def demonstrate_context_conflict(context: dict[str, Any]) -> None:
    """Show what happens when a node forgets to spread the previous context.

    ``context`` has no reducer, so returning ``{"context": {...}}`` from a node
    *replaces* the whole field instead of merging into it. A "naive" writer
    that skips the spread silently drops every key the researcher wrote.
    """
    naive_update = {"draft": "an unmerged draft"}  # bug: no `**context` spread
    dropped = sorted(set(context) - set(naive_update))
    print(f"anti-pattern demo: naive writer would drop keys {dropped}")


def main() -> None:
    app = build_graph()

    demonstrate_context_conflict({"topic": "reducers", "research": "..."})

    for topic in TOPICS:
        result = app.invoke({"context": {"topic": topic}})
        for note in result["scratchpad"]:
            print(note)
        reply = result["messages"][-1].content
        print(f"topic={topic!r} result={reply!r}")

    print("=== TRACK7 MODULE 48: AGENT COLLABORATION COMPLETE ===")


if __name__ == "__main__":
    main()
