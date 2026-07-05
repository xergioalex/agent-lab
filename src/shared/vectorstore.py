"""A tiny in-memory vector store used by the RAG and Qdrant modules.

It deliberately mirrors the shape of a real vector database (upsert documents,
similarity search with scores) so the mental model transfers directly to Qdrant.
Pure-Python cosine similarity keeps it dependency-free and offline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from langchain_core.embeddings import Embeddings

from src.shared.embeddings import get_embeddings


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@dataclass
class Document:
    """A stored chunk: text plus arbitrary metadata payload."""

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A similarity-search hit."""

    document: Document
    score: float


class InMemoryVectorStore:
    """Minimal cosine-similarity vector store with a Qdrant-like surface."""

    def __init__(self, embeddings: Embeddings | None = None) -> None:
        self.embeddings = embeddings or get_embeddings()
        self._docs: dict[str, Document] = {}
        self._vectors: dict[str, list[float]] = {}

    def add_texts(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        """Embed and upsert ``texts``; returns the assigned ids."""
        metadatas = metadatas or [{} for _ in texts]
        ids = ids or [f"doc-{len(self._docs) + i}" for i in range(len(texts))]
        vectors = self.embeddings.embed_documents(texts)
        for doc_id, text, meta, vec in zip(ids, texts, metadatas, vectors):
            self._docs[doc_id] = Document(id=doc_id, text=text, metadata=meta)
            self._vectors[doc_id] = vec
        return ids

    def similarity_search(self, query: str, k: int = 3) -> list[SearchResult]:
        """Return the top-``k`` documents most similar to ``query``."""
        query_vec = self.embeddings.embed_query(query)
        scored = [
            SearchResult(self._docs[doc_id], cosine_similarity(query_vec, vec))
            for doc_id, vec in self._vectors.items()
        ]
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:k]

    def __len__(self) -> int:
        return len(self._docs)
