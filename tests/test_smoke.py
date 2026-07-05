"""Smoke tests for Agent Lab modules that do not require API keys."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"


def _run_script(relative: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / relative)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_state_basics_runs():
    result = _run_script("src/01_state_basics/hello_world.py")
    assert result.returncode == 0
    assert "hello" in result.stdout


def test_langgraph_basics_runs():
    result = _run_script("src/02_langgraph_basics/basic_graph.py")
    assert result.returncode == 0
    assert "start" in result.stdout


def test_routing_runs():
    result = _run_script("src/04_routing_and_branches/router.py")
    assert result.returncode == 0
    assert "blocker" in result.stdout


def test_tools_runs():
    result = _run_script("src/05_tools/mock_tool.py")
    assert result.returncode == 0
    assert "Slack sent" in result.stdout


def test_memory_basics_runs():
    result = _run_script("src/06_memory_basics/memory.py")
    assert result.returncode == 0
    assert "login" in result.stdout


def test_qdrant_placeholder_runs():
    result = _run_script("src/07_qdrant_integration/mock_qdrant.py")
    assert result.returncode == 0
    assert "Qdrant placeholder" in result.stdout


def test_neo4j_placeholder_runs():
    result = _run_script("src/08_graph_memory_neo4j/mock_graph.py")
    assert result.returncode == 0
    assert "Neo4j placeholder" in result.stdout


def test_multi_agent_runs():
    result = _run_script("src/09_multi_agent_systems/agents.py")
    assert result.returncode == 0
    assert "done" in result.stdout


def test_brain_simulation_runs():
    result = _run_script("src/10_full_brain_simulation/brain.py")
    assert result.returncode == 0
    assert "Full Brain Simulation" in result.stdout


def test_shared_state_typeddict():
    spec = importlib.util.spec_from_file_location(
        "shared_state", SRC / "shared" / "state.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert "message" in module.State.__annotations__


def test_llm_nodes_requires_api_key():
    """03_llm_nodes must fail gracefully when OPENAI_API_KEY is unset."""
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "src/03_llm_nodes/llm_node.py")],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "OPENAI_API_KEY" in result.stderr or "credentials" in result.stderr.lower()
