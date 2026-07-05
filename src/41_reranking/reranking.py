"""41 — Reranking: two-stage retrieve-then-rerank.

Stage 1 (first-stage retrieval) uses the cheap, fast bi-encoder path from
modules 37/38: embed query and candidates independently, rank by cosine
similarity. Stage 2 (reranking) uses a **cross-encoder-style** scorer: a
function of the (query, candidate) *pair* jointly, which is more accurate but
too expensive to run over the whole corpus -- so it only re-scores the small
candidate set stage 1 already narrowed down.

The cross-encoder here is a deterministic, offline heuristic (exact-phrase
containment + token overlap + a length-normalization term) standing in for a
real cross-encoder model, which is not installed and would need a key/service
in production. The mechanics -- narrow with a cheap retriever, refine with an
expensive scorer -- are the same either way.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/41_reranking/reranking.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryVectorStore, SearchResult, get_logger  # noqa: E402

logger = get_logger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# A corpus where the bi-encoder's bag-of-words similarity is a noisy proxy:
# doc-decoy stuffs the query's exact keywords ("request", "HR portal") into
# unrelated sub-topics (password resets, IT accounts, training), which drives
# its cosine score above doc-precise -- the one document that actually
# answers the question. The cross-encoder's phrase/coverage/length signals
# see through the keyword stuffing and correctly promote doc-precise.
CORPUS: list[tuple[str, str]] = [
    ("doc-precise", "To request vacation, go through the HR portal at least two weeks in advance."),
    (
        "doc-decoy",
        "The HR portal lets you request vacation balances, request HR portal "
        "password resets, request HR portal IT accounts, and request HR "
        "portal training through the portal.",
    ),
    ("doc-oncall", "The on-call engineer rotates weekly and monitors the incident channel."),
    ("doc-standup", "Daily standups happen every morning to sync on blockers in the team channel."),
]

QUERY = "request vacation through the HR portal"
FIRST_STAGE_K = 4


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def first_stage_retrieve(query: str, corpus: list[tuple[str, str]], k: int) -> list[SearchResult]:
    """Cheap bi-encoder retrieval: query and candidates embedded independently."""
    store = InMemoryVectorStore()
    ids, texts = zip(*corpus)
    store.add_texts(list(texts), ids=list(ids))
    return store.similarity_search(query, k=k)


def cross_encoder_score(query: str, text: str) -> float:
    """Deterministic cross-encoder-style heuristic score for a (query, text) pair.

    A real cross-encoder feeds ``[query, text]`` through one transformer so
    every query token can attend to every candidate token jointly -- much
    more accurate than comparing two independently-computed vectors, but too
    slow to run over an entire corpus. This heuristic approximates that joint
    view with three pair-level signals a bi-encoder's cosine score cannot see:
    exact phrase containment, query-token coverage, and a length-fit penalty.
    """
    query_tokens = _tokenize(query)
    text_tokens = _tokenize(text)
    if not query_tokens or not text_tokens:
        return 0.0
    coverage = sum(1 for token in query_tokens if token in text_tokens) / len(query_tokens)
    phrase_bonus = 1.0 if query.lower().rstrip("?") in text.lower() else 0.0
    length_fit = 1.0 / (1.0 + abs(len(text_tokens) - len(query_tokens)) * 0.1)
    return coverage * 2.0 + phrase_bonus * 1.0 + length_fit * 0.5


def rerank(query: str, candidates: list[SearchResult]) -> list[tuple[str, float]]:
    """Re-score first-stage candidates with the cross-encoder-style heuristic."""
    scored = [
        (result.document.id, cross_encoder_score(query, result.document.text))
        for result in candidates
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


def main() -> None:
    print(f"query={QUERY!r}")

    first_stage = first_stage_retrieve(QUERY, CORPUS, FIRST_STAGE_K)
    first_stage_ranking = [result.document.id for result in first_stage]
    print("--- stage 1: bi-encoder first pass ---")
    for result in first_stage:
        print(f"id={result.document.id} bi_encoder_score={result.score:.4f}")

    reranked = rerank(QUERY, first_stage)
    reranked_ranking = [doc_id for doc_id, _ in reranked]
    print("--- stage 2: cross-encoder-style rerank ---")
    for doc_id, score in reranked:
        print(f"id={doc_id} cross_encoder_score={score:.4f}")

    print(f"first_stage_rank={first_stage_ranking}")
    print(f"reranked_rank={reranked_ranking}")

    deltas = {
        doc_id: first_stage_ranking.index(doc_id) - reranked_ranking.index(doc_id)
        for doc_id in reranked_ranking
    }
    for doc_id, delta in deltas.items():
        print(f"delta id={doc_id} positions_gained={delta}")

    top_changed = first_stage_ranking[0] != reranked_ranking[0]
    print(f"top_changed_after_rerank={top_changed}")

    print("=== TRACK5 MODULE 41: RERANKING COMPLETE ===")


if __name__ == "__main__":
    main()
