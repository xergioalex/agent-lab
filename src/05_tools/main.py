"""05 — Tools: manual agent <-> ToolNode loop over DEMO_TOOLS.

Demonstrates binding tools to the model, executing them via ``ToolNode``, and
looping until the model returns a final text answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import DEMO_TOOLS, AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

_SLACK_ONLY = [t for t in DEMO_TOOLS if t.name == "send_slack"]
_MODEL = get_chat_model(
    responses=["Posted the update to the team channel."],
    max_tool_calls=1,
).bind_tools(_SLACK_ONLY)


def agent(state: AgentState) -> dict[str, object]:
    reply = _MODEL.invoke(state["messages"])
    return {"messages": [reply]}


def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "done"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(_SLACK_ONLY))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", route_after_agent, {"tools": "tools", "done": END})
    graph.add_edge("tools", "agent")
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke(
        {"messages": [HumanMessage(content="Send hello to the team on Slack.")]}
    )
    tool_msgs = [m.content for m in result["messages"] if getattr(m, "type", "") == "tool"]
    for observation in tool_msgs:
        print(observation)
    print(f"final={result['messages'][-1].content!r}")
    print("=== MODULE 05: TOOLS COMPLETE ===")


if __name__ == "__main__":
    main()
