"""12 — Parallel Execution: fan-out/fan-in with the Send API and a reducer.

A dispatcher fans a list of documents out to parallel ``worker`` invocations
via ``Send``. Each worker runs in its own super-step and contributes a partial
update to the shared ``scratchpad`` list, which is safe only because the
state field is annotated with the ``operator.add`` reducer (list
concatenation instead of last-write-wins overwrite). An ``aggregate`` node
then fans back in and reduces the collected results into a single message.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/12_parallel_execution/parallel.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.types import Send  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

DOCUMENTS: tuple[str, ...] = (
    "LangGraph models agents as state machines.",
    "Reducers merge concurrent partial updates safely.",
    "Send fans work out across a super-step.",
    "Fan-in aggregation reduces parallel results.",
)


def dispatch(state: AgentState) -> list[Send]:
    """Fan-out: one ``Send`` per document, each carrying its own input.

    ``Send(node, arg)`` schedules ``node`` with ``arg`` as its *entire* input
    for that invocation — this is what makes the fan-out parallel: each
    worker task is independent and can be scheduled within the same
    super-step.
    """
    documents = state.get("context", {}).get("documents", ())
    return [Send("worker", {"context": {"document": doc}}) for doc in documents]


def worker(state: AgentState) -> dict[str, object]:
    """Process a single document. Runs once per ``Send`` — potentially in parallel."""
    document = state["context"]["document"]
    word_count = len(document.split())
    logger.info("worker processed %d-word document", word_count)
    # Returning a list here relies on the operator.add reducer on `scratchpad`
    # to concatenate results from every parallel worker instead of one
    # worker's write clobbering another's.
    return {"scratchpad": [f"{word_count} words: {document!r}"]}


def aggregate(state: AgentState) -> dict[str, object]:
    """Fan-in: reduce every worker's contribution into one summary message."""
    notes = state.get("scratchpad", [])
    total_words = sum(int(note.split(" words:", 1)[0]) for note in notes)
    summary = AIMessage(
        content=f"Processed {len(notes)} documents, total_words={total_words}"
    )
    return {"messages": [summary], "context": {**state.get("context", {}), "total_words": total_words}}


def build_graph():
    """Compile the fan-out/fan-in graph: START -(Send)-> worker* -> aggregate -> END."""
    graph = StateGraph(AgentState)
    graph.add_node("worker", worker)
    graph.add_node("aggregate", aggregate)
    graph.add_conditional_edges(START, dispatch, ["worker"])
    graph.add_edge("worker", "aggregate")
    graph.add_edge("aggregate", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({"context": {"documents": list(DOCUMENTS)}})

    for note in result["scratchpad"]:
        print(f"worker result: {note}")
    print(f"total_words={result['context']['total_words']}")
    print(f"summary: {result['messages'][-1].content}")

    print("=== TRACK1 MODULE 12: PARALLEL EXECUTION COMPLETE ===")


if __name__ == "__main__":
    main()
