"""16 — Structured Outputs: Pydantic schemas with a validate-and-retry loop.

``model.with_structured_output(Schema)`` returns a runnable that yields a
populated ``Schema`` instance instead of free text. Real models sometimes
emit output that fails the schema's own validation (a category outside an
allowed set, a malformed enum, …) — production code must catch
``pydantic.ValidationError`` and retry with a repaired prompt rather than
crash. This module builds that loop and demonstrates it against the offline
``FakeToolCallingModel``, which we deliberately feed a first message that
fails validation so the retry path actually runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/16_structured_outputs/structured_output.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pydantic import BaseModel, ValidationError, field_validator  # noqa: E402

from src.shared import get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

ALLOWED_CATEGORIES = ("bug", "feature", "question")
MAX_ATTEMPTS = 3


class TicketSummary(BaseModel):
    """The typed shape we want the model to fill in."""

    category: str
    priority: int
    summary: str

    @field_validator("category")
    @classmethod
    def category_must_be_known(cls, value: str) -> str:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"category {value!r} is not one of {ALLOWED_CATEGORIES}"
            )
        return value


def _repair_prompt(raw_text: str) -> str:
    """Turn a rejected free-text ticket into a normalized category keyword.

    Stands in for a real repair strategy: re-prompting the model with the
    validation error appended, asking it to pick strictly from the allowed
    set. Here we do the equivalent deterministically by keyword-matching.
    """
    lowered = raw_text.lower()
    for category in ALLOWED_CATEGORIES:
        if category in lowered:
            return category
    return "question"  # safe default when nothing matches


def parse_with_retry(
    raw_text: str, *, max_attempts: int = MAX_ATTEMPTS
) -> tuple[TicketSummary, int]:
    """Call ``with_structured_output`` and retry on ``ValidationError``.

    Returns the validated model plus the attempt count it took to succeed.
    """
    model = get_chat_model()
    structured = model.with_structured_output(TicketSummary)
    attempt_text = raw_text

    for attempt in range(1, max_attempts + 1):
        try:
            result = structured.invoke(attempt_text)
        except ValidationError as exc:
            logger.warning("attempt %d rejected: %s", attempt, exc)
            attempt_text = _repair_prompt(attempt_text)
            continue
        logger.info("attempt %d accepted: %s", attempt, result)
        return result, attempt

    raise RuntimeError(f"structured output still invalid after {max_attempts} attempts")


def main() -> None:
    # This free-text ticket does not contain a bare category keyword, so the
    # fake model's first attempt (category == the whole sentence) fails
    # validation and the loop must repair and retry.
    raw_ticket = "The app crashes when I click save, this is a bug."

    result, attempts = parse_with_retry(raw_ticket)
    print(f"attempts={attempts}")
    print(f"category={result.category!r} priority={result.priority} summary={result.summary!r}")
    print(f"parsed_type={type(result).__name__}")

    print("=== TRACK2 MODULE 16: STRUCTURED OUTPUTS COMPLETE ===")


if __name__ == "__main__":
    main()
