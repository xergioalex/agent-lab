"""30 -- Episodic Memory: timestamped event episodes with a fixed clock.

Deepens module 06 (a flat event log) into structured, time-ordered ``Episode``
records: each has a monotonic tick (from an injected clock, never wall-clock),
a description of what happened, and free-form metadata. Demonstrates append +
time-ordered replay + range queries.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/30_episodic_memory/episodic_memory.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


class FixedClock:
    """A deterministic clock: each ``tick()`` call advances by exactly 1.

    Stands in for wall-clock time so episodic timestamps stay reproducible
    across runs and machines.
    """

    def __init__(self, start: int = 0) -> None:
        self._now = start

    def tick(self) -> int:
        self._now += 1
        return self._now


@dataclass
class Episode:
    """A single timestamped event: what happened, when, with what context."""

    episode_id: int
    tick: int
    event: str
    metadata: dict[str, Any] = field(default_factory=dict)


class EpisodicMemory:
    """Append-only, time-ordered event log."""

    def __init__(self, clock: FixedClock) -> None:
        self._clock = clock
        self._episodes: list[Episode] = []

    def append(self, event: str, **metadata: Any) -> Episode:
        episode = Episode(
            episode_id=len(self._episodes) + 1,
            tick=self._clock.tick(),
            event=event,
            metadata=metadata,
        )
        self._episodes.append(episode)
        logger.info(
            "recorded episode #%d at tick=%d: %s", episode.episode_id, episode.tick, event
        )
        return episode

    def replay(self, *, descending: bool = False) -> list[Episode]:
        """Return all episodes in time order (ascending by default)."""
        return sorted(self._episodes, key=lambda e: e.tick, reverse=descending)

    def between(self, start_tick: int, end_tick: int) -> list[Episode]:
        """Episodes whose tick falls within ``[start_tick, end_tick]``."""
        return [e for e in self._episodes if start_tick <= e.tick <= end_tick]


def main() -> None:
    clock = FixedClock(start=0)
    memory = EpisodicMemory(clock)

    memory.append("user logged in", user="alice")
    memory.append("user opened dashboard", user="alice")
    memory.append("user exported report", user="alice", report="Q1-sales")
    memory.append("user logged out", user="alice")

    print("replay (ascending):")
    for ep in memory.replay():
        print(f"  tick={ep.tick} id={ep.episode_id} event={ep.event!r} meta={ep.metadata}")

    print("replay (descending):")
    for ep in memory.replay(descending=True):
        print(f"  tick={ep.tick} id={ep.episode_id} event={ep.event!r}")

    windowed = memory.between(2, 3)
    print(f"between(2,3): {[e.event for e in windowed]}")

    print("=== TRACK4 MODULE 30: EPISODIC MEMORY COMPLETE ===")


if __name__ == "__main__":
    main()
