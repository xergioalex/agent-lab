"""Smoke tests for Track 2 — LLM Engineering modules (15-20).

Every module is offline-first: no API key or external service is required.
Each test runs the module's script via subprocess and asserts a stable,
deterministic substring in stdout, mirroring `tests/test_smoke.py`.
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


def test_chat_models_runs():
    result = _run_script("src/15_chat_models/chat_turn.py")
    assert result.returncode == 0
    assert "=== TRACK2 MODULE 15: CHAT MODELS COMPLETE ===" in result.stdout


def test_structured_outputs_runs():
    result = _run_script("src/16_structured_outputs/structured_output.py")
    assert result.returncode == 0
    assert "attempts=2" in result.stdout
    assert "=== TRACK2 MODULE 16: STRUCTURED OUTPUTS COMPLETE ===" in result.stdout


def test_function_calling_runs():
    result = _run_script("src/17_function_calling/tool_loop.py")
    assert result.returncode == 0
    assert "tool_calls=['get_weather', 'send_slack']" in result.stdout
    assert "=== TRACK2 MODULE 17: FUNCTION CALLING COMPLETE ===" in result.stdout


def test_prompt_engineering_runs():
    result = _run_script("src/18_prompt_engineering/prompt_engineering.py")
    assert result.returncode == 0
    assert "CATEGORY: bug | ACTION: escalate to engineering" in result.stdout
    assert "=== TRACK2 MODULE 18: PROMPT ENGINEERING COMPLETE ===" in result.stdout


def test_context_engineering_runs():
    result = _run_script("src/19_context_engineering/context_budget.py")
    assert result.returncode == 0
    assert "condensed_count=9" in result.stdout
    assert "=== TRACK2 MODULE 19: CONTEXT ENGINEERING COMPLETE ===" in result.stdout


def test_model_routing_runs():
    result = _run_script("src/20_model_routing/model_router.py")
    assert result.returncode == 0
    assert "tier=cheap" in result.stdout
    assert "tier=capable" in result.stdout
    assert "=== TRACK2 MODULE 20: MODEL ROUTING COMPLETE ===" in result.stdout
