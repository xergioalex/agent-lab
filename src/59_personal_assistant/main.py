"""59 — Personal Assistant: memory + tool routing + recall.

Capstone that integrates **Track 1** routing (module `11_graph_branching`),
**Track 3** tool loops (module `05_tools`), and **Track 4** memory
(module `06_memory_basics`) into one assistant: every turn is written to a
session memory log, an intent router decides whether the turn needs a tool
action, a memory recall, or a plain chat reply, and a manual `ToolNode` loop
(no deprecated `create_react_agent`) executes any tool calls.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/59_personal_assistant/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

from src.shared import DEMO_TOOLS, AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

TOOLS = DEMO_TOOLS
_TOOL_NODE = ToolNode(TOOLS)

# Keyword tables driving the deterministic offline intent router.
_TOOL_KEYWORDS = ("weather", "task", "slack", "sum")
_RECALL_KEYWORDS = ("remember", "earlier", "before", "recall", "previous")


def _classify(text: str) -> str:
    """Deterministic keyword-based intent classifier (Track 1 routing)."""
    lowered = text.lower()
    if any(keyword in lowered for keyword in _RECALL_KEYWORDS):
        return "recall"
    if any(keyword in lowered for keyword in _TOOL_KEYWORDS):
        return "tool"
    return "chat"


def ingest(state: AgentState) -> dict[str, Any]:
    """Write the incoming turn to session memory and classify its intent."""
    text = str(state["messages"][-1].content)
    context = state.get("context", {})
    memory: list[str] = list(context.get("memory", []))
    memory.append(f"user: {text}")
    intent = _classify(text)
    logger.info("ingested turn intent=%s", intent)
    return {"context": {**context, "memory": memory, "intent": intent}}


def route_intent(state: AgentState) -> str:
    """Conditional-edge router: dispatch on the classified intent."""
    return state["context"]["intent"]


def call_model(state: AgentState) -> dict[str, Any]:
    """Agent node: let the (offline) model pick a tool or answer directly."""
    model = get_chat_model().bind_tools(TOOLS)
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def route_after_model(state: AgentState) -> str:
    """Loop back to the tool node while the model keeps requesting tools."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "finalize"


def recall(state: AgentState) -> dict[str, Any]:
    """Answer from session memory instead of the model or a tool."""
    text = str(state["messages"][-1].content).lower()
    tokens = [w for w in text.split() if len(w) > 3]
    memory = state["context"]["memory"][:-1]  # exclude the current turn itself
    hits = [entry for entry in memory if any(tok in entry.lower() for tok in tokens)]
    reply = (
        "Recalled from memory: " + " | ".join(hits)
        if hits
        else "Nothing in memory matches that yet."
    )
    return {"messages": [AIMessage(content=reply)]}


def chat(state: AgentState) -> dict[str, Any]:
    """Plain conversational reply — no tool, no recall needed."""
    return {"messages": [AIMessage(content="Got it — anything else I can help with?")]}


def finalize(state: AgentState) -> dict[str, Any]:
    """Convergence node: append the assistant's reply to session memory."""
    reply = str(state["messages"][-1].content)
    memory = list(state["context"]["memory"])
    memory.append(f"assistant: {reply}")
    return {"context": {**state["context"], "memory": memory}}


def build_graph():
    """Compile the personal-assistant graph (routing + tools + memory)."""
    graph = StateGraph(AgentState)
    graph.add_node("ingest", ingest)
    graph.add_node("agent", call_model)
    graph.add_node("tools", _TOOL_NODE)
    graph.add_node("recall", recall)
    graph.add_node("chat", chat)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "ingest")
    graph.add_conditional_edges(
        "ingest", route_intent, {"tool": "agent", "recall": "recall", "chat": "chat"}
    )
    graph.add_conditional_edges(
        "agent", route_after_model, {"tools": "tools", "finalize": "finalize"}
    )
    graph.add_edge("tools", "agent")
    graph.add_edge("recall", "finalize")
    graph.add_edge("chat", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


REQUESTS: tuple[str, ...] = (
    "What is the weather in Paris?",
    "Do you remember what I asked earlier?",
    "Thanks, that is all for now.",
)


def main() -> None:
    app = build_graph()
    context: dict[str, Any] = {"memory": []}
    for request in REQUESTS:
        result = app.invoke(
            {"messages": [HumanMessage(content=request)], "context": context}
        )
        context = result["context"]
        reply = result["messages"][-1].content
        print(f"user={request!r} intent={context['intent']} reply={reply!r}")

    print(f"memory_entries={len(context['memory'])}")
    print("=== TRACK9 MODULE 59: PERSONAL ASSISTANT COMPLETE ===")


if __name__ == "__main__":
    main()
