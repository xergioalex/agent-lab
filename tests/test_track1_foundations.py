"""Smoke tests for Track 1 — Foundations modules (11-14).

Mirrors the style of ``tests/test_smoke.py``: run each module's script via
subprocess, assert a clean exit and a stable substring in stdout. No API keys
or external services are required — every module here is offline-first.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_script(relative: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / relative)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_graph_branching_runs():
    result = _run_script("src/11_graph_branching/branching.py")
    assert result.returncode == 0
    assert "category=bug" in result.stdout
    assert "category=feature" in result.stdout
    assert "category=question" in result.stdout
    assert "category=general" in result.stdout
    assert "=== TRACK1 MODULE 11: GRAPH BRANCHING COMPLETE ===" in result.stdout


def test_parallel_execution_runs():
    result = _run_script("src/12_parallel_execution/parallel.py")
    assert result.returncode == 0
    assert "total_words=24" in result.stdout
    assert "=== TRACK1 MODULE 12: PARALLEL EXECUTION COMPLETE ===" in result.stdout


def test_async_nodes_runs():
    result = _run_script("src/13_async_nodes/async_nodes.py")
    assert result.returncode == 0
    assert "speedup: async was faster than sync = True" in result.stdout
    assert "=== TRACK1 MODULE 13: ASYNC NODES COMPLETE ===" in result.stdout


def test_error_handling_runs():
    result = _run_script("src/14_error_handling/error_handling.py")
    assert result.returncode == 0
    assert "scenario=recovers outcome=success attempts=3" in result.stdout
    assert (
        "scenario=circuit_breaker outcome=fallback attempts=2" in result.stdout
    )
    assert "=== TRACK1 MODULE 14: ERROR HANDLING COMPLETE ===" in result.stdout
