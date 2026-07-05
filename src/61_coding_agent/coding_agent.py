"""61 — Coding Agent: a manual tool-calling loop for code assistance.

Capstone that deepens **Track 3** (tool use, module `05_tools`): given a task,
the agent iterates over code-oriented tools (`read_file`, `run_tests`,
`apply_patch`) via a manual `ToolNode` loop (`add_conditional_edges`, not the
deprecated `create_react_agent`) until it has enough observations to report a
fix.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/61_coding_agent/coding_agent.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

# A toy, in-memory "repository" so the tools stay offline and deterministic.
_REPO_FILE = "calculator.py"
_BUGGY_SOURCE = "def add(a, b):\n    return a - b  # bug: should be a + b"


@tool
def read_file(path: str) -> str:
    """Read the contents of a file in the toy repository."""
    return _BUGGY_SOURCE


@tool
def run_tests(path: str) -> str:
    """Run the test suite for a file and report pass/fail results."""
    return "FAILED test_calculator.py::test_add - assert (1 - 2) == -1, expected 3"


@tool
def apply_patch(patch: str) -> str:
    """Apply a unified-diff style patch to fix the reported bug."""
    return "Patch applied: add() now returns a + b; re-run tests to confirm."


CODE_TOOLS = [read_file, run_tests, apply_patch]
_TOOL_NODE = ToolNode(CODE_TOOLS)


def call_model(state: AgentState) -> dict[str, Any]:
    """Agent node: pick the next code tool (or stop) given the transcript so far."""
    model = get_chat_model(max_tool_calls=len(CODE_TOOLS)).bind_tools(CODE_TOOLS)
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def route_after_model(state: AgentState) -> str:
    """Keep looping through tools while the agent keeps requesting them."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "finalize"


def finalize(state: AgentState) -> dict[str, Any]:
    """Summarize the tool trace into a scratchpad entry."""
    steps = [
        f"{m.name}: {m.content}"
        for m in state["messages"]
        if isinstance(m, ToolMessage)
    ]
    return {"scratchpad": steps}


def build_graph():
    """Compile the coding-agent manual tool loop."""
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", _TOOL_NODE)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", route_after_model, {"tools": "tools", "finalize": "finalize"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("finalize", END)
    return graph.compile()


TASK = (
    f"Please read {_REPO_FILE}, run the tests, and apply a patch to fix the "
    "add function."
)


def main() -> None:
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content=TASK)]})

    print(f"task={TASK!r}")
    for step in result["scratchpad"]:
        print(f"step: {step}")
    final_answer = result["messages"][-1].content
    print(f"final_answer={final_answer!r}")
    print(f"tool_calls_made={len(result['scratchpad'])}")
    print("=== TRACK9 MODULE 61: CODING AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
