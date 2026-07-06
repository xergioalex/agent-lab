"""17 — Function Calling: bind_tools + a manual tool-call loop.

``langgraph.prebuilt.create_react_agent`` is deprecated (and uninstalled in
this environment): production agents build the loop themselves with
``ToolNode`` and a conditional edge, which is exactly what this module does.
``model.bind_tools(DEMO_TOOLS)`` lets the (offline) model emit real tool
calls; the graph routes back to the model whenever tool calls remain and
finishes once the model returns a plain text answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/17_function_calling/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import DEMO_TOOLS, AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

MAX_TOOL_CALLS = 2


def build_graph():
    """Compile a manual tool-call loop: agent <-> tools until no calls remain.

    This is the pattern `create_react_agent` used to hide — spelled out so
    it's clear what actually happens on every turn.
    """
    model = get_chat_model(
        responses=["Done: fetched the weather and posted it to Slack."],
        max_tool_calls=MAX_TOOL_CALLS,
    ).bind_tools(DEMO_TOOLS)

    def agent(state: AgentState) -> dict[str, object]:
        reply = model.invoke(state["messages"])
        logger.info("agent reply: tool_calls=%s content=%r", reply.tool_calls, reply.content)
        return {"messages": [reply]}

    def has_pending_tool_calls(state: AgentState) -> str:
        """Conditional edge: keep looping through `tools` while calls remain."""
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


def main() -> None:
    app = build_graph()
    result = app.invoke(
        {"messages": [HumanMessage(content="What's the weather in Paris? Then send it to Slack.")]}
    )

    tool_calls_seen = [
        tc["name"]
        for m in result["messages"]
        if isinstance(m, AIMessage)
        for tc in (m.tool_calls or [])
    ]
    final_reply = result["messages"][-1].content

    print(f"tool_calls={tool_calls_seen}")
    print(f"messages_in_transcript={len(result['messages'])}")
    print(f"final_reply={final_reply!r}")
    print("=== TRACK2 MODULE 17: FUNCTION CALLING COMPLETE ===")


if __name__ == "__main__":
    main()
