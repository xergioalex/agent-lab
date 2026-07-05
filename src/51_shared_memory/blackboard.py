"""51 — Shared Memory: a blackboard agents post facts to and read from.

A **blackboard** is a shared workspace: agents post observations under their
own namespace and read whatever earlier agents have already posted. Three
agents run in sequence — ``researcher``, ``planner``, ``critic`` — each
reading the board built so far and posting one new fact to it, followed by a
``summarize`` node that prints the final board. Because the graph runs the
agents one after another, each agent's write is fully merged into state
*before* the next agent's node runs — this is what guarantees read-after-write
ordering (an agent always sees prior posts, never a half-written board).

The board lives in ``AgentState.context["blackboard"]``, namespaced per agent
(``{"researcher": [...], "planner": [...], "critic": [...]}``) so two agents'
posts never collide — reusing `src.shared`'s in-memory ``AgentState``, no new
storage infrastructure required.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

# Make `src.shared` importable when run as `python src/51_shared_memory/blackboard.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

Board = dict[str, list[str]]


def _agent_node(name: str, produce_fact: Callable[[Board], str]):
    """Build a node that reads the board so far and posts one fact under `name`."""

    def node(state: AgentState) -> dict[str, Any]:
        context = state.get("context", {})
        board: Board = context.get("blackboard", {})
        fact = produce_fact(board)
        # Namespacing per agent (own list under its own key) is what lets two
        # agents post in the same run without overwriting each other's facts.
        updated_board = {**board, name: [*board.get(name, []), fact]}
        note = f"[{name}] posted: {fact}"
        logger.info(note)
        return {
            "context": {**context, "blackboard": updated_board},
            "scratchpad": [note],
        }

    return node


def _researcher_fact(_board: Board) -> str:
    return "LangGraph state updates are merged into shared state via reducers."


def _planner_fact(board: Board) -> str:
    finding = board["researcher"][-1]
    return f"Plan: apply '{finding}' when designing the next module."


def _critic_fact(board: Board) -> str:
    plan = board["planner"][-1]
    return f"Critique: '{plan}' is sound but should mention namespacing too."


def summarize(state: AgentState) -> dict[str, Any]:
    """Read the final board and print every agent's namespaced contribution."""
    board: Board = state["context"]["blackboard"]
    lines = [f"{agent}: {' | '.join(facts)}" for agent, facts in sorted(board.items())]
    message = AIMessage(content="Blackboard summary -- " + "; ".join(lines))
    return {"messages": [message]}


def build_graph():
    """Compile the sequential researcher -> planner -> critic -> summarize graph."""
    graph = StateGraph(AgentState)
    graph.add_node("researcher", _agent_node("researcher", _researcher_fact))
    graph.add_node("planner", _agent_node("planner", _planner_fact))
    graph.add_node("critic", _agent_node("critic", _critic_fact))
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "planner")
    graph.add_edge("planner", "critic")
    graph.add_edge("critic", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({"context": {"blackboard": {}}})

    for note in result["scratchpad"]:
        print(note)

    board: Board = result["context"]["blackboard"]
    for agent in sorted(board):
        print(f"board[{agent}]={board[agent]}")

    print(f"summary: {result['messages'][-1].content}")
    print("=== TRACK7 MODULE 51: SHARED MEMORY COMPLETE ===")


if __name__ == "__main__":
    main()
