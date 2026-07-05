"""49 — Negotiation: proposer / critic offer-critique-counter-offer loop.

A ``propose`` node emits an offer, a ``critique`` node scores it against an
acceptance range, and a conditional edge routes back to ``propose`` for
another round (a concession), or forward to ``converge`` once the offer is
accepted or a max-round cap is reached. This is the negotiation analogue of
module 14's retry loop: the same "retry vs. give up" shape, applied to two
agents converging on a deal instead of one node recovering from failure.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/49_negotiation/negotiation.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)


def propose(state: AgentState) -> dict[str, Any]:
    """Emit an offer: the opening offer on round 1, a concession thereafter."""
    context = state["context"]
    round_ = context["round"] + 1
    offer = context["opening_offer"] if round_ == 1 else context["offer"] - context["step"]
    note = f"[proposer] round {round_}: offer={offer}"
    logger.info(note)
    return {"context": {**context, "round": round_, "offer": offer}, "scratchpad": [note]}


def critique(state: AgentState) -> dict[str, Any]:
    """Score the current offer against the acceptance range and decide status."""
    context = state["context"]
    offer = context["offer"]
    round_ = context["round"]

    if context["target_min"] <= offer <= context["target_max"]:
        status = "accepted"
        note = f"[critic] round {round_}: accepted offer={offer}"
    elif round_ >= context["max_rounds"]:
        status = "capped"
        note = f"[critic] round {round_}: rejected offer={offer}, round cap reached"
    else:
        status = "pending"
        note = f"[critic] round {round_}: rejected offer={offer}, counter lower"
    logger.info(note)
    return {"context": {**context, "status": status}, "scratchpad": [note]}


def route_after_critique(state: AgentState) -> str:
    """Loop back for another concession, or converge once settled/capped."""
    status = state["context"]["status"]
    return "converge" if status in ("accepted", "capped") else "propose"


def converge(state: AgentState) -> dict[str, Any]:
    """Summarize the negotiation's final outcome."""
    context = state["context"]
    outcome = "deal" if context["status"] == "accepted" else "no_deal"
    message = AIMessage(
        content=f"Negotiation outcome={outcome} after {context['round']} round(s): "
        f"final offer={context['offer']}"
    )
    return {"messages": [message]}


def build_graph():
    """Compile the propose -> critique -(loop or converge)-> converge graph."""
    graph = StateGraph(AgentState)
    graph.add_node("propose", propose)
    graph.add_node("critique", critique)
    graph.add_node("converge", converge)

    graph.add_edge(START, "propose")
    graph.add_edge("propose", "critique")
    graph.add_conditional_edges(
        "critique",
        route_after_critique,
        {"propose": "propose", "converge": "converge"},
    )
    graph.add_edge("converge", END)
    return graph.compile()


SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "name": "settles_within_budget",
        "context": {
            "round": 0,
            "offer": 0,
            "opening_offer": 150,
            "target_min": 90,
            "target_max": 110,
            "step": 20,
            "max_rounds": 5,
            "status": "pending",
        },
    },
    {
        "name": "hits_round_cap",
        "context": {
            "round": 0,
            "offer": 0,
            "opening_offer": 150,
            "target_min": 1,
            "target_max": 5,
            "step": 20,
            "max_rounds": 5,
            "status": "pending",
        },
    },
)


def main() -> None:
    app = build_graph()

    for scenario in SCENARIOS:
        result = app.invoke({"context": scenario["context"]})
        for note in result["scratchpad"]:
            print(note)
        reply = result["messages"][-1].content
        print(f"scenario={scenario['name']} {reply}")

    print("=== TRACK7 MODULE 49: NEGOTIATION COMPLETE ===")


if __name__ == "__main__":
    main()
