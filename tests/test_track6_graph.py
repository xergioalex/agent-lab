"""Smoke tests for Track 6 (Graph Intelligence) modules 43-47.

Mirrors ``tests/test_smoke.py``: each script is run via subprocess with no
environment configured (offline-first), asserting exit 0 and a stable
substring in stdout.
"""

from tests.conftest import run_module


def test_neo4j_basics_runs_offline_fallback():
    """43 must use the InMemoryGraphStore fallback when NEO4J_URI is unset."""
    result = run_module("43_neo4j_basics")
    assert result.returncode == 0
    assert "MODULE 43: NEO4J BASICS COMPLETE (offline fallback)" in result.stdout
    assert "rel alice -[WORKS_AT]-> acme" in result.stdout


def test_graph_modeling_cypher_runs():
    result = run_module("44_graph_modeling_cypher")
    assert result.returncode == 0
    assert "MODULE 44: GRAPH MODELING & CYPHER COMPLETE" in result.stdout
    assert "dana -[OWNS]-> payments" in result.stdout


def test_dependency_analysis_runs():
    result = run_module("45_dependency_analysis")
    assert result.returncode == 0
    assert "MODULE 45: DEPENDENCY ANALYSIS COMPLETE" in result.stdout
    assert "package_dag topological_order=['db', 'auth', 'api', 'webapp']" in result.stdout
    assert "task_graph detected_cycle=" in result.stdout


def test_root_cause_analysis_runs():
    result = run_module("46_root_cause_analysis")
    assert result.returncode == 0
    assert "MODULE 46: ROOT CAUSE ANALYSIS COMPLETE" in result.stdout
    assert "most_likely_root=database" in result.stdout


def test_organizational_graph_runs():
    result = run_module("47_organizational_graph")
    assert result.returncode == 0
    assert "MODULE 47: ORGANIZATIONAL GRAPH COMPLETE" in result.stdout
    assert "who_owns(checkout)=['hank']" in result.stdout
