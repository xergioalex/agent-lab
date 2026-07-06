"""Smoke tests for Track 8 — Production modules (53-58).

Mirrors the style of ``tests/test_smoke.py``: run each module's script via
subprocess, assert a clean exit and a stable substring in stdout. No API keys
or external services are required — every module here is offline-first.
"""

from tests.conftest import run_module


def test_observability_runs():
    result = run_module("53_observability")
    assert result.returncode == 0
    assert "run-tree:" in result.stdout
    assert "metrics: nodes=3" in result.stdout
    assert "=== MODULE 53: OBSERVABILITY COMPLETE ===" in result.stdout


def test_evaluations_runs():
    result = run_module("54_evaluations")
    assert result.returncode == 0
    assert "=== SCORECARD ===" in result.stdout
    assert "total=5 passed=4 pass_rate=80.0%" in result.stdout
    assert "=== MODULE 54: EVALUATIONS COMPLETE ===" in result.stdout


def test_testing_agents_runs():
    result = run_module("55_testing_agents")
    assert result.returncode == 0
    assert "snapshots_stable_across_runs=True" in result.stdout
    assert "[PASS] has_at_least_one_message" in result.stdout
    assert "=== MODULE 55: TESTING AGENTS COMPLETE ===" in result.stdout


def test_security_runs():
    result = run_module("56_security")
    assert result.returncode == 0
    assert "NEUTRALIZED" in result.stdout
    assert "REJECTED (validation)" in result.stdout
    assert "=== MODULE 56: SECURITY COMPLETE ===" in result.stdout


def test_cost_and_multitenancy_runs():
    result = run_module("57_cost_and_multitenancy")
    assert result.returncode == 0
    assert "isolated=True" in result.stdout
    assert "=== COST REPORT ===" in result.stdout
    assert "=== MODULE 57: COST AND MULTITENANCY COMPLETE ===" in result.stdout


def test_deployment_runs():
    result = run_module("58_deployment")
    assert result.returncode == 0
    assert "[PASS] compose_defines_qdrant" in result.stdout
    assert "[PASS] ci_runs_offline_pytest" in result.stdout
    assert "=== MODULE 58: DEPLOYMENT COMPLETE ===" in result.stdout
