"""54 — Evaluations: a golden-set eval harness with pluggable scorers.

Demonstrates the shape every production eval harness shares: a fixed **golden
set** of (input, expected) pairs, one or more **scorers** that grade a single
run against its expected output, and an aggregator that turns per-case scores
into a pass rate. The system under test here is a small, deliberately naive
sentiment classifier — naive enough to fail on sarcasm, which is the point:
evals exist to *find* exactly that kind of gap before it reaches production.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# Make `src.shared` importable when run as `python src/54_evaluations/evaluations.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)

# --------------------------------------------------------------------------- #
# System under test: a naive, offline sentiment classifier.
# --------------------------------------------------------------------------- #

_POSITIVE_WORDS = {"love", "great", "good", "excellent", "happy", "thanks"}
_NEGATIVE_WORDS = {"hate", "bad", "terrible", "broken", "awful", "angry"}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z']+", text.lower()))


def classify_sentiment(text: str) -> str:
    """Lexicon-based sentiment classifier — intentionally simple.

    Misses sarcasm and mixed signals on purpose: the eval harness exists to
    surface that gap with a number, not to hide it.
    """
    tokens = _words(text)
    is_positive = bool(tokens & _POSITIVE_WORDS)
    is_negative = bool(tokens & _NEGATIVE_WORDS)
    if is_positive and not is_negative:
        return "positive"
    if is_negative and not is_positive:
        return "negative"
    return "neutral"


# --------------------------------------------------------------------------- #
# Golden set
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class GoldenCase:
    """One golden-set example: an input and its expected label."""

    input: str
    expected: str


GOLDEN_SET: tuple[GoldenCase, ...] = (
    GoldenCase("I love the new dashboard, great work!", "positive"),
    GoldenCase("This update is terrible and broken.", "negative"),
    GoldenCase("The meeting is scheduled for 3pm.", "neutral"),
    GoldenCase("I hate how this turned out; it's really bad.", "negative"),
    GoldenCase("Great, another bug crashed my session. Thanks a lot.", "negative"),
)
"""The last case is sarcastic: the naive classifier reads the surface words
('great', 'thanks') as positive, but a human labels it negative. This is the
expected, demonstrated failure of a lexicon-based scorer."""


# --------------------------------------------------------------------------- #
# Scorers
# --------------------------------------------------------------------------- #

Scorer = Callable[[str, str], float]


def exact_match_scorer(expected: str, actual: str) -> float:
    """1.0 if the predicted label matches exactly, else 0.0."""
    return 1.0 if expected == actual else 0.0


def polarity_detected_scorer(expected: str, actual: str) -> float:
    """Partial credit: did the classifier at least detect *some* charge?

    Rewards detecting non-neutral sentiment when charged sentiment is
    expected (or correctly staying neutral when neutral is expected) —
    even if the exact polarity is wrong. Combined with the exact-match
    scorer this shows why relying on a single lenient scorer can mask
    real regressions (see README "Common Mistakes").
    """
    if expected == "neutral":
        return 1.0 if actual == "neutral" else 0.0
    return 1.0 if actual != "neutral" else 0.0


SCORERS: tuple[tuple[str, Scorer], ...] = (
    ("exact_match", exact_match_scorer),
    ("polarity_detected", polarity_detected_scorer),
)

PASS_THRESHOLD = 0.75


@dataclass(frozen=True)
class EvalResult:
    """The scored outcome for a single golden case."""

    case: GoldenCase
    actual: str
    scores: dict[str, float]

    @property
    def composite(self) -> float:
        return sum(self.scores.values()) / len(self.scores)

    @property
    def passed(self) -> bool:
        return self.composite >= PASS_THRESHOLD


def run_eval(golden_set: tuple[GoldenCase, ...]) -> list[EvalResult]:
    """Run the system under test against every golden case and score it."""
    results: list[EvalResult] = []
    for case in golden_set:
        actual = classify_sentiment(case.input)
        scores = {name: scorer(case.expected, actual) for name, scorer in SCORERS}
        result = EvalResult(case=case, actual=actual, scores=scores)
        logger.info(
            "case=%r expected=%s actual=%s composite=%.2f",
            case.input,
            case.expected,
            actual,
            result.composite,
        )
        results.append(result)
    return results


def print_scorecard(results: list[EvalResult]) -> None:
    for result in results:
        status = "pass" if result.passed else "fail"
        print(
            f"case={result.case.input!r} expected={result.case.expected} "
            f"actual={result.actual} composite={result.composite:.2f} {status}"
        )
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = 100.0 * passed / total if total else 0.0
    print("=== SCORECARD ===")
    print(f"total={total} passed={passed} pass_rate={pass_rate:.1f}%")


def main() -> None:
    results = run_eval(GOLDEN_SET)
    print_scorecard(results)
    print("=== MODULE 54: EVALUATIONS COMPLETE ===")


if __name__ == "__main__":
    main()
