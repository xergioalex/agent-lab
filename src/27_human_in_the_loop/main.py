"""27 — Human-in-the-Loop: pause on interrupt(), resume with Command.

``propose_action`` calls ``interrupt(payload)`` to pause the graph mid-run and
surface a proposed action for approval. ``MemorySaver`` checkpoints the run
per ``thread_id`` so it can be resumed later — even from a different process.
This module drives the interrupt -> resume cycle entirely in code (no real
stdin): each scenario invokes once to trigger the pause, reads the proposal
off ``result["__interrupt__"]``, then resumes with ``Command(resume=...)``
carrying an approve / edit / reject decision.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/27_human_in_the_loop/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.types import Command, interrupt  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)


def propose_action(state: AgentState) -> dict[str, object]:
    """Propose a side-effecting action, then pause until a human decides."""
    context = state.get("context", {})
    action = f"send_slack: notify #team about '{context.get('title', 'the release')}'"
    decision = interrupt({"proposed_action": action})
    logger.info("resumed with decision=%r", decision)
    return {"context": {**context, "action": action, "decision": decision}}


def apply_decision(state: AgentState) -> dict[str, object]:
    """Act on the human decision: approve, edit, or reject the proposed action."""
    context = state["context"]
    decision = context["decision"]
    verdict = decision.get("verdict")
    if verdict == "approve":
        outcome = f"executed: {context['action']}"
    elif verdict == "edit":
        outcome = f"executed (edited): {decision['edited_action']}"
    else:
        outcome = "rejected: no action taken"
    logger.info("apply_decision: %s", outcome)
    return {"messages": [AIMessage(content=outcome)], "context": {**context, "outcome": outcome}}


def build_graph():
    """Compile the propose -> (pause) -> apply_decision graph with a checkpointer."""
    graph = StateGraph(AgentState)
    graph.add_node("propose_action", propose_action)
    graph.add_node("apply_decision", apply_decision)
    graph.add_edge(START, "propose_action")
    graph.add_edge("propose_action", "apply_decision")
    graph.add_edge("apply_decision", END)
    return graph.compile(checkpointer=MemorySaver())


def run_scenario(app: Any, thread_id: str, title: str, decision: dict[str, object]) -> str:
    """Drive one interrupt -> resume cycle programmatically (no real stdin)."""
    config = {"configurable": {"thread_id": thread_id}}

    paused = app.invoke({"context": {"title": title}}, config=config)
    if "__interrupt__" not in paused:
        raise RuntimeError("expected the graph to pause at interrupt()")
    proposed = paused["__interrupt__"][0].value["proposed_action"]
    print(f"thread={thread_id} paused_on={proposed!r}")

    resumed = app.invoke(Command(resume=decision), config=config)
    outcome = resumed["context"]["outcome"]
    print(f"thread={thread_id} outcome={outcome!r}")
    return outcome


def main() -> None:
    app = build_graph()
    run_scenario(app, "release-1", "v2.0 release", {"verdict": "approve"})
    run_scenario(
        app,
        "release-2",
        "v2.1 release",
        {"verdict": "edit", "edited_action": "send_slack: notify #leads only"},
    )
    run_scenario(app, "release-3", "v2.2 release", {"verdict": "reject"})

    print("=== TRACK3 MODULE 27: HUMAN IN THE LOOP COMPLETE ===")


if __name__ == "__main__":
    main()
