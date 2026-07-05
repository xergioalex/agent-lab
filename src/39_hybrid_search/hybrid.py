"""39 — Hybrid Search: dense embeddings + keyword scoring, fused by rank.

Combines the dense (embedding) retriever from modules 37/38 with a pure-Python
keyword/BM25-style scorer, then fuses both rankings with Reciprocal Rank Fusion
(RRF). Shows a query where neither signal alone finds the best document, but
the fused ranking does. Fully offline: no external search engine, no numpy.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/39_hybrid_search/hybrid.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryVectorStore, get_logger  # noqa: E402

logger = get_logger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# A corpus engineered so keyword search nails the exact error code but misses
# the paraphrase, while dense search catches the paraphrase but dilutes the
# exact code across many shared words. Fusion recovers both.
CORPUS: list[tuple[str, str]] = [
    ("doc-code", "Error ERR_429 means the rate limiter rejected the request; retry with backoff."),
    ("doc-paraphrase", "When the API throttles you because of too many requests, wait and try again later."),
    ("doc-oncall", "The on-call engineer rotates weekly and monitors the incident channel."),
    ("doc-standup", "Daily standups happen every morning to sync on blockers in the team channel."),
]

QUERY = "What does ERR_429 mean and what should I do about rate limiting?"


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def keyword_score(query: str, text: str) -> float:
    """Pure-Python BM25-style overlap score (no external search engine).

    Real BM25 weighs term frequency against document length and inverse
    document frequency; this keeps the essential idea -- more query terms
    present, proportionally to document length -- without a dependency.
    """
    query_tokens = set(_tokenize(query))
    text_tokens = _tokenize(text)
    if not text_tokens or not query_tokens:
        return 0.0
    overlap = sum(1 for token in text_tokens if token in query_tokens)
    return overlap / math.sqrt(len(text_tokens))


def keyword_rank(query: str, corpus: list[tuple[str, str]]) -> list[str]:
    """Rank document ids by keyword score, descending."""
    scored = [(doc_id, keyword_score(query, text)) for doc_id, text in corpus]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [doc_id for doc_id, _ in scored]


def dense_rank(query: str, corpus: list[tuple[str, str]]) -> list[str]:
    """Rank document ids by dense (embedding) similarity, descending."""
    store = InMemoryVectorStore()
    ids, texts = zip(*corpus)
    store.add_texts(list(texts), ids=list(ids))
    results = store.similarity_search(query, k=len(corpus))
    return [result.document.id for result in results]


def reciprocal_rank_fusion(
    rankings: list[list[str]], k: int = 60
) -> list[tuple[str, float]]:
    """Fuse multiple rankings into one score per document via RRF.

    ``score(doc) = sum over rankings of 1 / (k + rank)``. Documents that rank
    highly in *either* signal accumulate score; a document only one signal
    likes still surfaces, but one that both signals like rises to the top.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)


def main() -> None:
    keyword_ranking = keyword_rank(QUERY, CORPUS)
    dense_ranking = dense_rank(QUERY, CORPUS)
    fused = reciprocal_rank_fusion([dense_ranking, keyword_ranking])
    fused_ranking = [doc_id for doc_id, _ in fused]

    print(f"query={QUERY!r}")
    print(f"keyword_rank={keyword_ranking}")
    print(f"dense_rank={dense_ranking}")
    print(f"fused_rank={fused_ranking}")
    for doc_id, score in fused:
        print(f"fused id={doc_id} score={score:.5f}")

    # doc-paraphrase is genuinely relevant (a paraphrase of the rate-limit
    # error) but shares no exact tokens with the query's error code. Keyword
    # search alone buries it below the irrelevant doc-oncall (a false
    # positive from common words); dense embeddings rank it correctly, and
    # fusion inherits that correct placement instead of keyword's mistake.
    paraphrase = "doc-paraphrase"
    distractor = "doc-oncall"
    keyword_buries_it = keyword_ranking.index(paraphrase) > keyword_ranking.index(
        distractor
    )
    fusion_recovers_it = fused_ranking.index(paraphrase) < fused_ranking.index(
        distractor
    )
    print(
        f"keyword_rank_of({paraphrase})={keyword_ranking.index(paraphrase) + 1} "
        f"vs keyword_rank_of({distractor})={keyword_ranking.index(distractor) + 1} "
        f"-> keyword_buries_relevant_doc={keyword_buries_it}"
    )
    print(
        f"fused_rank_of({paraphrase})={fused_ranking.index(paraphrase) + 1} "
        f"vs fused_rank_of({distractor})={fused_ranking.index(distractor) + 1} "
        f"-> fusion_recovers_relevant_doc={fusion_recovers_it}"
    )

    print("=== TRACK5 MODULE 39: HYBRID SEARCH COMPLETE ===")


if __name__ == "__main__":
    main()
