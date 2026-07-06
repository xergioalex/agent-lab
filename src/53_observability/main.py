"""53 — Observability: structured logging, run metrics, and a run tree.

Demonstrates instrumenting a small LangGraph agent so every run produces:

- structured log lines via ``get_logger`` (one per node enter/exit)
- per-run metrics: wall-clock latency, node count, and an estimated token count
- a readable **run tree** showing the execution path taken through the graph

This is the offline foundation real tracing tools (LangSmith, OpenTelemetry)
build on: capture start/stop + metadata around each unit of work, then render
it. Nothing here requires a key or a service.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/53_observability/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)


def estimate_tokens(text: str) -> int:
    """Cheap, deterministic token estimate: ~4 characters per token."""
    return max(1, len(text) // 4)


@dataclass
class RunSpan:
    """A single instrumented node execution — one entry in the run tree."""

    name: str
    duration_ms: float
    tokens_est: int


@dataclass
class RunTree:
    """Ordered collection of spans produced by one graph invocation."""

    spans: list[RunSpan] = field(default_factory=list)

    def record(self, span: RunSpan) -> None:
        self.spans.append(span)

    @property
    def total_latency_ms(self) -> float:
        return sum(span.duration_ms for span in self.spans)

    @property
    def total_tokens_est(self) -> int:
        return sum(span.tokens_est for span in self.spans)

    def render(self) -> str:
        """Render the run tree as an indented, human-readable trace."""
        lines: list[str] = []
        for depth, span in enumerate(self.spans):
            indent = "    " * depth
            prefix = "└── " if depth > 0 else ""
            lines.append(
                f"{indent}{prefix}{span.name} "
                f"({span.duration_ms:.2f}ms, ~{span.tokens_est} tokens)"
            )
        return "\n".join(lines)


def traced_node(
    run_tree: RunTree, name: str
) -> Callable[[Callable[[AgentState], dict[str, Any]]], Callable[[AgentState], dict[str, Any]]]:
    """Decorator factory: wrap a node function with timing + logging + a run-tree span."""

    def decorator(
        fn: Callable[[AgentState], dict[str, Any]],
    ) -> Callable[[AgentState], dict[str, Any]]:
        def wrapped(state: AgentState) -> dict[str, Any]:
            logger.info("node %r: enter", name)
            started = time.perf_counter()
            try:
                result = fn(state)
            except Exception:
                logger.exception("node %r: raised an exception", name)
                raise
            duration_ms = (time.perf_counter() - started) * 1000
            text = "".join(str(v) for v in result.values())
            tokens = estimate_tokens(text)
            run_tree.record(RunSpan(name=name, duration_ms=duration_ms, tokens_est=tokens))
            logger.info("node %r: exit (%.2fms, ~%d tokens)", name, duration_ms, tokens)
            return result

        return wrapped

    return decorator


def plan(state: AgentState) -> dict[str, Any]:
    """Draft a one-line plan from the latest human message."""
    messages = state.get("messages", [])
    query = str(messages[-1].content) if messages else ""
    return {"scratchpad": [f"plan: answer '{query}' using the knowledge base"]}


def retrieve(state: AgentState) -> dict[str, Any]:
    """Simulate a retrieval step (deterministic, no vector store needed)."""
    return {"scratchpad": ["retrieve: found 1 relevant snippet"]}


def respond(state: AgentState, model: Any) -> dict[str, Any]:
    """Produce the final answer via the shared chat-model factory."""
    messages = state.get("messages", [])
    reply = model.invoke(messages)
    return {"messages": [reply]}


def build_graph(run_tree: RunTree):
    """Compile a 3-node graph with every node instrumented for observability."""
    model = get_chat_model(responses=["Standups are at 9:30am in #team."])

    graph = StateGraph(AgentState)
    graph.add_node("plan", traced_node(run_tree, "plan")(plan))
    graph.add_node("retrieve", traced_node(run_tree, "retrieve")(retrieve))
    graph.add_node(
        "respond", traced_node(run_tree, "respond")(lambda s: respond(s, model))
    )
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "retrieve")
    graph.add_edge("retrieve", "respond")
    graph.add_edge("respond", END)
    return graph.compile()


def main() -> None:
    run_tree = RunTree()
    app = build_graph(run_tree)

    query = "When is the daily standup?"
    result = app.invoke({"messages": [HumanMessage(content=query)]})
    answer = result["messages"][-1].content
    assert isinstance(result["messages"][-1], AIMessage)

    print(f"query={query!r} answer={answer!r}")
    print("run-tree:")
    print(run_tree.render())
    print(
        f"metrics: nodes={len(run_tree.spans)} "
        f"total_latency_ms={run_tree.total_latency_ms:.2f} "
        f"tokens_est={run_tree.total_tokens_est}"
    )
    print("=== MODULE 53: OBSERVABILITY COMPLETE ===")


if __name__ == "__main__":
    main()
