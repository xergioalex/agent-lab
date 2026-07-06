"""32 -- Procedural Memory: reusable step sequences retrieved by trigger.

Contrasts semantic memory ("knowing that" -- module 31, facts) with procedural
memory ("knowing how" -- this module): named procedures made of ordered
steps, looked up not by a query embedding but by matching a trigger condition
against the request, then applied.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# Make `src.shared` importable when run as `python src/32_procedural_memory/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)


@dataclass
class Procedure:
    """A named, reusable skill: a trigger condition plus ordered steps."""

    name: str
    triggers: tuple[str, ...]
    steps: list[str] = field(default_factory=list)


class ProceduralMemory:
    """Store and retrieve procedures by matching a request against triggers."""

    def __init__(self) -> None:
        self._procedures: dict[str, Procedure] = {}

    def add(self, procedure: Procedure) -> None:
        self._procedures[procedure.name] = procedure
        logger.info(
            "learned procedure %r (%d steps)", procedure.name, len(procedure.steps)
        )

    def retrieve_by_trigger(self, request: str) -> Procedure | None:
        text = request.lower()
        for procedure in self._procedures.values():
            if any(trigger in text for trigger in procedure.triggers):
                return procedure
        return None

    def apply(self, procedure: Procedure) -> list[str]:
        """"Execute" a procedure: here, just render its steps in order."""
        return [f"step {i + 1}: {step}" for i, step in enumerate(procedure.steps)]


PROCEDURES: tuple[Procedure, ...] = (
    Procedure(
        name="reset_password",
        triggers=("reset password", "forgot password", "can't log in"),
        steps=[
            "Verify the user's identity",
            "Send a one-time reset link to the registered email",
            "Prompt the user to set a new password",
            "Invalidate all existing sessions",
        ],
    ),
    Procedure(
        name="file_bug_report",
        triggers=("bug", "crash", "error"),
        steps=[
            "Collect reproduction steps",
            "Attach logs or a screenshot",
            "File the ticket in the tracker",
            "Tag the relevant engineering team",
        ],
    ),
)


def main() -> None:
    memory = ProceduralMemory()
    for procedure in PROCEDURES:
        memory.add(procedure)

    requests = ("I forgot my password and can't log in", "The app crashes on startup")
    for request in requests:
        procedure = memory.retrieve_by_trigger(request)
        print(f"request={request!r}")
        if procedure is None:
            print("  no matching procedure")
            continue
        print(f"  matched procedure={procedure.name!r}")
        for line in memory.apply(procedure):
            print(f"    {line}")

    print("=== TRACK4 MODULE 32: PROCEDURAL MEMORY COMPLETE ===")


if __name__ == "__main__":
    main()
