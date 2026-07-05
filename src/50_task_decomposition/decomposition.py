"""50 — Task Decomposition: decompose a goal, fan out subtasks, reduce results.

A ``decompose`` router splits a goal into independent subtasks and fans them
out via ``Send`` — one worker invocation per subtask, scheduled within the
same super-step (see module 12 for the fan-out/fan-in mechanics this reuses).
Each worker only sees its own subtask; a ``reduce`` node gathers every
worker's contribution (accumulated through the reducer-backed ``scratchpad``)
into one final answer. This is the classic map/assign/reduce shape applied to
goal decomposition instead of document batches.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/50_task_decomposition/decomposition.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.types import Send  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

# Static goal -> subtasks mapping standing in for an LLM-driven planner — kept
# deterministic and offline while modeling a realistic decomposition step.
DECOMPOSITION: dict[str, tuple[str, ...]] = {
    "Ship the multi-agent module": ("design", "implement", "test", "document"),
    "Launch the negotiation demo": ("draft-proposal", "review-terms", "finalize-deal"),
}

GOALS: tuple[str, ...] = tuple(DECOMPOSITION)


def decompose(state: AgentState) -> list[Send]:
    """Fan-out: one ``Send`` per subtask, each carrying only its own input.

    Because each ``Send`` sets the *entire* input for that worker invocation,
    a worker never sees another worker's subtask — the coordinator (this
    router) is the only place that knows the full assignment.
    """
    goal = state["context"]["goal"]
    subtasks = DECOMPOSITION[goal]
    logger.info("decomposed goal %r into %d subtask(s)", goal, len(subtasks))
    return [
        Send("worker", {"context": {"goal": goal, "subtask": subtask}})
        for subtask in subtasks
    ]


def worker(state: AgentState) -> dict[str, Any]:
    """Complete a single subtask. Runs once per ``Send`` — potentially in parallel."""
    context = state["context"]
    subtask, goal = context["subtask"], context["goal"]
    note = f"[{subtask}] completed for goal '{goal}'"
    logger.info(note)
    # Relies on the `operator.add` reducer on `scratchpad` to concatenate
    # every worker's contribution instead of one worker's write clobbering
    # another's — the same fan-in safety net used in module 12.
    return {"scratchpad": [note]}


def reduce(state: AgentState) -> dict[str, Any]:
    """Fan-in: gather every worker's contribution into one final answer.

    Sorted so the printed order — and therefore the smoke test — is stable
    regardless of the order in which parallel workers complete.
    """
    goal = state["context"]["goal"]
    notes = sorted(state.get("scratchpad", []))
    summary = AIMessage(
        content=f"Goal '{goal}' complete via {len(notes)} subtask(s): " + " | ".join(notes)
    )
    return {
        "messages": [summary],
        "context": {**state.get("context", {}), "subtask_count": len(notes)},
    }


def build_graph():
    """Compile the decompose(Send*) -> worker* -> reduce graph."""
    graph = StateGraph(AgentState)
    graph.add_node("worker", worker)
    graph.add_node("reduce", reduce)
    graph.add_conditional_edges(START, decompose, ["worker"])
    graph.add_edge("worker", "reduce")
    graph.add_edge("reduce", END)
    return graph.compile()


def main() -> None:
    app = build_graph()

    for goal in GOALS:
        result = app.invoke({"context": {"goal": goal}})
        for note in sorted(result["scratchpad"]):
            print(f"worker result: {note}")
        print(f"subtask_count={result['context']['subtask_count']}")
        print(f"summary: {result['messages'][-1].content}")

    print("=== TRACK7 MODULE 50: TASK DECOMPOSITION COMPLETE ===")


if __name__ == "__main__":
    main()
