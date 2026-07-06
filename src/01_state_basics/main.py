"""01 — State Basics: multi-stage pipeline with branching and audit trail.

Every step is a pure ``state -> state`` transformation chained in order.
Conditional routing is explicit Python (module 02 re-expresses this as a
LangGraph). An ``audit`` list records which nodes ran so the final state is
self-documenting.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


class PipelineState(TypedDict, total=False):
    message: str
    priority: str
    category: str
    enriched: str
    valid: bool
    route: str
    response: str
    audit: list[str]


def _append_audit(state: PipelineState, step: str) -> list[str]:
    return [*state.get("audit", []), step]


def ingest(state: PipelineState) -> PipelineState:
    return {**state, "audit": _append_audit(state, "ingest")}


def classify(state: PipelineState) -> PipelineState:
    text = state["message"].lower()
    category = "incident" if any(w in text for w in ("down", "crash", "block")) else "request"
    priority = "high" if category == "incident" else "normal"
    logger.info("classified category=%s priority=%s", category, priority)
    return {
        **state,
        "category": category,
        "priority": priority,
        "audit": _append_audit(state, "classify"),
    }


def enrich(state: PipelineState) -> PipelineState:
    prefix = f"[{state['priority']}/{state['category']}]"
    return {
        **state,
        "enriched": f"{prefix} {state['message']}",
        "audit": _append_audit(state, "enrich"),
    }


def validate(state: PipelineState) -> PipelineState:
    valid = len(state["message"]) >= 3
    return {**state, "valid": valid, "audit": _append_audit(state, "validate")}


def route_decision(state: PipelineState) -> PipelineState:
    if not state.get("valid"):
        route = "reject"
    elif state.get("category") == "incident":
        route = "escalate"
    else:
        route = "standard"
    return {**state, "route": route, "audit": _append_audit(state, "route")}


def format_response(state: PipelineState) -> PipelineState:
    route = state.get("route", "standard")
    if route == "reject":
        response = "rejected: message too short"
    elif route == "escalate":
        response = f"escalated: {state.get('enriched', state['message'])}"
    else:
        response = f"accepted: {state.get('enriched', state['message'])}"
    return {**state, "response": response, "audit": _append_audit(state, "format")}


PIPELINE = (
    ingest,
    classify,
    enrich,
    validate,
    route_decision,
    format_response,
)


def run_pipeline(message: str) -> PipelineState:
    state: PipelineState = {"message": message, "audit": []}
    for step in PIPELINE:
        state = step(state)
    return state


REQUESTS: tuple[str, ...] = (
    "hello team",
    "we are blocked on the deploy",
    "ok",
)


def main() -> None:
    for message in REQUESTS:
        final = run_pipeline(message)
        print(
            f"message={message!r} route={final['route']} "
            f"response={final['response']!r} audit={final['audit']}"
        )
    print("=== MODULE 01: STATE BASICS COMPLETE ===")


if __name__ == "__main__":
    main()
