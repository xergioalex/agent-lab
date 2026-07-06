"""23 — Executor Agent: run an ordered plan's steps against DEMO_TOOLS.

Takes the shape of plan module 22 produces (an ordered list of tool-name
steps) and executes each one in turn, collecting one result per step into
``AgentState.context``. A step whose name doesn't match a known tool, or
whose tool call raises, is handled gracefully — logged and recorded as a
degraded result — instead of crashing the run. An empty plan is handled the
same way: the loop never starts and ``finalize`` reports "no steps".
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/23_executor_agent/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, DEMO_TOOLS, get_logger  # noqa: E402

logger = get_logger(__name__)

_TOOLS_BY_NAME = {tool.name: tool for tool in DEMO_TOOLS}

# Canned arguments per tool so a step can run without an LLM in the loop.
_STEP_ARGS: dict[str, dict[str, object]] = {
    "get_weather": {"city": "Paris"},
    "search_knowledge_base": {"query": "standup"},
    "create_task": {"title": "Follow up with the team"},
    "add_numbers": {"a": 2, "b": 3},
    "send_slack": {"message": "Plan executed successfully."},
}


def execute_step(state: AgentState) -> dict[str, object]:
    """Run the plan's current step against its matching tool, recording the result."""
    context = state["context"]
    steps: list[str] = context["steps"]
    index: int = context.get("index", 0)
    step = steps[index]

    tool = _TOOLS_BY_NAME.get(step)
    if tool is None:
        logger.warning("no tool registered for step %r; skipping", step)
        outcome = f"skipped: no tool for step {step!r}"
    else:
        try:
            outcome = tool.invoke(_STEP_ARGS.get(step, {}))
        except Exception as exc:  # execution failure is routed, never swallowed
            logger.error("step %r failed: %s", step, exc)
            outcome = f"failed: {exc}"

    results = context.get("results", []) + [outcome]
    return {"context": {**context, "index": index + 1, "results": results}}


def route_initial(state: AgentState) -> str:
    """Skip straight to `finalize` when the plan has no steps at all."""
    context = state.get("context", {})
    return "execute_step" if context.get("steps") else "finalize"


def route_after_step(state: AgentState) -> str:
    """Keep looping while steps remain, otherwise finalize."""
    context = state["context"]
    return "execute_step" if context["index"] < len(context["steps"]) else "finalize"


def finalize(state: AgentState) -> dict[str, object]:
    """Summarize every step's result, or report an empty plan explicitly."""
    context = state["context"]
    results = context.get("results", [])
    if results:
        summary = f"executed {len(results)} step(s): {results}"
    else:
        summary = "no steps to execute"
    return {"context": {**context, "summary": summary}}


def build_graph():
    """Compile the plan -> step loop -> results graph."""
    graph = StateGraph(AgentState)
    graph.add_node("execute_step", execute_step)
    graph.add_node("finalize", finalize)
    graph.add_conditional_edges(
        START, route_initial, {"execute_step": "execute_step", "finalize": "finalize"}
    )
    graph.add_conditional_edges(
        "execute_step",
        route_after_step,
        {"execute_step": "execute_step", "finalize": "finalize"},
    )
    graph.add_edge("finalize", END)
    return graph.compile()


PLANS: tuple[list[str], ...] = (
    ["get_weather", "send_slack"],
    ["respond_directly"],  # no matching tool -> handled gracefully
    [],  # empty plan -> handled gracefully
)


def main() -> None:
    app = build_graph()
    for steps in PLANS:
        result = app.invoke({"context": {"steps": steps, "index": 0, "results": []}})
        print(f"steps={steps} summary={result['context']['summary']}")

    print("=== TRACK3 MODULE 23: EXECUTOR AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
