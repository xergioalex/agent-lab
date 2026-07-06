"""35 -- Memory Scoring: relevance + recency + importance as one deterministic score.

Combines three signals into a single weighted score used to rank memories:
relevance (word overlap with the query), recency (linear decay from an
injected fixed "now" tick, never wall-clock), and importance (an explicit
weight assigned at write time). Prints the full breakdown per candidate so
each contribution is visible.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

# Make `src.shared` importable when run as `python src/35_memory_scoring/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


@dataclass
class Candidate:
    """A scorable memory candidate."""

    text: str
    tick: int  # when it was written (fixed-clock tick, not wall-clock)
    importance: float  # 0..1, assigned at write time


CANDIDATES: tuple[Candidate, ...] = (
    Candidate("User asked how to reset their password.", tick=1, importance=0.4),
    Candidate(
        "Fact: password resets invalidate all existing sessions.", tick=8, importance=0.8
    ),
    Candidate("User mentioned they like dark mode.", tick=2, importance=0.2),
    Candidate(
        "Procedure reset_password: verify identity, send link.", tick=9, importance=0.9
    ),
)

NOW_TICK = 10
RECENCY_HALF_LIFE = 5
RELEVANCE_WEIGHT = 0.5
RECENCY_WEIGHT = 0.3
IMPORTANCE_WEIGHT = 0.2


def _tokenize(text: str) -> set[str]:
    return {tok.strip(".,:?").lower() for tok in text.split() if tok.strip(".,:?")}


def relevance_score(query: str, candidate: Candidate) -> float:
    """Fraction of query tokens present in the candidate text (0..1)."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0.0
    overlap = query_tokens & _tokenize(candidate.text)
    return len(overlap) / len(query_tokens)


def recency_score(candidate: Candidate, now_tick: int, half_life: int = RECENCY_HALF_LIFE) -> float:
    """Linear decay: 1.0 at ``now_tick``, 0.0 at (or beyond) ``half_life`` ticks old."""
    age = max(now_tick - candidate.tick, 0)
    return max(0.0, 1.0 - age / half_life)


def total_score(query: str, candidate: Candidate, now_tick: int) -> dict[str, float]:
    """Weighted sum of relevance, recency, and importance -- fully deterministic."""
    rel = relevance_score(query, candidate)
    rec = recency_score(candidate, now_tick)
    imp = candidate.importance
    total = RELEVANCE_WEIGHT * rel + RECENCY_WEIGHT * rec + IMPORTANCE_WEIGHT * imp
    return {
        "relevance": round(rel, 3),
        "recency": round(rec, 3),
        "importance": round(imp, 3),
        "total": round(total, 3),
    }


def main() -> None:
    query = "How do I reset my password?"
    print(f"query={query!r} now_tick={NOW_TICK}")

    scored = [(c, total_score(query, c, NOW_TICK)) for c in CANDIDATES]
    scored.sort(key=lambda pair: pair[1]["total"], reverse=True)

    for candidate, breakdown in scored:
        print(
            f"text={candidate.text!r} "
            f"relevance={breakdown['relevance']} recency={breakdown['recency']} "
            f"importance={breakdown['importance']} total={breakdown['total']}"
        )
        logger.info("scored candidate %r -> %s", candidate.text, breakdown)

    print("=== TRACK4 MODULE 35: MEMORY SCORING COMPLETE ===")


if __name__ == "__main__":
    main()
