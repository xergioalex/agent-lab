"""15 — Chat Models: typed messages and the provider bridge.

Demonstrates the four core message types (``SystemMessage``, ``HumanMessage``,
``AIMessage``, ``ToolMessage``) and how ``get_chat_model`` is the single seam
that swaps a real ``ChatOpenAI`` for the deterministic, offline
``FakeToolCallingModel`` — the exact same call site works with either backend.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/15_chat_models/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import (  # noqa: E402
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from src.shared import get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a concise on-call assistant. Answer in one short sentence."
)


def build_first_turn(user_text: str) -> list[BaseMessage]:
    """A minimal chat turn: system persona + a single human message."""
    return [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_text)]


def append_reply(history: list[BaseMessage], reply: AIMessage) -> list[BaseMessage]:
    """Grow the transcript with the model's reply — the shape LangGraph's
    ``add_messages`` reducer preserves across graph turns (see module 03)."""
    return [*history, reply]


def build_tool_observation_turn(
    history: list[BaseMessage], tool_call_id: str, observation: str
) -> list[BaseMessage]:
    """A ``ToolMessage`` reports a tool's result back to the model.

    Every ``ToolMessage`` must carry the ``tool_call_id`` of the ``AIMessage``
    tool call it answers — this is how the model correlates results with
    requests when several tools are in flight (module 17 builds this loop).
    """
    return [*history, ToolMessage(content=observation, tool_call_id=tool_call_id)]


def main() -> None:
    model = get_chat_model(
        responses=[
            "The on-call rotation is posted in #oncall.",
            "Deploys require two approvals before shipping.",
        ]
    )

    # Turn 1: system + human -> AI reply.
    history = build_first_turn("Who is on call this week?")
    reply_1 = model.invoke(history)
    logger.info("turn 1 reply: %s", reply_1.content)
    history = append_reply(history, reply_1)
    print(f"turn=1 roles={[type(m).__name__ for m in history]}")
    print(f"turn=1 reply={reply_1.content!r}")

    # Turn 2: append a follow-up human message, reuse the same running history.
    history = [*history, HumanMessage(content="What about deploy approvals?")]
    reply_2 = model.invoke(history)
    history = append_reply(history, reply_2)
    print(f"turn=2 roles={[type(m).__name__ for m in history]}")
    print(f"turn=2 reply={reply_2.content!r}")

    # A ToolMessage in the transcript: the shape used once tools are involved.
    tool_history = build_tool_observation_turn(
        build_first_turn("Send a status update to the team."),
        tool_call_id="call_1",
        observation="Slack sent: status update",
    )
    print(f"tool_history roles={[type(m).__name__ for m in tool_history]}")

    print("=== TRACK2 MODULE 15: CHAT MODELS COMPLETE ===")


if __name__ == "__main__":
    main()
