"""26 — Planning Loops: plan -> execute -> replan until done, with a hard cap.

Extends module 23's step loop with a ``replan`` phase: when a step fails (no
matching tool, or the tool raises), the agent doesn't just skip it — it
revises its remaining plan from the observed failure, injecting a diagnostic
step before continuing. A ``max_iterations`` guard bounds how many times the
agent is allowed to replan, so the loop always terminates even if steps keep
failing — abandoning whatever remains rather than looping forever.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/26_planning_loops/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, DEMO_TOOLS, get_logger  # noqa: E402

logger = get_logger(__name__)

_TOOLS_BY_NAME = {tool.name: tool for tool in DEMO_TOOLS}
_DIAGNOSTIC_STEP = "search_knowledge_base"

_STEP_ARGS: dict[str, dict[str, object]] = {
    "get_weather": {"city": "Paris"},
    "search_knowledge_base": {"query": "deploy"},
    "create_task": {"title": "Investigate failed step"},
    "add_numbers": {"a": 2, "b": 3},
    "send_slack": {"message": "Plan finished."},
}


def plan(state: AgentState) -> dict[str, object]:
    """Initial planning phase: fall back to a safe default if given no steps."""
    context = state["context"]
    remaining = context.get("remaining") or ["respond_directly"]
    logger.info("initial plan: %s", remaining)
    return {"context": {**context, "remaining": remaining}}


def _run_step(step: str) -> tuple[str, bool]:
    """Execute one step; return (outcome, succeeded)."""
    tool = _TOOLS_BY_NAME.get(step)
    if tool is None:
        return f"skipped: no tool for step {step!r}", False
    try:
        return tool.invoke(_STEP_ARGS.get(step, {})), True
    except Exception as exc:  # execution failure is routed, never swallowed
        logger.error("step %r failed: %s", step, exc)
        return f"failed: {exc}", False


def execute_step(state: AgentState) -> dict[str, object]:
    """Pop and run the next step, recording whether it needs a replan."""
    context = state["context"]
    remaining = list(context["remaining"])
    step = remaining.pop(0)
    outcome, succeeded = _run_step(step)
    completed = context.get("completed", []) + [(step, outcome)]
    logger.info("executed %r -> %s (succeeded=%s)", step, outcome, succeeded)
    return {
        "context": {
            **context,
            "remaining": remaining,
            "completed": completed,
            "needs_replan": not succeeded,
        }
    }


def route_after_execute(state: AgentState) -> str:
    """Finalize on completion or cap; otherwise replan on failure, else continue."""
    context = state["context"]
    if not context["remaining"]:
        return "finalize"
    if context["iteration"] >= context["max_iterations"]:
        return "finalize"
    return "replan" if context["needs_replan"] else "execute_step"


def replan(state: AgentState) -> dict[str, object]:
    """Revise the remaining plan from the last observed failure."""
    context = state["context"]
    iteration = context["iteration"] + 1
    remaining = list(context["remaining"])
    if _DIAGNOSTIC_STEP not in remaining:
        remaining.insert(0, _DIAGNOSTIC_STEP)
    logger.info("replan #%d: remaining=%s", iteration, remaining)
    return {"context": {**context, "remaining": remaining, "iteration": iteration, "needs_replan": False}}


def finalize(state: AgentState) -> dict[str, object]:
    """Report a completed plan, or an iteration-capped, partially abandoned one."""
    context = state["context"]
    remaining = context["remaining"]
    completed = context["completed"]
    if remaining:
        summary = (
            f"iteration cap reached ({context['iteration']}), "
            f"{len(remaining)} step(s) abandoned: {remaining}"
        )
    else:
        summary = f"plan completed after {context['iteration']} replan(s), {len(completed)} step(s) executed"
    return {"context": {**context, "summary": summary}}


def build_graph():
    """Compile the plan -> execute -> replan loop with its termination guard."""
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("execute_step", execute_step)
    graph.add_node("replan", replan)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "execute_step")
    graph.add_conditional_edges(
        "execute_step",
        route_after_execute,
        {"execute_step": "execute_step", "replan": "replan", "finalize": "finalize"},
    )
    graph.add_edge("replan", "execute_step")
    graph.add_edge("finalize", END)
    return graph.compile()


SCENARIOS: tuple[dict[str, object], ...] = (
    {"remaining": ["get_weather", "verify_deployment", "send_slack"], "max_iterations": 3},
    {
        "remaining": ["nonexistent_a", "nonexistent_b", "nonexistent_c", "nonexistent_d"],
        "max_iterations": 2,
    },
)


def main() -> None:
    app = build_graph()
    for scenario in SCENARIOS:
        initial_remaining = scenario["remaining"]
        result = app.invoke(
            {
                "context": {
                    **scenario,
                    "completed": [],
                    "iteration": 0,
                    "needs_replan": False,
                }
            }
        )
        print(f"remaining_initial={initial_remaining} summary={result['context']['summary']}")

    print("=== TRACK3 MODULE 26: PLANNING LOOPS COMPLETE ===")


if __name__ == "__main__":
    main()
