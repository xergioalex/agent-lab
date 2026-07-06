"""Smoke tests for Track 7 — Multi-Agent modules (48-52).

Mirrors the style of ``tests/test_smoke.py``: run each module's script via
subprocess, assert a clean exit and a stable substring in stdout. No API keys
or external services are required — every module here is offline-first.
"""

from tests.conftest import run_module


def test_agent_collaboration_runs():
    result = run_module("48_agent_collaboration")
    assert result.returncode == 0
    assert "anti-pattern demo: naive writer would drop keys" in result.stdout
    assert "topic='reducers'" in result.stdout
    assert "topic='fan-out'" in result.stdout
    assert "topic='blackboard'" in result.stdout
    assert "=== TRACK7 MODULE 48: AGENT COLLABORATION COMPLETE ===" in result.stdout


def test_negotiation_runs():
    result = run_module("49_negotiation")
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
    result = run_module("50_task_decomposition")
    assert result.returncode == 0
    assert "subtask_count=4" in result.stdout
    assert "subtask_count=3" in result.stdout
    assert "worker result: [design] completed" in result.stdout
    assert "worker result: [draft-proposal] completed" in result.stdout
    assert "=== TRACK7 MODULE 50: TASK DECOMPOSITION COMPLETE ===" in result.stdout


def test_shared_memory_runs():
    result = run_module("51_shared_memory")
    assert result.returncode == 0
    assert "[researcher] posted:" in result.stdout
    assert "[planner] posted:" in result.stdout
    assert "[critic] posted:" in result.stdout
    assert "summary: Blackboard summary --" in result.stdout
    assert "=== TRACK7 MODULE 51: SHARED MEMORY COMPLETE ===" in result.stdout


def test_event_bus_runs():
    result = run_module("52_event_bus")
    assert result.returncode == 0
    assert "research.requested -> researcher_handler: researched reducers" in result.stdout
    assert "draft.requested -> writer_handler: drafted note about reducers" in result.stdout
    assert "Delivered 4 event(s) via the bus." in result.stdout
    assert "=== TRACK7 MODULE 52: EVENT BUS COMPLETE ===" in result.stdout
