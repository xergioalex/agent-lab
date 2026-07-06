"""22 — Planner Agent: turn a goal into a structured, ordered plan.

The planner calls ``get_chat_model().with_structured_output(Plan)`` so the
goal is normalized through a validated Pydantic schema (this is the same API
a real model uses for tool-argument extraction and structured answers). The
offline fake cannot truly reason about ordering, so a deterministic
keyword-to-tool matcher decomposes the goal into an ordered list of steps —
the same style of matching module 21 uses to pick a tool. The resulting plan
shape is explicitly validated before it is handed off (module 23 consumes
exactly this shape).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/22_planner_agent/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from src.shared import AgentState, DEMO_TOOLS, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

_TOOL_NAMES: tuple[str, ...] = tuple(tool.name for tool in DEMO_TOOLS)
_FALLBACK_STEP = "respond_directly"


class Plan(BaseModel):
    """Structured plan produced by ``with_structured_output`` — validated shape."""

    goal: str = Field(description="the goal, restated by the model")
    step_count: int = Field(default=1, description="how many steps the plan has")


def _derive_steps(goal: str) -> list[str]:
    """Deterministically decompose a goal into an ordered list of tool steps."""
    text = goal.lower()
    steps = [name for name in _TOOL_NAMES if any(tok in text for tok in name.split("_"))]
    return steps or [_FALLBACK_STEP]


def _validate_plan(steps: list[str]) -> None:
    """Fail loudly on an invalid plan shape — never trust an empty/unknown plan."""
    if not steps:
        raise ValueError("planner produced an empty plan")
    known = set(_TOOL_NAMES) | {_FALLBACK_STEP}
    unknown = [step for step in steps if step not in known]
    if unknown:
        raise ValueError(f"plan references unknown step(s): {unknown}")


def plan_node(state: AgentState) -> dict[str, object]:
    """Generate and validate a structured plan from the latest goal message."""
    goal = str(state["messages"][-1].content)
    planner = get_chat_model().with_structured_output(Plan)
    plan = planner.invoke(goal)
    if not isinstance(plan, Plan):
        raise TypeError(f"expected a Plan instance, got {type(plan)!r}")

    steps = _derive_steps(goal)
    _validate_plan(steps)
    logger.info("planned %d step(s) for goal=%r: %s", len(steps), plan.goal, steps)
    return {"context": {"goal": plan.goal, "steps": steps}}


def build_graph():
    """Compile the (single-node) goal -> plan graph."""
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", END)
    return graph.compile()


GOALS: tuple[str, ...] = (
    "Check the weather in Paris and send a slack summary to the team.",
    "Just say hello.",
)


def main() -> None:
    app = build_graph()
    for goal in GOALS:
        result = app.invoke({"messages": [HumanMessage(content=goal)]})
        context = result["context"]
        print(f"goal={context['goal']!r} steps={context['steps']}")

    print("=== TRACK3 MODULE 22: PLANNER AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
