"""07 — Qdrant Integration: embed -> index -> retrieve inside a StateGraph.

Uses ``InMemoryVectorStore`` offline; switches to a real Qdrant client when
``QDRANT_URL`` is configured (same gating pattern as module 42).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Protocol, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import (  # noqa: E402
    InMemoryVectorStore,
    SearchResult,
    Settings,
    get_embeddings,
    get_logger,
    get_settings,
)

logger = get_logger(__name__)

DOCUMENTS: list[tuple[str, str, dict[str, Any]]] = [
    ("doc-deploy", "Production deploys require two approvals from senior engineers.", {"category": "policy"}),
    ("doc-vacation", "Vacation requests go through the HR portal two weeks ahead.", {"category": "policy"}),
    ("doc-oncall", "The on-call engineer rotates weekly and monitors incidents.", {"category": "runbook"}),
]

QUERY = "Who approves production deploys?"


class VectorStoreClient(Protocol):
    def add_texts(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]: ...

    def similarity_search(self, query: str, k: int = 3) -> list[SearchResult]: ...


def _build_qdrant_store(settings: Settings) -> VectorStoreClient:
    from qdrant_client import QdrantClient  # noqa: PLC0415
    from qdrant_client.models import Distance, PointStruct, VectorParams  # noqa: PLC0415

    embeddings = get_embeddings()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    collection = "agent_lab_module_07"

    class Adapter:
        def __init__(self) -> None:
            self._client = client
            dim = len(embeddings.embed_query("probe"))
            self._client.recreate_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

        def add_texts(
            self,
            texts: list[str],
            metadatas: list[dict[str, Any]] | None = None,
            ids: list[str] | None = None,
        ) -> list[str]:
            metadatas = metadatas or [{} for _ in texts]
            ids = ids or [f"id-{i}" for i in range(len(texts))]
            vectors = embeddings.embed_documents(texts)
            points = [
                PointStruct(id=doc_id, vector=vec, payload={"text": text, **meta})
                for doc_id, text, meta, vec in zip(ids, texts, metadatas, vectors)
            ]
            self._client.upsert(collection_name=collection, points=points)
            return ids

        def similarity_search(self, query: str, k: int = 3) -> list[SearchResult]:
            from src.shared import Document  # noqa: PLC0415

            vector = embeddings.embed_query(query)
            hits = self._client.search(collection_name=collection, query_vector=vector, limit=k)
            return [
                SearchResult(
                    Document(id=str(h.id), text=h.payload.get("text", ""), metadata={}),
                    h.score,
                )
                for h in hits
            ]

    return Adapter()


def build_store() -> VectorStoreClient:
    settings = get_settings()
    if settings.has_qdrant():
        logger.info("using Qdrant at %s", settings.qdrant_url)
        return _build_qdrant_store(settings)
    logger.info("using InMemoryVectorStore (offline)")
    return InMemoryVectorStore()


class VectorState(TypedDict, total=False):
    store: Any
    backend: str
    indexed: int
    hits: list[SearchResult]


def index_docs(state: VectorState) -> dict[str, object]:
    store = build_store()
    ids, texts, metas = zip(*DOCUMENTS)
    store.add_texts(list(texts), metadatas=list(metas), ids=list(ids))
    backend = type(store).__name__
    return {"store": store, "backend": backend, "indexed": len(texts)}


def retrieve(state: VectorState) -> dict[str, object]:
    store: VectorStoreClient = state["store"]
    hits = store.similarity_search(QUERY, k=2)
    return {"hits": hits}


def report(state: VectorState) -> dict[str, object]:
    for hit in state["hits"]:
        print(f"id={hit.document.id} score={hit.score:.4f} text={hit.document.text!r}")
    return {}


def build_graph():
    graph = StateGraph(VectorState)
    graph.add_node("index", index_docs)
    graph.add_node("retrieve", retrieve)
    graph.add_node("report", report)
    graph.add_edge(START, "index")
    graph.add_edge("index", "retrieve")
    graph.add_edge("retrieve", "report")
    graph.add_edge("report", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({})
    print(f"backend={result['backend']} indexed={result['indexed']} query={QUERY!r}")
    print("=== MODULE 07: QDRANT INTEGRATION COMPLETE ===")


if __name__ == "__main__":
    main()
