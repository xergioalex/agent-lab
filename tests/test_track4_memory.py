"""Smoke tests for Track 4 -- Memory modules (29-36).

Mirrors the style of ``tests/test_smoke.py``: run each module's script via
subprocess, assert a clean exit and a stable substring in stdout. No API keys
or external services are required -- every module here is offline-first and
uses fixed clocks / seeded data so output is deterministic.
"""

from tests.conftest import run_module


def test_conversation_memory_runs():
    result = run_module("29_conversation_memory")
    assert result.returncode == 0
    assert "buffer: 6 message(s) retained (all)" in result.stdout
    assert "window(n=3): 3 message(s) retained" in result.stdout
    assert "summary(n=3):" in result.stdout
    assert "=== TRACK4 MODULE 29: CONVERSATION MEMORY COMPLETE ===" in result.stdout


def test_episodic_memory_runs():
    result = run_module("30_episodic_memory")
    assert result.returncode == 0
    assert "replay (ascending):" in result.stdout
    assert "tick=1 id=1 event='user logged in'" in result.stdout
    assert "tick=4 id=4 event='user logged out'" in result.stdout
    assert "between(2,3): ['user opened dashboard', 'user exported report']" in result.stdout
    assert "=== TRACK4 MODULE 30: EPISODIC MEMORY COMPLETE ===" in result.stdout


def test_semantic_memory_runs():
    result = run_module("31_semantic_memory")
    assert result.returncode == 0
    assert "query='What is the capital of France?'" in result.stdout
    assert "fact='Paris is the capital of France.'" in result.stdout
    assert "=== TRACK4 MODULE 31: SEMANTIC MEMORY COMPLETE ===" in result.stdout


def test_procedural_memory_runs():
    result = run_module("32_procedural_memory")
    assert result.returncode == 0
    assert "matched procedure='reset_password'" in result.stdout
    assert "matched procedure='file_bug_report'" in result.stdout
    assert "=== TRACK4 MODULE 32: PROCEDURAL MEMORY COMPLETE ===" in result.stdout


def test_memory_writer_runs():
    result = run_module("33_memory_writer")
    assert result.returncode == 0
    assert "extracted 5 candidate(s)" in result.stdout
    assert "conversation: 2 item(s)" in result.stdout
    assert "episodic: 1 item(s)" in result.stdout
    assert "semantic: 1 item(s)" in result.stdout
    assert "procedural: 1 item(s)" in result.stdout
    assert "=== TRACK4 MODULE 33: MEMORY WRITER COMPLETE ===" in result.stdout


def test_memory_retrieval_runs():
    result = run_module("34_memory_retrieval")
    assert result.returncode == 0
    assert "query='How do I reset my password?'" in result.stdout
    assert "assembled context (budget=160 chars):" in result.stdout
    assert "[conversation] User asked how to reset their password." in result.stdout
    assert "=== TRACK4 MODULE 34: MEMORY RETRIEVAL COMPLETE ===" in result.stdout


def test_memory_scoring_runs():
    result = run_module("35_memory_scoring")
    assert result.returncode == 0
    assert "now_tick=10" in result.stdout
    assert "total=0.423" in result.stdout
    assert "=== TRACK4 MODULE 35: MEMORY SCORING COMPLETE ===" in result.stdout


def test_memory_consolidation_decay_runs():
    result = run_module("36_memory_consolidation_decay")
    assert result.returncode == 0
    assert "consolidated into 3 trace(s):" in result.stdout
    assert (
        "kept=['user asked about password reset', 'user viewed the dashboard']"
        in result.stdout
    )
    assert "dropped=['user mentioned they like dark mode']" in result.stdout
    assert (
        "=== TRACK4 MODULE 36: MEMORY CONSOLIDATION & DECAY COMPLETE ===" in result.stdout
    )
