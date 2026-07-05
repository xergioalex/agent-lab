"""14 — Error Handling: retries with backoff, fallback, and a circuit breaker.

A ``flaky`` node fails ``N`` times (simulating a transient error) before
succeeding. A conditional edge retries it with a small exponential backoff
until either it succeeds or the attempt budget is exhausted, in which case a
circuit breaker trips and control routes to a ``fallback`` node instead of
raising. Every failure is logged — never swallowed silently.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Make `src.shared` importable when run as `python src/14_error_handling/error_handling.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

BACKOFF_BASE_SECONDS = 0.01


class TransientError(RuntimeError):
    """Raised by the flaky node to simulate a recoverable upstream failure."""


def flaky_node(state: AgentState) -> dict[str, object]:
    """A node that fails until ``attempts`` reaches ``succeed_at``.

    The failure is caught locally, logged, and recorded in state as an
    ``error`` — this is *not* swallowing the exception: it is deliberately
    converted into routable state so the graph's conditional edge can decide
    whether to retry, fall back, or proceed.
    """
    context = state.get("context", {})
    attempts = context.get("attempts", 0) + 1
    succeed_at = context["succeed_at"]
    backoff = BACKOFF_BASE_SECONDS * (2 ** (attempts - 1))
    time.sleep(backoff)

    try:
        if attempts < succeed_at:
            raise TransientError(f"upstream unavailable (attempt {attempts})")
    except TransientError as exc:
        logger.warning("flaky_node failed: %s (backoff=%.3fs)", exc, backoff)
        return {
            "context": {**context, "attempts": attempts, "error": str(exc)},
            "scratchpad": [f"attempt {attempts} failed: {exc}"],
        }

    logger.info("flaky_node succeeded on attempt %d", attempts)
    return {
        "context": {**context, "attempts": attempts, "error": None},
        "scratchpad": [f"attempt {attempts} succeeded"],
    }


def route_after_flaky(state: AgentState) -> str:
    """Retry on transient error, trip the circuit breaker past the budget."""
    context = state["context"]
    if context.get("error") is None:
        return "success"
    if context["attempts"] >= context["max_attempts"]:
        return "circuit_breaker"
    return "retry"


def finalize(state: AgentState) -> dict[str, object]:
    """Happy path: the flaky call eventually succeeded."""
    attempts = state["context"]["attempts"]
    message = AIMessage(content=f"succeeded after {attempts} attempt(s)")
    return {"messages": [message], "context": {**state["context"], "outcome": "success"}}


def fallback(state: AgentState) -> dict[str, object]:
    """Circuit breaker tripped: degrade gracefully instead of raising."""
    attempts = state["context"]["attempts"]
    logger.error("circuit breaker open after %d attempt(s); using fallback", attempts)
    message = AIMessage(content=f"circuit_open after {attempts} attempt(s), used fallback")
    return {
        "messages": [message],
        "context": {**state["context"], "outcome": "fallback", "circuit_open": True},
    }


def build_graph():
    """Compile the retry/backoff/circuit-breaker graph."""
    graph = StateGraph(AgentState)
    graph.add_node("flaky", flaky_node)
    graph.add_node("finalize", finalize)
    graph.add_node("fallback", fallback)

    graph.add_edge(START, "flaky")
    graph.add_conditional_edges(
        "flaky",
        route_after_flaky,
        {"retry": "flaky", "success": "finalize", "circuit_breaker": "fallback"},
    )
    graph.add_edge("finalize", END)
    graph.add_edge("fallback", END)
    return graph.compile()


def main() -> None:
    app = build_graph()

    # Scenario 1: recovers within budget.
    recovered = app.invoke({"context": {"attempts": 0, "succeed_at": 3, "max_attempts": 5}})
    print(
        f"scenario=recovers outcome={recovered['context']['outcome']} "
        f"attempts={recovered['context']['attempts']} "
        f"message={recovered['messages'][-1].content!r}"
    )

    # Scenario 2: never recovers in time -> circuit breaker trips -> fallback.
    tripped = app.invoke({"context": {"attempts": 0, "succeed_at": 10, "max_attempts": 2}})
    print(
        f"scenario=circuit_breaker outcome={tripped['context']['outcome']} "
        f"attempts={tripped['context']['attempts']} "
        f"message={tripped['messages'][-1].content!r}"
    )

    print("=== TRACK1 MODULE 14: ERROR HANDLING COMPLETE ===")


if __name__ == "__main__":
    main()
