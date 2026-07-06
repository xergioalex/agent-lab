"""36 -- Memory Consolidation & Decay: merge duplicates, forget the stale.

Two maintenance passes over an episode set: **consolidation** merges repeated
occurrences of the same underlying memory into one trace (bumping its
importance each time it recurs), then **decay** drops traces whose combined
recency+importance score falls below a threshold at a fixed, injected "now".
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

# Make `src.shared` importable when run as
# `python src/36_memory_consolidation_decay/memory_consolidation_decay.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


@dataclass
class MemoryTrace:
    """A consolidated memory: text, how many times it recurred, and importance."""

    text: str
    last_tick: int
    occurrences: int = 1
    importance: float = 0.3


RAW_EPISODES: tuple[tuple[str, int], ...] = (
    ("user asked about password reset", 1),
    ("user viewed the dashboard", 2),
    ("user asked about password reset", 4),
    ("user asked about password reset", 7),
    ("user viewed the dashboard", 8),
    ("user mentioned they like dark mode", 3),
)

NOW_TICK = 10
DECAY_HALF_LIFE = 5
IMPORTANCE_BUMP_PER_REPEAT = 0.2
DECAY_THRESHOLD = 0.35


def consolidate(episodes: tuple[tuple[str, int], ...]) -> list[MemoryTrace]:
    """Merge repeated occurrences of the same text into one trace.

    Each repeat bumps importance (repetition signals it matters) and refreshes
    ``last_tick`` to the most recent occurrence.
    """
    traces: dict[str, MemoryTrace] = {}
    for text, tick in episodes:
        if text not in traces:
            traces[text] = MemoryTrace(text=text, last_tick=tick)
        else:
            trace = traces[text]
            trace.occurrences += 1
            trace.last_tick = max(trace.last_tick, tick)
            trace.importance = min(1.0, trace.importance + IMPORTANCE_BUMP_PER_REPEAT)
    return list(traces.values())


def _recency(trace: MemoryTrace, now_tick: int) -> float:
    age = max(now_tick - trace.last_tick, 0)
    return max(0.0, 1.0 - age / DECAY_HALF_LIFE)


def decay(
    traces: list[MemoryTrace], now_tick: int, threshold: float
) -> tuple[list[MemoryTrace], list[MemoryTrace]]:
    """Split traces into ``(kept, dropped)`` by a recency+importance score."""
    kept: list[MemoryTrace] = []
    dropped: list[MemoryTrace] = []
    for trace in traces:
        score = 0.5 * _recency(trace, now_tick) + 0.5 * trace.importance
        target = kept if score >= threshold else dropped
        target.append(trace)
        logger.info(
            "trace %r score=%.3f -> %s",
            trace.text,
            score,
            "kept" if score >= threshold else "dropped",
        )
    return kept, dropped


def main() -> None:
    print(f"raw episodes: {len(RAW_EPISODES)}")

    consolidated = consolidate(RAW_EPISODES)
    print(f"consolidated into {len(consolidated)} trace(s):")
    for trace in sorted(consolidated, key=lambda t: t.text):
        print(
            f"  text={trace.text!r} occurrences={trace.occurrences} "
            f"last_tick={trace.last_tick} importance={trace.importance}"
        )

    kept, dropped = decay(consolidated, NOW_TICK, DECAY_THRESHOLD)
    print(f"decay pass (now_tick={NOW_TICK}, threshold={DECAY_THRESHOLD}):")
    print(f"  kept={sorted(t.text for t in kept)}")
    print(f"  dropped={sorted(t.text for t in dropped)}")

    print("=== TRACK4 MODULE 36: MEMORY CONSOLIDATION & DECAY COMPLETE ===")


if __name__ == "__main__":
    main()
