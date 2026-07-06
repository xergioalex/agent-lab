"""34 -- Memory Retrieval: query -> rank -> assemble context across memory types.

Given a query, pulls candidates from all four memory kinds (conversation,
episodic, semantic, procedural), ranks them by a simple relevance score, and
assembles the highest-ranked items into one budget-bounded context block
ready to inject into a prompt.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

# Make `src.shared` importable when run as `python src/34_memory_retrieval/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


@dataclass
class MemoryItem:
    """A single retrievable item, tagged with the memory kind it came from."""

    kind: str
    text: str


MEMORY_POOL: tuple[MemoryItem, ...] = (
    MemoryItem("conversation", "User asked how to reset their password."),
    MemoryItem("episodic", "At tick=12 the user triggered a password reset."),
    MemoryItem("semantic", "Fact: password resets invalidate all existing sessions."),
    MemoryItem(
        "procedural",
        "Procedure reset_password: verify identity, send link, set new password.",
    ),
    MemoryItem("semantic", "Fact: the support team's SLA is 24 hours."),
    MemoryItem("episodic", "At tick=3 the user logged in from a new device."),
)


def _tokenize(text: str) -> set[str]:
    return {tok.strip(".,:?").lower() for tok in text.split() if tok.strip(".,:?")}


def relevance(query: str, item: MemoryItem) -> int:
    """Word-overlap relevance: number of tokens shared between query and item."""
    return len(_tokenize(query) & _tokenize(item.text))


def rank(query: str, pool: tuple[MemoryItem, ...]) -> list[tuple[MemoryItem, int]]:
    """Sort the pool by descending relevance to ``query`` (stable for ties)."""
    scored = [(item, relevance(query, item)) for item in pool]
    return sorted(scored, key=lambda pair: pair[1], reverse=True)


def assemble(ranked: list[tuple[MemoryItem, int]], budget_chars: int) -> str:
    """Greedily add the highest-ranked items until the character budget is spent."""
    lines: list[str] = []
    used = 0
    for item, score in ranked:
        if score <= 0:
            continue
        line = f"[{item.kind}] {item.text}"
        if used + len(line) > budget_chars:
            break
        lines.append(line)
        used += len(line)
    return "\n".join(lines)


def main() -> None:
    query = "How do I reset my password?"
    ranked = rank(query, MEMORY_POOL)

    print(f"query={query!r}")
    for item, score in ranked:
        print(f"  score={score} kind={item.kind} text={item.text!r}")

    context = assemble(ranked, budget_chars=160)
    print("assembled context (budget=160 chars):")
    print(context)

    logger.info("assembled %d char(s) of context for query %r", len(context), query)
    print("=== TRACK4 MODULE 34: MEMORY RETRIEVAL COMPLETE ===")


if __name__ == "__main__":
    main()
