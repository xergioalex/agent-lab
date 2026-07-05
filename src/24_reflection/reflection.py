"""24 — Reflection: a bounded generate -> critique -> revise self-critique loop.

``generate`` drafts an answer, ``critique`` judges it against a simple quality
bar (word count — a stand-in for a real rubric), and — if it falls short —
the feedback is fed back in as a new human turn before looping back to
``generate``. The offline fake model advances through a canned list of
increasingly detailed drafts one per human turn (see
``FakeToolCallingModel._final_text``), which is exactly what lets this
scripted loop demonstrate the answer visibly improving across revisions. A
hard ``MAX_ITERATIONS`` guard forces approval even if the quality bar is
never met, guaranteeing termination.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/24_reflection/reflection.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

MAX_ITERATIONS = 3
MIN_WORDS = 12

# Canned drafts of increasing quality/length; the fake model cycles through
# them one per human turn, which is what lets the critique loop below observe
# a real (if scripted) improvement across revisions.
MODEL = get_chat_model(
    responses=[
        "Agents plan and act.",
        "Agents plan, then act using tools, then observe the results.",
        "Agents plan, act with tools, observe results, and reflect to revise "
        "their answer before responding to the user.",
    ]
)


def generate(state: AgentState) -> dict[str, object]:
    """Draft (or revise) an answer given the conversation so far."""
    context = state.get("context", {})
    iteration = context.get("iteration", 0) + 1
    draft = MODEL.invoke(state["messages"])
    logger.info("iteration %d draft=%r", iteration, draft.content)
    return {"messages": [draft], "context": {**context, "iteration": iteration}}


def critique(state: AgentState) -> dict[str, object]:
    """Judge the latest draft; force approval once the iteration cap is hit."""
    context = state["context"]
    draft = str(state["messages"][-1].content)
    word_count = len(draft.split())
    if context["iteration"] >= MAX_ITERATIONS or word_count >= MIN_WORDS:
        verdict, feedback = "approved", "meets the length/detail bar"
    else:
        verdict = "revise"
        feedback = f"too brief ({word_count} words) — add more concrete detail"
    logger.info("critique: %s (%s)", verdict, feedback)
    return {"context": {**context, "verdict": verdict, "feedback": feedback}}


def route_after_critique(state: AgentState) -> str:
    """Loop back for another revision, or stop once approved."""
    return "revise" if state["context"]["verdict"] == "revise" else "done"


def add_feedback(state: AgentState) -> dict[str, object]:
    """Feed the critique back in as a new human turn before the next draft."""
    feedback = state["context"]["feedback"]
    return {"messages": [HumanMessage(content=f"Revise: {feedback}")]}


def build_graph():
    """Compile the generate -> critique -> revise loop."""
    graph = StateGraph(AgentState)
    graph.add_node("generate", generate)
    graph.add_node("critique", critique)
    graph.add_node("add_feedback", add_feedback)

    graph.add_edge(START, "generate")
    graph.add_edge("generate", "critique")
    graph.add_conditional_edges(
        "critique", route_after_critique, {"revise": "add_feedback", "done": END}
    )
    graph.add_edge("add_feedback", "generate")
    return graph.compile()


GOAL = "Explain how AI agents work in one sentence."


def main() -> None:
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content=GOAL)]})

    drafts = [m.content for m in result["messages"] if isinstance(m, AIMessage)]
    for revision, draft in enumerate(drafts, start=1):
        print(f"revision {revision}: {draft!r}")

    context = result["context"]
    print(f"iterations={context['iteration']} verdict={context['verdict']}")
    print("=== TRACK3 MODULE 24: REFLECTION COMPLETE ===")


if __name__ == "__main__":
    main()
