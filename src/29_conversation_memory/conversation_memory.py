"""29 -- Conversation Memory: short-term buffer, window, and summary strategies.

Demonstrates three ways to bound a growing conversation over
``AgentState.messages``: keep everything (buffer), keep only the last N turns
(window), or keep the last N turns verbatim plus a summary of the rest
(summary). Contrasts token cost vs. context loss for each strategy.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/29_conversation_memory/conversation_memory.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)


def buffer_all(messages: list[BaseMessage]) -> list[str]:
    """Buffer strategy: keep the entire conversation, no eviction."""
    return [str(m.content) for m in messages]


def window_last_n(messages: list[BaseMessage], n: int) -> list[str]:
    """Window strategy: keep only the last ``n`` messages, drop the rest."""
    return [str(m.content) for m in messages[-n:]]


def summarize_overflow(messages: list[BaseMessage], n: int) -> tuple[str, list[str]]:
    """Summary strategy: keep the last ``n`` verbatim + a summary of the evicted head.

    The "summary" is a deterministic digest (no LLM call) so the exercise stays
    offline and reproducible; in production this step would call an LLM.
    """
    evicted = messages[:-n] if len(messages) > n else []
    kept = messages[-n:]
    if not evicted:
        summary = "(no overflow)"
    else:
        topics = ", ".join(str(m.content)[:20] for m in evicted)
        summary = f"[summary of {len(evicted)} earlier turn(s): {topics}]"
    return summary, [str(m.content) for m in kept]


CONVERSATION: tuple[BaseMessage, ...] = (
    HumanMessage(content="Hi, I'm planning a trip to Kyoto."),
    AIMessage(content="Great! When are you traveling?"),
    HumanMessage(content="Sometime in April, for cherry blossoms."),
    AIMessage(content="April is peak season, book early."),
    HumanMessage(content="Any ryokan recommendations near Gion?"),
    AIMessage(content="I'd suggest looking at traditional inns in Higashiyama."),
)


def main() -> None:
    state: AgentState = {"messages": list(CONVERSATION)}
    messages = state["messages"]

    full = buffer_all(messages)
    windowed = window_last_n(messages, 3)
    summary, kept = summarize_overflow(messages, 3)

    print(f"buffer: {len(full)} message(s) retained (all)")
    print(f"window(n=3): {len(windowed)} message(s) retained -> {windowed}")
    print(f"summary(n=3): {summary}")
    print(f"summary(n=3) kept verbatim -> {kept}")

    logger.info("conversation memory strategies compared over %d turns", len(messages))
    print("=== TRACK4 MODULE 29: CONVERSATION MEMORY COMPLETE ===")


if __name__ == "__main__":
    main()
