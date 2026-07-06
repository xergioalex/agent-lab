"""Smoke tests for Track 3 — Agent Engineering modules (21-28).

Mirrors the style of ``tests/test_smoke.py`` and
``tests/test_track1_foundations.py``: run each module's script via
subprocess, assert a clean exit and stable substrings in stdout. Every
module here is offline-first (the `FakeToolCallingModel`) — no API keys or
external services are required.
"""

from tests.conftest import run_module


def test_react_agent_runs():
    result = run_module("21_react_agent")
    assert result.returncode == 0
    assert "act(propose)=['get_weather']" in result.stdout
    assert "act(propose)=['send_slack']" in result.stdout
    assert "reason(final)=" in result.stdout
    assert "Completed using tools" in result.stdout
    assert "=== TRACK3 MODULE 21: REACT AGENT COMPLETE ===" in result.stdout


def test_planner_agent_runs():
    result = run_module("22_planner_agent")
    assert result.returncode == 0
    assert "steps=['get_weather', 'send_slack']" in result.stdout
    assert "steps=['respond_directly']" in result.stdout
    assert "=== TRACK3 MODULE 22: PLANNER AGENT COMPLETE ===" in result.stdout


def test_executor_agent_runs():
    result = run_module("23_executor_agent")
    assert result.returncode == 0
    assert "executed 2 step(s)" in result.stdout
    assert "skipped: no tool for step 'respond_directly'" in result.stdout
    assert "summary=no steps to execute" in result.stdout
    assert "=== TRACK3 MODULE 23: EXECUTOR AGENT COMPLETE ===" in result.stdout


def test_reflection_runs():
    result = run_module("24_reflection")
    assert result.returncode == 0
    assert "revision 1: 'Agents plan and act.'" in result.stdout
    assert "revision 3:" in result.stdout
    assert "iterations=3 verdict=approved" in result.stdout
    assert "=== TRACK3 MODULE 24: REFLECTION COMPLETE ===" in result.stdout


def test_router_agent_runs():
    result = run_module("25_router_agent")
    assert result.returncode == 0
    assert "intent=weather" in result.stdout
    assert "intent=task" in result.stdout
    assert "intent=general" in result.stdout
    assert "=== TRACK3 MODULE 25: ROUTER AGENT COMPLETE ===" in result.stdout


def test_planning_loops_runs():
    result = run_module("26_planning_loops")
    assert result.returncode == 0
    assert "plan completed after 1 replan(s), 4 step(s) executed" in result.stdout
    assert "iteration cap reached (2), 2 step(s) abandoned" in result.stdout
    assert "=== TRACK3 MODULE 26: PLANNING LOOPS COMPLETE ===" in result.stdout


def test_human_in_the_loop_runs():
    result = run_module("27_human_in_the_loop")
    assert result.returncode == 0
    assert "thread=release-1 paused_on=" in result.stdout
    assert "thread=release-1 outcome=\"executed:" in result.stdout
    assert "thread=release-2 outcome='executed (edited): send_slack: notify #leads only'" in result.stdout
    assert "thread=release-3 outcome='rejected: no action taken'" in result.stdout
    assert "=== TRACK3 MODULE 27: HUMAN IN THE LOOP COMPLETE ===" in result.stdout


def test_supervisor_runs():
    result = run_module("28_supervisor")
    assert result.returncode == 0
    assert "[weather_worker]" in result.stdout
    assert "[research_worker]" in result.stdout
    assert "[task_worker]" in result.stdout
    assert "[general_worker]" in result.stdout
    assert "final_answer=\"Aggregated 4 worker result(s):" in result.stdout
    assert "=== TRACK3 MODULE 28: SUPERVISOR COMPLETE ===" in result.stdout
