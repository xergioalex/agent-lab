"""33 -- Memory Writer: the extract -> classify -> store write pipeline.

A single raw interaction rarely belongs to one memory type. This pipeline
fans a raw interaction out into candidate memory items, classifies each one
(conversation / episodic / semantic / procedural), and routes it to the
matching store -- the "front door" every memory-typed module in this track
(29-32) writes through.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

# Make `src.shared` importable when run as `python src/33_memory_writer/memory_writer.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)

MemoryKind = Literal["conversation", "episodic", "semantic", "procedural"]

RAW_INTERACTION: tuple[str, ...] = (
    "User asked: How do I reset my password?",
    "At tick=12 the user triggered a password reset request.",
    "Fact: password resets invalidate all existing sessions.",
    "Procedure: reset_password -> verify identity, send link, set new password.",
    "Agent replied: I've sent a reset link to your email.",
)


def extract(raw_interaction: tuple[str, ...]) -> list[str]:
    """Split a raw interaction into independent candidate memory items."""
    return [line.strip() for line in raw_interaction if line.strip()]


def classify(candidate: str) -> MemoryKind:
    """Route a candidate to a memory kind using simple, explainable keyword rules."""
    lowered = candidate.lower()
    if "procedure:" in lowered:
        return "procedural"
    if "fact:" in lowered:
        return "semantic"
    if "tick=" in lowered:
        return "episodic"
    return "conversation"


def store(candidates: list[str]) -> dict[MemoryKind, list[str]]:
    """Fan candidates out into per-kind buckets (stand-ins for modules 29-32)."""
    buckets: dict[MemoryKind, list[str]] = {
        "conversation": [],
        "episodic": [],
        "semantic": [],
        "procedural": [],
    }
    for candidate in candidates:
        kind = classify(candidate)
        buckets[kind].append(candidate)
        logger.info("routed candidate to %s memory: %r", kind, candidate)
    return buckets


def main() -> None:
    candidates = extract(RAW_INTERACTION)
    print(f"extracted {len(candidates)} candidate(s)")

    buckets = store(candidates)
    for kind in ("conversation", "episodic", "semantic", "procedural"):
        items = buckets[kind]
        print(f"{kind}: {len(items)} item(s) -> {items}")

    print("=== TRACK4 MODULE 33: MEMORY WRITER COMPLETE ===")


if __name__ == "__main__":
    main()
