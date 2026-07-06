"""Smoke tests for Track 1 — Foundations modules (11-14).

Mirrors the style of ``tests/test_smoke.py``: run each module's script via
subprocess, assert a clean exit and a stable substring in stdout. No API keys
or external services are required — every module here is offline-first.
"""

from tests.conftest import run_module


def test_graph_branching_runs():
    result = run_module("11_graph_branching")
    assert result.returncode == 0
    assert "category=bug" in result.stdout
    assert "category=feature" in result.stdout
    assert "category=question" in result.stdout
    assert "category=general" in result.stdout
    assert "=== TRACK1 MODULE 11: GRAPH BRANCHING COMPLETE ===" in result.stdout


def test_parallel_execution_runs():
    result = run_module("12_parallel_execution")
    assert result.returncode == 0
    assert "total_words=24" in result.stdout
    assert "=== TRACK1 MODULE 12: PARALLEL EXECUTION COMPLETE ===" in result.stdout


def test_async_nodes_runs():
    result = run_module("13_async_nodes")
    assert result.returncode == 0
    assert "speedup: async was faster than sync = True" in result.stdout
    assert "=== TRACK1 MODULE 13: ASYNC NODES COMPLETE ===" in result.stdout


def test_error_handling_runs():
    result = run_module("14_error_handling")
    assert result.returncode == 0
    assert "scenario=recovers outcome=success attempts=3" in result.stdout
    assert (
        "scenario=circuit_breaker outcome=fallback attempts=2" in result.stdout
    )
    assert "=== TRACK1 MODULE 14: ERROR HANDLING COMPLETE ===" in result.stdout
