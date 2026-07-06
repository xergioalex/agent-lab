"""03 — LLM Nodes: preprocess -> reason -> synthesize inside a StateGraph.

Uses ``get_chat_model()`` so the exercise runs offline (deterministic fake)
and automatically upgrades to ``ChatOpenAI`` when ``OPENAI_API_KEY`` is set.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_chat_model, get_logger, is_offline  # noqa: E402

logger = get_logger(__name__)

MODEL = get_chat_model(
    responses=["Summarized: the user greeted the agent and wants a concise reply."]
)


def preprocess(state: AgentState) -> dict[str, object]:
    text = str(state["messages"][-1].content).strip()
    normalized = " ".join(text.split())
    logger.info("preprocess: normalized %r", normalized)
    return {"context": {**state.get("context", {}), "normalized": normalized}}


def reason(state: AgentState) -> dict[str, object]:
    prompt = state["context"]["normalized"]
    reply = MODEL.invoke([HumanMessage(content=f"Reply briefly to: {prompt}")])
    return {"context": {**state["context"], "draft": str(reply.content)}}


def synthesize(state: AgentState) -> dict[str, object]:
    draft = state["context"]["draft"]
    backend = "offline-fake" if is_offline() else "openai"
    final = f"[{backend}] {draft}"
    return {"context": {**state["context"], "response": final}}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("preprocess", preprocess)
    graph.add_node("reason", reason)
    graph.add_node("synthesize", synthesize)
    graph.add_edge(START, "preprocess")
    graph.add_edge("preprocess", "reason")
    graph.add_edge("reason", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content="hello")]})
    print(f"response={result['context']['response']!r}")
    print("=== MODULE 03: LLM NODES COMPLETE ===")


if __name__ == "__main__":
    main()
