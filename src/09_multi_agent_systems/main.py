"""09 — Multi-Agent Systems: planner -> executor -> critic with replan loop.

The critic can send the run back to the planner when quality checks fail,
demonstrating cooperative roles sharing one graph state.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


class TeamState(TypedDict, total=False):
    plan: list[str]
    result: str | None
    verdict: str | None
    attempts: int


def planner(state: TeamState) -> dict[str, object]:
    attempts = state.get("attempts", 0)
    if attempts == 0:
        plan = ["gather_logs", "identify_root_cause", "draft_fix"]
    else:
        plan = ["gather_logs", "identify_root_cause", "draft_fix", "add_tests"]
    logger.info("planner: plan=%s attempt=%d", plan, attempts)
    return {"plan": plan, "result": None, "verdict": None}


def executor(state: TeamState) -> dict[str, object]:
    executed = ", ".join(state["plan"])
    result = f"done: executed [{executed}]"
    logger.info("executor: %s", result)
    return {"result": result}


def critic(state: TeamState) -> dict[str, object]:
    attempts = state.get("attempts", 0)
    needs_tests = attempts == 0 and "add_tests" not in state.get("plan", [])
    verdict = "revise" if needs_tests else "approve"
    logger.info("critic: verdict=%s", verdict)
    return {"verdict": verdict, "attempts": attempts + 1}


def route_after_critic(state: TeamState) -> str:
    return "planner" if state.get("verdict") == "revise" else "finish"


def finish(state: TeamState) -> dict[str, object]:
    return {}


def build_graph():
    graph = StateGraph(TeamState)
    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("critic", critic)
    graph.add_node("finish", finish)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "critic")
    graph.add_conditional_edges(
        "critic", route_after_critic, {"planner": "planner", "finish": "finish"}
    )
    graph.add_edge("finish", END)
    return graph.compile()


def main() -> None:
    result = build_graph().invoke({"attempts": 0})
    print(f"result={result['result']!r} verdict={result['verdict']} attempts={result['attempts']}")
    print("=== MODULE 09: MULTI-AGENT SYSTEMS COMPLETE ===")


if __name__ == "__main__":
    main()
