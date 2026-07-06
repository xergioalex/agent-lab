"""37 — Embeddings: vectors, cosine similarity, and chunking.

Demonstrates how ``get_embeddings()`` turns text into vectors, how cosine
similarity ranks documents against a query, and how chunk size changes what
gets retrieved. Runs fully offline via the deterministic ``HashingEmbeddings``
bag-of-words embedder (no OpenAI key, no numpy).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/37_embeddings/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_embeddings, get_logger  # noqa: E402

logger = get_logger(__name__)

# A small corpus standing in for a company knowledge base.
CORPUS: dict[str, str] = {
    "deploy": "Production deploys run through CI after two approvals from senior engineers.",
    "oncall": "The on-call engineer rotates weekly and monitors the incident channel.",
    "standup": "Daily standups happen every morning to sync on blockers in the team channel.",
    "vacation": "Employees request vacation through the HR portal two weeks in advance.",
}

QUERY = "Who approves a production deploy before it ships?"

# A longer document that mixes several topics -- chunking it differently
# changes which sentences end up embedded together, and therefore what a
# query retrieves.
LONG_DOCUMENT = (
    "Production deploys run through CI after two approvals from senior engineers. "
    "The on-call engineer rotates weekly and monitors the incident channel. "
    "Daily standups happen every morning to sync on blockers in the team channel. "
    "Employees request vacation through the HR portal two weeks in advance."
)


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors (pure Python, no numpy)."""
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_by_similarity(query: str, documents: dict[str, str]) -> list[tuple[str, float]]:
    """Embed ``query`` and every document, then rank documents by cosine similarity.

    Uses ``get_embeddings()`` — the real ``OpenAIEmbeddings`` if ``OPENAI_API_KEY``
    is set, otherwise the deterministic, dependency-free ``HashingEmbeddings``.
    Hashed embeddings are a bag-of-words: each token contributes +/-1 to a bucket
    picked by ``md5(token) % dim``. They carry real signal (shared vocabulary
    scores higher) while staying reproducible across runs and processes, which is
    exactly what an offline demo and a smoke test need.
    """
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query(query)
    doc_vectors = embeddings.embed_documents(list(documents.values()))
    scored = [
        (doc_id, cosine_similarity(query_vector, vector))
        for doc_id, vector in zip(documents.keys(), doc_vectors)
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


def chunk_text(text: str, chunk_size: int) -> list[str]:
    """Split ``text`` into word-based chunks of at most ``chunk_size`` words."""
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]


def main() -> None:
    logger.info("embedding %d corpus documents", len(CORPUS))
    ranked = rank_by_similarity(QUERY, CORPUS)
    print(f"query={QUERY!r}")
    for doc_id, score in ranked:
        print(f"doc={doc_id} score={score:.4f}")

    print()
    print("--- chunking the same long document at two granularities ---")
    for chunk_size in (11, 45):
        chunks = chunk_text(LONG_DOCUMENT, chunk_size)
        chunk_corpus = {f"chunk-{i}": chunk for i, chunk in enumerate(chunks)}
        chunk_ranked = rank_by_similarity(QUERY, chunk_corpus)
        best_chunk, best_score = chunk_ranked[0]
        best_text = chunks[int(best_chunk.split("-")[1])]
        print(
            f"chunk_size={chunk_size} num_chunks={len(chunks)} "
            f"best_chunk={best_chunk} score={best_score:.4f} text={best_text!r}"
        )
    print(
        "takeaway: sentence-sized chunks (chunk_size=11) isolate the deploy "
        "sentence and score higher; one giant chunk (chunk_size=45) dilutes "
        "the same signal with unrelated topics and scores lower."
    )

    print("=== TRACK5 MODULE 37: EMBEDDINGS COMPLETE ===")


if __name__ == "__main__":
    main()
