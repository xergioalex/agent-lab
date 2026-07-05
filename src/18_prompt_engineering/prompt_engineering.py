"""18 — Prompt Engineering: templates, system prompts, and few-shot examples.

Compares a bare, structure-free prompt against a ``ChatPromptTemplate`` that
adds a system persona and few-shot examples. The rendered message lists make
the structural difference visible; the model configuration (canned response
sets) stands in for the fact that a real LLM's completion quality and format
follow directly from how the prompt is built — structure is not decoration,
it's the interface contract with the model.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/18_prompt_engineering/prompt_engineering.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.prompts import ChatPromptTemplate  # noqa: E402

from src.shared import get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

# A naive prompt: no persona, no format contract, just the raw question.
NAIVE_PROMPT = ChatPromptTemplate.from_messages([("human", "{question}")])

# Few-shot examples teach the model the exact output shape we want.
FEW_SHOT_EXAMPLES: list[tuple[str, str]] = [
    ("The app crashes on save.", "CATEGORY: bug | ACTION: escalate to engineering"),
    ("I'd like a dark mode option.", "CATEGORY: feature | ACTION: add to roadmap"),
]

_engineered_messages: list[tuple[str, str]] = [
    ("system", "You are a terse ticket-triage assistant. Reply only in the format "
                "'CATEGORY: <cat> | ACTION: <action>'. Study the examples."),
]
for example_input, example_output in FEW_SHOT_EXAMPLES:
    _engineered_messages.append(("human", example_input))
    _engineered_messages.append(("ai", example_output))
_engineered_messages.append(("human", "{question}"))

ENGINEERED_PROMPT = ChatPromptTemplate.from_messages(_engineered_messages)


def main() -> None:
    question = "The app crashes when I hit save, this is a bug."

    naive_messages = NAIVE_PROMPT.format_messages(question=question)
    engineered_messages = ENGINEERED_PROMPT.format_messages(question=question)

    print(f"naive_message_count={len(naive_messages)} roles="
          f"{[type(m).__name__ for m in naive_messages]}")
    print(f"engineered_message_count={len(engineered_messages)} roles="
          f"{[type(m).__name__ for m in engineered_messages]}")

    # The naive model has no canned responses -> it falls back to echoing the
    # query, which is what an under-specified prompt tends to produce: a
    # generic, unstructured reply.
    naive_model = get_chat_model()
    naive_reply = naive_model.invoke(naive_messages)

    # The engineered model is configured with the well-formed, on-contract
    # answer the system prompt + few-shot examples are designed to elicit.
    engineered_model = get_chat_model(
        responses=["CATEGORY: bug | ACTION: escalate to engineering"]
    )
    engineered_reply = engineered_model.invoke(engineered_messages)

    logger.info("naive reply: %s", naive_reply.content)
    logger.info("engineered reply: %s", engineered_reply.content)

    print(f"naive_reply={naive_reply.content!r}")
    print(f"engineered_reply={engineered_reply.content!r}")
    print("=== TRACK2 MODULE 18: PROMPT ENGINEERING COMPLETE ===")


if __name__ == "__main__":
    main()
