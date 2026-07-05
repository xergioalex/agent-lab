"""38 — RAG Fundamentals: retrieve -> augment -> generate.

Wires ``InMemoryVectorStore`` (retrieve) to ``get_chat_model`` (generate)
through a plain string prompt (augment), the same three-step loop a
production RAG pipeline runs against a real vector database and LLM. Fully
offline: the store uses the deterministic ``HashingEmbeddings`` and the model
is the deterministic ``FakeToolCallingModel``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/38_rag_fundamentals/rag.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import (  # noqa: E402
    InMemoryVectorStore,
    SearchResult,
    get_chat_model,
    get_logger,
)

logger = get_logger(__name__)

# id -> text. In production this would be chunked documents loaded from a
# knowledge base, wiki, or ticketing system (see module 37 for chunking).
KNOWLEDGE_BASE: list[tuple[str, str]] = [
    ("kb-deploy", "Production deploys run through CI after two approvals from senior engineers."),
    ("kb-oncall", "The on-call engineer rotates weekly and monitors the incident channel."),
    ("kb-standup", "Daily standups happen every morning to sync on blockers in the team channel."),
    ("kb-vacation", "Employees request vacation through the HR portal two weeks in advance."),
]

QUESTION = "Who has to approve a production deploy before it ships?"
TOP_K = 2


def ingest(store: InMemoryVectorStore, corpus: list[tuple[str, str]]) -> None:
    """Embed and upsert every document into the vector store."""
    ids, texts = zip(*corpus)
    store.add_texts(list(texts), ids=list(ids))
    logger.info("ingested %d documents", len(corpus))


def retrieve(store: InMemoryVectorStore, question: str, k: int) -> list[SearchResult]:
    """Retrieve step: the top-k documents most similar to the question."""
    return store.similarity_search(question, k=k)


def augment(question: str, results: list[SearchResult]) -> str:
    """Augment step: stuff retrieved context into the prompt, with citations.

    Real systems must respect the model's context window -- only the
    highest-scoring chunks fit, so retrieval quality (module 37's chunking,
    module 39's hybrid search) directly bounds answer quality here.
    """
    context = "\n".join(f"[{r.document.id}] {r.document.text}" for r in results)
    return (
        "Answer the question using ONLY the context below. "
        "Cite the source id(s) you used in square brackets.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )


def generate(prompt: str, grounding_id: str) -> str:
    """Generate step: call the chat model with the augmented prompt.

    The offline fake returns a canned, citation-bearing answer so the demo
    stays deterministic; a real ``ChatOpenAI`` would read the same augmented
    prompt and produce a grounded answer citing the same context.
    """
    canned_answer = (
        f"Two senior engineers must approve a deploy via CI before it ships. [{grounding_id}]"
    )
    model = get_chat_model(responses=[canned_answer])
    response = model.invoke(prompt)
    return str(response.content)


def main() -> None:
    store = InMemoryVectorStore()
    ingest(store, KNOWLEDGE_BASE)

    results = retrieve(store, QUESTION, TOP_K)
    print(f"question={QUESTION!r}")
    for result in results:
        print(f"retrieved id={result.document.id} score={result.score:.4f}")

    prompt = augment(QUESTION, results)
    answer = generate(prompt, results[0].document.id)
    print(f"answer={answer!r}")

    print("=== TRACK5 MODULE 38: RAG FUNDAMENTALS COMPLETE ===")


if __name__ == "__main__":
    main()
