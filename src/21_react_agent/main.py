"""21 — ReAct Agent: a manual reason -> act -> observe loop over DEMO_TOOLS.

``langgraph.prebuilt.create_react_agent`` is deprecated (and uninstalled in
this environment). This module spells the ReAct loop out explicitly: a
``reason`` node asks the model what to do next, a conditional edge checks
whether it proposed a tool call, an ``act`` node (``ToolNode``) executes it,
and the resulting observation feeds straight back into ``reason`` — repeating
until the model answers with plain text instead of a tool call.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/21_react_agent/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import AgentState, DEMO_TOOLS, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

MODEL = get_chat_model(max_tool_calls=2).bind_tools(DEMO_TOOLS)


def reason(state: AgentState) -> dict[str, object]:
    """Reason: ask the model what to do next given the transcript so far."""
    ai_message = MODEL.invoke(state["messages"])
    if ai_message.tool_calls:
        logger.info("reason: proposing tool call(s) %s", ai_message.tool_calls)
    else:
        logger.info("reason: final answer ready")
    return {"messages": [ai_message]}


def route_after_reason(state: AgentState) -> str:
    """Act if the model proposed a tool call; otherwise the loop is done."""
    last = state["messages"][-1]
    return "act" if getattr(last, "tool_calls", None) else "done"


def build_graph():
    """Compile the reason -> act -> observe loop: agent <-> tools until done."""
    graph = StateGraph(AgentState)
    graph.add_node("reason", reason)
    graph.add_node("act", ToolNode(DEMO_TOOLS))  # "act" executes, its output is the "observe" step
    graph.add_edge(START, "reason")
    graph.add_conditional_edges("reason", route_after_reason, {"act": "act", "done": END})
    graph.add_edge("act", "reason")
    return graph.compile()


QUERY = "What's the weather in Paris? Then send a slack message to the team."


def main() -> None:
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content=QUERY)]})

    for message in result["messages"]:
        if isinstance(message, HumanMessage):
            print(f"reason(input)={message.content!r}")
        elif isinstance(message, AIMessage) and message.tool_calls:
            print(f"act(propose)={[tc['name'] for tc in message.tool_calls]}")
        elif isinstance(message, ToolMessage):
            print(f"observe={message.content!r}")
        else:
            print(f"reason(final)={message.content!r}")

    print("=== TRACK3 MODULE 21: REACT AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
