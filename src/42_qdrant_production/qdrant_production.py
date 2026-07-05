"""42 — Qdrant Production Path: real client vs. offline fallback.

A production vector-store wrapper that uses the **real** ``qdrant-client``
when ``QDRANT_URL`` is configured, and falls back to the in-memory store
(module 07's baseline, deepened) otherwise. ``qdrant-client`` is **not
installed** in this environment, so its import lives strictly inside the
``QDRANT_URL``-gated branch and is never touched by the offline path this
script (and its smoke test) actually exercises.

Also demonstrates the concepts that carry over between both backends:
collections, payloads (arbitrary per-document metadata), and filtered search.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Protocol

# Make `src.shared` importable when run as `python src/42_qdrant_production/qdrant_production.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import (  # noqa: E402
    InMemoryVectorStore,
    SearchResult,
    Settings,
    get_logger,
    get_settings,
)

logger = get_logger(__name__)

COLLECTION_NAME = "agent_lab_docs"

# id, text, payload (metadata). A real deployment would filter search by
# payload fields like `category` or `tenant_id` -- Qdrant does this
# server-side; the in-memory fallback does it by post-filtering below.
DOCUMENTS: list[tuple[str, str, dict[str, Any]]] = [
    ("doc-deploy", "Production deploys run through CI after two approvals.", {"category": "policy"}),
    ("doc-vacation", "Employees request vacation through the HR portal two weeks ahead.", {"category": "policy"}),
    ("doc-oncall", "The on-call engineer rotates weekly and monitors incidents.", {"category": "runbook"}),
    ("doc-standup", "Daily standups happen every morning in the team channel.", {"category": "runbook"}),
]

QUERY = "What is the policy for requesting time off?"


class VectorStoreClient(Protocol):
    """The minimal surface both backends implement, so callers never branch."""

    def add_texts(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]: ...

    def similarity_search(self, query: str, k: int = 3) -> list[SearchResult]: ...

    def __len__(self) -> int: ...


def _build_qdrant_store(settings: Settings) -> VectorStoreClient:
    """Build a real Qdrant-backed store. Only called when ``QDRANT_URL`` is set.

    The ``qdrant-client`` import is deliberately kept inside this function
    (never at module top level) so this script stays importable and runnable
    with the dependency absent -- the exact requirement for the offline
    fallback path below to be the one the smoke test exercises.
    """
    from qdrant_client import QdrantClient  # noqa: PLC0415 - intentionally lazy
    from qdrant_client.models import (  # noqa: PLC0415
        Distance,
        PointStruct,
        VectorParams,
    )

    from src.shared import get_embeddings  # noqa: PLC0415

    embeddings = get_embeddings()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

    class QdrantAdapter:
        """Adapts ``QdrantClient`` to the same surface as ``InMemoryVectorStore``."""

        def __init__(self) -> None:
            self._client = client
            self._count = 0
            probe_dim = len(embeddings.embed_query("probe"))
            self._client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=probe_dim, distance=Distance.COSINE),
            )

        def add_texts(
            self,
            texts: list[str],
            metadatas: list[dict[str, Any]] | None = None,
            ids: list[str] | None = None,
        ) -> list[str]:
            metadatas = metadatas or [{} for _ in texts]
            ids = ids or [f"doc-{self._count + i}" for i in range(len(texts))]
            vectors = embeddings.embed_documents(texts)
            points = [
                PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={"text": text, **meta},
                )
                for doc_id, text, meta, vector in zip(ids, texts, metadatas, vectors)
            ]
            self._client.upsert(collection_name=COLLECTION_NAME, points=points)
            self._count += len(texts)
            return ids

        def similarity_search(self, query: str, k: int = 3) -> list[SearchResult]:
            from src.shared import Document  # noqa: PLC0415

            query_vector = embeddings.embed_query(query)
            hits = self._client.search(
                collection_name=COLLECTION_NAME, query_vector=query_vector, limit=k
            )
            return [
                SearchResult(
                    Document(
                        id=str(hit.id),
                        text=hit.payload.get("text", ""),
                        metadata={k: v for k, v in hit.payload.items() if k != "text"},
                    ),
                    hit.score,
                )
                for hit in hits
            ]

        def __len__(self) -> int:
            return self._count

    return QdrantAdapter()


def build_store() -> VectorStoreClient:
    """Return a real Qdrant-backed store if ``QDRANT_URL`` is configured.

    Otherwise fall back to ``InMemoryVectorStore`` -- the path exercised
    offline by this script and its smoke test.
    """
    settings = get_settings()
    if settings.has_qdrant():
        logger.info("QDRANT_URL set -> using real qdrant-client backend")
        return _build_qdrant_store(settings)
    logger.info("QDRANT_URL not set -> falling back to InMemoryVectorStore")
    return InMemoryVectorStore()


def similarity_search_filtered(
    store: VectorStoreClient, query: str, k: int, category: str | None = None
) -> list[SearchResult]:
    """Similarity search with an optional metadata filter.

    A real Qdrant collection would push this filter server-side via a
    ``Filter``/``FieldCondition`` on the payload. The in-memory fallback has
    no server to push it to, so it over-fetches and post-filters -- correct
    results, different cost profile, which is exactly the tradeoff production
    code needs to be honest about.
    """
    if category is None:
        return store.similarity_search(query, k=k)
    candidates = store.similarity_search(query, k=k * len(DOCUMENTS))
    matching = [r for r in candidates if r.document.metadata.get("category") == category]
    return matching[:k]


def main() -> None:
    store = build_store()
    ids, texts, metadatas = zip(*DOCUMENTS)
    store.add_texts(list(texts), metadatas=list(metadatas), ids=list(ids))

    backend = type(store).__name__
    print(f"collection={COLLECTION_NAME} backend={backend} docs={len(store)}")

    results = similarity_search_filtered(store, QUERY, k=2, category="policy")
    for result in results:
        print(
            f"id={result.document.id} category={result.document.metadata.get('category')} "
            f"score={result.score:.4f}"
        )

    print("=== TRACK5 MODULE 42: QDRANT PRODUCTION COMPLETE ===")


if __name__ == "__main__":
    main()
