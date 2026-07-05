"""Smoke tests for Track 5 — Retrieval / RAG modules (37-42).

Mirrors the style of ``tests/test_smoke.py``: run each module's script via
subprocess, assert a clean exit and a stable substring in stdout. No API keys
or external services are required — every module here is offline-first.
Module 42 specifically exercises the ``InMemoryVectorStore`` fallback path
(``QDRANT_URL`` unset), since ``qdrant-client`` is not installed.
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


def test_embeddings_runs():
    result = _run_script("src/37_embeddings/embeddings.py")
    assert result.returncode == 0
    assert "doc=deploy score=0.3198" in result.stdout
    assert "chunk_size=11" in result.stdout
    assert "chunk_size=45" in result.stdout
    assert "=== TRACK5 MODULE 37: EMBEDDINGS COMPLETE ===" in result.stdout


def test_rag_fundamentals_runs():
    result = _run_script("src/38_rag_fundamentals/rag.py")
    assert result.returncode == 0
    assert "retrieved id=kb-deploy" in result.stdout
    assert "[kb-deploy]" in result.stdout
    assert "=== TRACK5 MODULE 38: RAG FUNDAMENTALS COMPLETE ===" in result.stdout


def test_hybrid_search_runs():
    result = _run_script("src/39_hybrid_search/hybrid.py")
    assert result.returncode == 0
    assert "keyword_buries_relevant_doc=True" in result.stdout
    assert "fusion_recovers_relevant_doc=True" in result.stdout
    assert "=== TRACK5 MODULE 39: HYBRID SEARCH COMPLETE ===" in result.stdout


def test_query_rewriting_runs():
    result = _run_script("src/40_query_rewriting/query_rewriting.py")
    assert result.returncode == 0
    assert "hyde_top id=kb-vacation" in result.stdout
    assert "baseline_top id=kb-deploy" in result.stdout
    assert "=== TRACK5 MODULE 40: QUERY REWRITING COMPLETE ===" in result.stdout


def test_reranking_runs():
    result = _run_script("src/41_reranking/reranking.py")
    assert result.returncode == 0
    assert "first_stage_rank=['doc-decoy', 'doc-precise'" in result.stdout
    assert "reranked_rank=['doc-precise', 'doc-decoy'" in result.stdout
    assert "top_changed_after_rerank=True" in result.stdout
    assert "=== TRACK5 MODULE 41: RERANKING COMPLETE ===" in result.stdout


def test_qdrant_production_offline_fallback_runs():
    """QDRANT_URL is unset in this environment: the InMemoryVectorStore
    fallback path must run green, since qdrant-client is not installed."""
    result = _run_script("src/42_qdrant_production/qdrant_production.py")
    assert result.returncode == 0
    assert "backend=InMemoryVectorStore" in result.stdout
    assert "=== TRACK5 MODULE 42: QDRANT PRODUCTION COMPLETE ===" in result.stdout
