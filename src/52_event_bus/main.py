"""52 — Event Bus: pub/sub message routing decoupled from graph edges.

A hard-wired conditional edge (module 11) requires the router to know every
possible destination up front: `mapping = {"bug": bug_node, ...}`. A **pub/sub
event bus** inverts that: publishers emit events on named topics without
knowing who (if anyone) is listening, and subscribers register interest in a
topic independently of the publisher. Adding a new subscriber never touches
the publisher's code — that's the decoupling win over hard-wired routing.

Here the bus lives inside a single graph node (``dispatch_events``): in a
real distributed system each subscriber would be its own process/agent
listening on a queue, but the routing *logic* — topic -> handler list,
looked up dynamically at publish time — is identical.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

# Make `src.shared` importable when run as `python src/52_event_bus/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

Handler = Callable[[dict[str, Any]], str]


class EventBus:
    """A minimal in-process publish/subscribe bus.

    Subscribers register a handler for a topic; publishing an event dispatches
    it to every handler subscribed to that topic, in subscription order. The
    publisher never references a handler directly — only the topic name.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = {}

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    def publish(self, topic: str, payload: dict[str, Any], log: list[str]) -> None:
        handlers = self._subscribers.get(topic, [])
        if not handlers:
            log.append(f"{topic} -> (no subscribers)")
            return
        for handler in handlers:
            result = handler(payload)
            entry = f"{topic} -> {handler.__name__}: {result}"
            logger.info(entry)
            log.append(entry)


def researcher_handler(payload: dict[str, Any]) -> str:
    return f"researched {payload['topic']}"


def writer_handler(payload: dict[str, Any]) -> str:
    return f"drafted note about {payload['topic']}"


def auditor_handler(payload: dict[str, Any]) -> str:
    return f"logged event for audit: {payload['topic']}"


# Static topic -> event payload sequence. Each topic may have zero, one, or
# several subscribers, dispatched independently of this list.
EVENTS: tuple[tuple[str, dict[str, Any]], ...] = (
    ("research.requested", {"topic": "reducers"}),
    ("draft.requested", {"topic": "reducers"}),
)


def dispatch_events(state: AgentState) -> dict[str, Any]:
    """Build the bus, register subscribers, publish every event, log delivery."""
    bus = EventBus()
    bus.subscribe("research.requested", researcher_handler)
    bus.subscribe("research.requested", auditor_handler)
    bus.subscribe("draft.requested", writer_handler)
    bus.subscribe("draft.requested", auditor_handler)

    log: list[str] = []
    for topic, payload in EVENTS:
        bus.publish(topic, payload, log)

    return {"scratchpad": log}


def summarize(state: AgentState) -> dict[str, Any]:
    """Report how many events were delivered across all subscribers."""
    log = state.get("scratchpad", [])
    message = AIMessage(content=f"Delivered {len(log)} event(s) via the bus.")
    return {"messages": [message]}


def build_graph():
    """Compile the dispatch_events -> summarize graph."""
    graph = StateGraph(AgentState)
    graph.add_node("dispatch_events", dispatch_events)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "dispatch_events")
    graph.add_edge("dispatch_events", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({})

    print("delivered event log:")
    for entry in result["scratchpad"]:
        print(f"  {entry}")
    print(result["messages"][-1].content)

    print("=== TRACK7 MODULE 52: EVENT BUS COMPLETE ===")


if __name__ == "__main__":
    main()
