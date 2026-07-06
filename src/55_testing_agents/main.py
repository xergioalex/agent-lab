"""55 — Testing Agents: fakes, snapshotting, and structural assertions.

LLM-backed agents are nondeterministic in production (temperature, model
upgrades, prompt drift), which makes exact-text assertions ("the reply is
literally 'X'") brittle. This module demonstrates the three patterns that
make agent testing reliable instead:

1. **Fakes/stubs** — swap the real model for `FakeToolCallingModel` (via
   `get_chat_model`) so tool-calling behaviour is deterministic and offline.
2. **Snapshotting** — capture a normalized *shape* of the output (roles,
   tool-call names, message count) rather than the raw text, so the
   snapshot is stable across runs and comparable over time.
3. **Structural assertions** — assert invariants ("the last message is an
   AIMessage", "no tool call is missing an id") instead of exact strings.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/55_testing_agents/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import DEMO_TOOLS, AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

MAX_TOOL_CALLS = 2


def build_graph():
    """The system under test: the same manual tool-call loop as module 17."""
    model = get_chat_model(
        responses=["Done: fetched the weather and posted it to Slack."],
        max_tool_calls=MAX_TOOL_CALLS,
    ).bind_tools(DEMO_TOOLS)

    def agent(state: AgentState) -> dict[str, Any]:
        reply = model.invoke(state["messages"])
        return {"messages": [reply]}

    def has_pending_tool_calls(state: AgentState) -> str:
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return "end"

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(DEMO_TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", has_pending_tool_calls, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()


# --------------------------------------------------------------------------- #
# Testing pattern 1: snapshotting — normalize the shape, not the raw text.
# --------------------------------------------------------------------------- #


def snapshot(result: AgentState) -> dict[str, Any]:
    """Reduce a run's output to a stable, comparable shape.

    Deliberately excludes anything nondeterministic across runs/versions
    (message ids, timestamps, exact tool-call ids) and keeps only structural
    facts: how many messages, which roles, which tools were called, and the
    role of the final message.
    """
    messages = result.get("messages", [])
    roles = [type(m).__name__ for m in messages]
    tool_calls = [
        tc["name"]
        for m in messages
        if isinstance(m, AIMessage)
        for tc in (m.tool_calls or [])
    ]
    return {
        "num_messages": len(messages),
        "roles": roles,
        "tool_calls": tool_calls,
        "final_role": roles[-1] if roles else None,
    }


# --------------------------------------------------------------------------- #
# Testing pattern 2: structural assertions — invariants, not exact strings.
# --------------------------------------------------------------------------- #


def structural_checks(result: AgentState) -> list[tuple[str, bool]]:
    """Assert invariants on the *shape* of a run rather than its exact text."""
    messages = result.get("messages", [])
    checks: list[tuple[str, bool]] = []

    checks.append(("has_at_least_one_message", len(messages) > 0))
    checks.append(
        ("final_message_is_ai_message", bool(messages) and isinstance(messages[-1], AIMessage))
    )
    checks.append(
        (
            "final_message_has_no_pending_tool_calls",
            bool(messages)
            and isinstance(messages[-1], AIMessage)
            and not messages[-1].tool_calls,
        )
    )
    checks.append(
        (
            "every_tool_call_has_an_id",
            all(
                tc.get("id") is not None
                for m in messages
                if isinstance(m, AIMessage)
                for tc in (m.tool_calls or [])
            ),
        )
    )
    checks.append(("tool_call_count_within_budget", len(snapshot(result)["tool_calls"]) <= MAX_TOOL_CALLS))
    return checks


def main() -> None:
    app = build_graph()
    query = "What's the weather in Paris? Then send it to Slack."

    # Two independent invocations of the same input — with a real LLM this
    # could vary; with the offline fake it is reproducible by design.
    result_a = app.invoke({"messages": [HumanMessage(content=query)]})
    result_b = app.invoke({"messages": [HumanMessage(content=query)]})

    snapshot_a = snapshot(result_a)
    snapshot_b = snapshot(result_b)
    snapshots_match = snapshot_a == snapshot_b

    print(f"snapshot_a={snapshot_a}")
    print(f"snapshot_b={snapshot_b}")
    print(f"snapshots_stable_across_runs={snapshots_match}")
    if not snapshots_match:
        raise AssertionError("snapshot mismatch across identical runs — nondeterminism leaked in")

    checks = structural_checks(result_a)
    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        all_passed = all_passed and passed
    if not all_passed:
        raise AssertionError("one or more structural checks failed")

    logger.info("all structural checks passed; snapshots stable across runs")
    print("=== MODULE 55: TESTING AGENTS COMPLETE ===")


if __name__ == "__main__":
    main()
