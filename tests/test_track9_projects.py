"""Smoke tests for Track 9 — Final Project Capstones (modules 59-64).

Mirrors the style of ``tests/test_smoke.py``: run each module's script via
subprocess, assert a clean exit and a stable substring in stdout. No API keys
or external services are required — every capstone here is offline-first.
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


def test_personal_assistant_runs():
    result = _run_script("src/59_personal_assistant/assistant.py")
    assert result.returncode == 0
    assert "intent=tool" in result.stdout
    assert "intent=recall" in result.stdout
    assert "intent=chat" in result.stdout
    assert "=== TRACK9 MODULE 59: PERSONAL ASSISTANT COMPLETE ===" in result.stdout


def test_research_agent_runs():
    result = _run_script("src/60_research_agent/research_agent.py")
    assert result.returncode == 0
    assert "revisions=1 critique='coverage sufficient'" in result.stdout
    assert "=== TRACK9 MODULE 60: RESEARCH AGENT COMPLETE ===" in result.stdout


def test_coding_agent_runs():
    result = _run_script("src/61_coding_agent/coding_agent.py")
    assert result.returncode == 0
    assert "tool_calls_made=3" in result.stdout
    assert "=== TRACK9 MODULE 61: CODING AGENT COMPLETE ===" in result.stdout


def test_incident_response_agent_runs():
    result = _run_script("src/62_incident_response_agent/incident_agent.py")
    assert result.returncode == 0
    assert "root_causes=['database']" in result.stdout
    assert "=== TRACK9 MODULE 62: INCIDENT RESPONSE AGENT COMPLETE ===" in result.stdout


def test_company_brain_runs():
    result = _run_script("src/63_company_brain/company_brain.py")
    assert result.returncode == 0
    assert "needed=['graph', 'rag']" in result.stdout
    assert "needed=['memory', 'graph']" in result.stdout
    assert "=== TRACK9 MODULE 63: COMPANY BRAIN COMPLETE ===" in result.stdout


def test_mini_dailybot_brain_runs():
    result = _run_script("src/64_mini_dailybot_brain/mini_dailybot_brain.py")
    assert result.returncode == 0
    assert "needed_subsystems=['graph', 'rag', 'tools']" in result.stdout
    assert "needed_subsystems=['memory']" in result.stdout
    assert "=== TRACK9 MODULE 64: MINI DAILYBOT BRAIN COMPLETE ===" in result.stdout
