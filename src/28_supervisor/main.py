"""28 — Supervisor: one node orchestrates multiple worker agents.

``supervisor`` inspects the next pending task and delegates it to exactly one
worker (a small node dedicated to one kind of job); the worker runs, appends
its result, and control returns to the supervisor for the next task. Once
every task has been delegated, ``aggregate`` combines all worker results into
one final answer. This differs from module 25's router: there, one message
picks one sub-graph and the run ends; here, the supervisor repeats the
dispatch across a whole queue of turns before producing a single answer.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/28_supervisor/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, DEMO_TOOLS, get_logger  # noqa: E402

logger = get_logger(__name__)

_TOOLS_BY_NAME = {tool.name: tool for tool in DEMO_TOOLS}
_CITY_PATTERN = re.compile(r"at the (.+)$")

_WORKER_KEYWORDS: dict[str, tuple[str, ...]] = {
    "weather_worker": ("weather", "forecast"),
    "research_worker": ("standup", "vacation", "deploy", "oncall", "knowledge"),
    "task_worker": ("task", "todo", "remind"),
}
_WORKERS: tuple[str, ...] = (*_WORKER_KEYWORDS, "general_worker")


def supervisor(state: AgentState) -> dict[str, object]:
    """Pick the next pending task and decide which worker should handle it."""
    context = state["context"]
    tasks: list[str] = context["tasks"]
    index: int = context.get("index", 0)
    task = tasks[index]
    worker = next(
        (name for name, kws in _WORKER_KEYWORDS.items() if any(kw in task.lower() for kw in kws)),
        "general_worker",
    )
    logger.info("supervisor: turn %d task=%r -> %s", index, task, worker)
    return {"context": {**context, "current_task": task, "current_worker": worker}}


def route_to_worker(state: AgentState) -> str:
    """Conditional-edge router: dispatch to the worker the supervisor picked."""
    return state["context"]["current_worker"]


def _worker_node(name: str):
    """Build a worker node that runs one DEMO_TOOLS call (or acknowledges)."""

    def _node(state: AgentState) -> dict[str, object]:
        context = state["context"]
        task = context["current_task"]
        if name == "weather_worker":
            match = _CITY_PATTERN.search(task)
            city = match.group(1).rstrip("?.! ") if match else "your area"
            output = f"[{name}] {_TOOLS_BY_NAME['get_weather'].invoke({'city': city})}"
        elif name == "research_worker":
            output = f"[{name}] {_TOOLS_BY_NAME['search_knowledge_base'].invoke({'query': task})}"
        elif name == "task_worker":
            output = f"[{name}] {_TOOLS_BY_NAME['create_task'].invoke({'title': task})}"
        else:
            output = f"[{name}] acknowledged: {task}"

        results = context.get("worker_results", []) + [output]
        return {"context": {**context, "worker_results": results, "index": context.get("index", 0) + 1}}

    return _node


def route_after_worker(state: AgentState) -> str:
    """Return to the supervisor while tasks remain, else aggregate."""
    context = state["context"]
    return "supervisor" if context["index"] < len(context["tasks"]) else "aggregate"


def aggregate(state: AgentState) -> dict[str, object]:
    """Combine every worker's result into one final answer."""
    context = state["context"]
    results = context["worker_results"]
    summary = "; ".join(results)
    final = AIMessage(content=f"Aggregated {len(results)} worker result(s): {summary}")
    return {"messages": [final], "context": {**context, "summary": summary}}


def build_graph():
    """Compile the supervisor <-> workers topology with a final aggregation node."""
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor)
    for name in _WORKERS:
        graph.add_node(name, _worker_node(name))
    graph.add_node("aggregate", aggregate)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route_to_worker, {name: name for name in _WORKERS})
    for name in _WORKERS:
        graph.add_conditional_edges(
            name, route_after_worker, {"supervisor": "supervisor", "aggregate": "aggregate"}
        )
    graph.add_edge("aggregate", END)
    return graph.compile()


TASKS: tuple[str, ...] = (
    "What's the weather at the team offsite?",
    "Look up the vacation policy.",
    "Create a task to update the roadmap.",
    "Say thanks to the team.",
)


def main() -> None:
    app = build_graph()
    result = app.invoke({"context": {"tasks": list(TASKS), "index": 0, "worker_results": []}})

    for output in result["context"]["worker_results"]:
        print(output)
    print(f"final_answer={result['messages'][-1].content!r}")

    print("=== TRACK3 MODULE 28: SUPERVISOR COMPLETE ===")


if __name__ == "__main__":
    main()
