"""Smoke tests for Track 7 — Multi-Agent modules (48-52).

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


def test_agent_collaboration_runs():
    result = _run_script("src/48_agent_collaboration/collaboration.py")
    assert result.returncode == 0
    assert "anti-pattern demo: naive writer would drop keys" in result.stdout
    assert "topic='reducers'" in result.stdout
    assert "topic='fan-out'" in result.stdout
    assert "topic='blackboard'" in result.stdout
    assert "=== TRACK7 MODULE 48: AGENT COLLABORATION COMPLETE ===" in result.stdout


def test_negotiation_runs():
    result = _run_script("src/49_negotiation/negotiation.py")
    assert result.returncode == 0
    assert (
        "scenario=settles_within_budget Negotiation outcome=deal after 3 round(s): "
        "final offer=110" in result.stdout
    )
    assert (
        "scenario=hits_round_cap Negotiation outcome=no_deal after 5 round(s): "
        "final offer=70" in result.stdout
    )
    assert "=== TRACK7 MODULE 49: NEGOTIATION COMPLETE ===" in result.stdout


def test_task_decomposition_runs():
    result = _run_script("src/50_task_decomposition/decomposition.py")
    assert result.returncode == 0
    assert "subtask_count=4" in result.stdout
    assert "subtask_count=3" in result.stdout
    assert "worker result: [design] completed" in result.stdout
    assert "worker result: [draft-proposal] completed" in result.stdout
    assert "=== TRACK7 MODULE 50: TASK DECOMPOSITION COMPLETE ===" in result.stdout


def test_shared_memory_runs():
    result = _run_script("src/51_shared_memory/blackboard.py")
    assert result.returncode == 0
    assert "[researcher] posted:" in result.stdout
    assert "[planner] posted:" in result.stdout
    assert "[critic] posted:" in result.stdout
    assert "summary: Blackboard summary --" in result.stdout
    assert "=== TRACK7 MODULE 51: SHARED MEMORY COMPLETE ===" in result.stdout


def test_event_bus_runs():
    result = _run_script("src/52_event_bus/event_bus.py")
    assert result.returncode == 0
    assert "research.requested -> researcher_handler: researched reducers" in result.stdout
    assert "draft.requested -> writer_handler: drafted note about reducers" in result.stdout
    assert "Delivered 4 event(s) via the bus." in result.stdout
    assert "=== TRACK7 MODULE 52: EVENT BUS COMPLETE ===" in result.stdout
