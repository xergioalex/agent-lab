"""Smoke tests for Agent Lab on-ramp modules (01-10)."""

import importlib.util

from tests.conftest import REPO_ROOT, offline_env, run_module


def test_state_basics_runs():
    result = run_module("01_state_basics")
    assert result.returncode == 0, result.stderr
    assert "hello" in result.stdout
    assert "MODULE 01" in result.stdout


def test_langgraph_basics_runs():
    result = run_module("02_langgraph_basics")
    assert result.returncode == 0, result.stderr
    assert "start" in result.stdout
    assert "MODULE 02" in result.stdout


def test_llm_nodes_runs_offline():
    result = run_module("03_llm_nodes")
    assert result.returncode == 0, result.stderr
    assert "MODULE 03" in result.stdout
    assert "offline-fake" in result.stdout or "openai" in result.stdout


def test_routing_runs():
    result = run_module("04_routing_and_branches")
    assert result.returncode == 0, result.stderr
    assert "blocker" in result.stdout
    assert "MODULE 04" in result.stdout


def test_tools_runs():
    result = run_module("05_tools")
    assert result.returncode == 0, result.stderr
    assert "Slack sent" in result.stdout
    assert "MODULE 05" in result.stdout


def test_memory_basics_runs():
    result = run_module("06_memory_basics")
    assert result.returncode == 0, result.stderr
    assert "login" in result.stdout
    assert "MODULE 06" in result.stdout


def test_qdrant_integration_runs():
    result = run_module("07_qdrant_integration")
    assert result.returncode == 0, result.stderr
    assert "MODULE 07" in result.stdout
    assert "indexed=3" in result.stdout


def test_graph_memory_neo4j_runs():
    result = run_module("08_graph_memory_neo4j")
    assert result.returncode == 0, result.stderr
    assert "MODULE 08" in result.stdout
    assert "Engineering led by Bob" in result.stdout


def test_multi_agent_runs():
    result = run_module("09_multi_agent_systems")
    assert result.returncode == 0, result.stderr
    assert "done" in result.stdout
    assert "MODULE 09" in result.stdout


def test_brain_simulation_runs():
    result = run_module("10_full_brain_simulation")
    assert result.returncode == 0, result.stderr
    assert "Full Brain Simulation" in result.stdout
    assert "MODULE 10" in result.stdout


def test_shared_state_typeddict():
    spec = importlib.util.spec_from_file_location(
        "shared_state", REPO_ROOT / "src" / "shared" / "state.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert "message" in module.State.__annotations__
