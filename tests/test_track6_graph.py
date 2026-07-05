"""Smoke tests for Track 6 (Graph Intelligence) modules 43-47.

Mirrors ``tests/test_smoke.py``: each script is run via subprocess with no
environment configured (offline-first), asserting exit 0 and a stable
substring in stdout.
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


def test_neo4j_basics_runs_offline_fallback():
    """43 must use the InMemoryGraphStore fallback when NEO4J_URI is unset."""
    result = _run_script("src/43_neo4j_basics/neo4j_basics.py")
    assert result.returncode == 0
    assert "MODULE 43: NEO4J BASICS COMPLETE (offline fallback)" in result.stdout
    assert "rel alice -[WORKS_AT]-> acme" in result.stdout


def test_graph_modeling_cypher_runs():
    result = _run_script("src/44_graph_modeling_cypher/graph_modeling_cypher.py")
    assert result.returncode == 0
    assert "MODULE 44: GRAPH MODELING & CYPHER COMPLETE" in result.stdout
    assert "dana -[OWNS]-> payments" in result.stdout


def test_dependency_analysis_runs():
    result = _run_script("src/45_dependency_analysis/dependency_analysis.py")
    assert result.returncode == 0
    assert "MODULE 45: DEPENDENCY ANALYSIS COMPLETE" in result.stdout
    assert "package_dag topological_order=['db', 'auth', 'api', 'webapp']" in result.stdout
    assert "task_graph detected_cycle=" in result.stdout


def test_root_cause_analysis_runs():
    result = _run_script("src/46_root_cause_analysis/root_cause_analysis.py")
    assert result.returncode == 0
    assert "MODULE 46: ROOT CAUSE ANALYSIS COMPLETE" in result.stdout
    assert "most_likely_root=database" in result.stdout


def test_organizational_graph_runs():
    result = _run_script("src/47_organizational_graph/organizational_graph.py")
    assert result.returncode == 0
    assert "MODULE 47: ORGANIZATIONAL GRAPH COMPLETE" in result.stdout
    assert "who_owns(checkout)=['hank']" in result.stdout
