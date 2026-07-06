"""Smoke tests for Track 2 — LLM Engineering modules (15-20).

Every module is offline-first: no API key or external service is required.
Each test runs the module's script via subprocess and asserts a stable,
deterministic substring in stdout, mirroring `tests/test_smoke.py`.
"""

from tests.conftest import run_module


def test_chat_models_runs():
    result = run_module("15_chat_models")
    assert result.returncode == 0
    assert "=== TRACK2 MODULE 15: CHAT MODELS COMPLETE ===" in result.stdout


def test_structured_outputs_runs():
    result = run_module("16_structured_outputs")
    assert result.returncode == 0
    assert "attempts=2" in result.stdout
    assert "=== TRACK2 MODULE 16: STRUCTURED OUTPUTS COMPLETE ===" in result.stdout


def test_function_calling_runs():
    result = run_module("17_function_calling")
    assert result.returncode == 0
    assert "tool_calls=['get_weather', 'send_slack']" in result.stdout
    assert "=== TRACK2 MODULE 17: FUNCTION CALLING COMPLETE ===" in result.stdout


def test_prompt_engineering_runs():
    result = run_module("18_prompt_engineering")
    assert result.returncode == 0
    assert "CATEGORY: bug | ACTION: escalate to engineering" in result.stdout
    assert "=== TRACK2 MODULE 18: PROMPT ENGINEERING COMPLETE ===" in result.stdout


def test_context_engineering_runs():
    result = run_module("19_context_engineering")
    assert result.returncode == 0
    assert "condensed_count=9" in result.stdout
    assert "=== TRACK2 MODULE 19: CONTEXT ENGINEERING COMPLETE ===" in result.stdout


def test_model_routing_runs():
    result = run_module("20_model_routing")
    assert result.returncode == 0
    assert "tier=cheap" in result.stdout
    assert "tier=capable" in result.stdout
    assert "=== TRACK2 MODULE 20: MODEL ROUTING COMPLETE ===" in result.stdout
