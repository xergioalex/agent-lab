"""Shared pytest helpers for Agent Lab module smoke tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Keys that activate real backends — tests must run offline regardless of shell .env.
_OFFLINE_UNSET = (
    "OPENAI_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "NEO4J_URI",
    "NEO4J_PASSWORD",
)


def offline_env() -> dict[str, str]:
    """Return a copy of os.environ with optional-backend keys removed."""
    env = os.environ.copy()
    for key in _OFFLINE_UNSET:
        env.pop(key, None)
    return env


def run_module(module_dir: str) -> subprocess.CompletedProcess:
    """Run ``src/<module_dir>/main.py`` with an offline environment."""
    script = REPO_ROOT / "src" / module_dir / "main.py"
    return subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
        env=offline_env(),
    )
