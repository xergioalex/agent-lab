"""19 — Context Engineering: trimming and running summarization.

Two complementary techniques for keeping a long-running conversation inside
a bounded context window:

- **Trimming** (`trim_messages`) drops the oldest messages once an
  approximate token budget is exceeded, optionally keeping the leading
  `SystemMessage`.
- **Running summarization** condenses the messages that trimming would
  otherwise discard into a single summary string, stored in `AgentState`'s
  free-form `context` channel, so information isn't silently lost — only
  compressed.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/19_context_engineering/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import (  # noqa: E402
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.messages.utils import count_tokens_approximately  # noqa: E402

from src.shared import AgentState, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

TRIM_MAX_TOKENS = 60
KEEP_RECENT = 4


def build_long_history() -> list[BaseMessage]:
    """Simulate a dozen turns of a support conversation."""
    topics = [
        "how do I reset my password",
        "where is the on-call schedule",
        "how do I request vacation",
        "what is the deploy process",
        "why did the last build fail",
        "how do I roll back a release",
    ]
    history: list[BaseMessage] = [
        SystemMessage(content="You are a helpful support assistant.")
    ]
    for topic in topics:
        history.append(HumanMessage(content=f"Question: {topic}?"))
        history.append(AIMessage(content=f"Answer about: {topic}."))
    return history


def budget(messages: list[BaseMessage]) -> dict[str, int]:
    """Report the message-count and approximate-token budget of a transcript."""
    return {
        "messages": len(messages),
        "approx_tokens": count_tokens_approximately(messages),
    }


def trim_to_budget(messages: list[BaseMessage], *, max_tokens: int) -> list[BaseMessage]:
    """Keep only the most recent messages (plus the leading system prompt)
    that fit within `max_tokens`, approximated with `count_tokens_approximately`.
    """
    return trim_messages(
        messages,
        max_tokens=max_tokens,
        token_counter="approximate",
        strategy="last",
        include_system=True,
    )


def summarizing_memory_node(
    state: AgentState, *, keep_recent: int = KEEP_RECENT
) -> dict[str, object]:
    """LangGraph-node-shaped function: condense old turns into `context["summary"]`.

    Wire this into a graph as any other node (`graph.add_node("memory", ...)`).
    It leaves the most recent `keep_recent` messages untouched and folds
    everything older into a single summary string produced by an (offline)
    summarizer call — real usage would prompt a capable model with the old
    transcript; here the fake returns a deterministic canned summary so the
    exercise stays reproducible.
    """
    messages = state.get("messages", [])
    if len(messages) <= keep_recent:
        return {"context": state.get("context", {})}

    old, recent = messages[:-keep_recent], messages[-keep_recent:]
    summarizer = get_chat_model(
        responses=[f"Summary of {len(old)} earlier turn(s) about support topics."]
    )
    summary = summarizer.invoke(
        [HumanMessage(content=" ".join(str(m.content) for m in old))]
    ).content

    logger.info("condensed %d old message(s) into a summary", len(old))
    return {
        "context": {
            **state.get("context", {}),
            "summary": summary,
            "condensed_count": len(old),
            "kept_recent": [type(m).__name__ for m in recent],
        }
    }


def main() -> None:
    history = build_long_history()
    before = budget(history)
    print(f"before_trim={before}")

    trimmed = trim_to_budget(history, max_tokens=TRIM_MAX_TOKENS)
    after_trim = budget(trimmed)
    print(f"after_trim={after_trim}")

    state: AgentState = {"messages": history, "context": {}}
    result = summarizing_memory_node(state, keep_recent=KEEP_RECENT)
    context = result["context"]
    print(f"summary={context['summary']!r}")
    print(f"condensed_count={context['condensed_count']} kept_recent={context['kept_recent']}")

    print("=== TRACK2 MODULE 19: CONTEXT ENGINEERING COMPLETE ===")


if __name__ == "__main__":
    main()
