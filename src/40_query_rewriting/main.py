"""40 — Query Rewriting: multi-query expansion and HyDE.

Two rewriting strategies for closing the gap between how a user phrases a
question and how the knowledge base phrases the answer:

1. **Multi-query expansion** — ask the model for several alternate phrasings
   of the same question, retrieve for each, and merge the results.
2. **HyDE (Hypothetical Document Embeddings)** — ask the model to sketch a
   *hypothetical answer*, embed that answer instead of the bare question, and
   retrieve with it. An answer-shaped embedding often lands closer to a real
   answer-shaped document than a short, terse question does.

Both run through ``get_chat_model``'s deterministic offline fake, so the
"rewrites" and "hypothetical answer" are canned but the retrieval mechanics
(embedding, similarity search, merging) are real.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/40_query_rewriting/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryVectorStore, SearchResult, get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

KNOWLEDGE_BASE: list[tuple[str, str]] = [
    ("kb-vacation", "Employees request vacation through the HR portal at least two weeks in advance."),
    ("kb-deploy", "Production deploys run through CI after two approvals from senior engineers."),
    ("kb-oncall", "The on-call engineer rotates weekly and monitors the incident channel."),
    ("kb-standup", "Daily standups happen every morning to sync on blockers in the team channel."),
]

USER_QUERY = "How far ahead do I need to plan a trip away from work?"

# Canned model response for multi-query expansion: a numbered list of
# alternate phrasings, exactly what a real prompt ("rewrite this question 3
# different ways") would ask an LLM to produce.
_MULTI_QUERY_RESPONSE = (
    "1. How much notice is required before taking time off?\n"
    "2. What is the process for requesting vacation?\n"
    "3. vacation HR portal advance notice policy"
)

# Canned model response for HyDE: a hypothetical answer to embed instead of
# the bare question.
_HYDE_RESPONSE = (
    "You should submit your vacation request through the HR portal at least "
    "two weeks before your planned time off."
)


def expand_query(query: str) -> list[str]:
    """Multi-query expansion: ask the model for alternate phrasings.

    In production this is one LLM call whose numbered-list output gets
    parsed; here the offline fake returns a fixed numbered list so the demo
    is deterministic while exercising the exact same parsing code.
    """
    model = get_chat_model(responses=[_MULTI_QUERY_RESPONSE])
    raw = str(model.invoke(f"Rewrite this question 3 different ways: {query!r}").content)
    rewrites = [line.split(".", 1)[-1].strip() for line in raw.splitlines() if line.strip()]
    return [query, *rewrites]


def hyde_query(query: str) -> str:
    """HyDE: generate a hypothetical answer and return it as the retrieval query."""
    model = get_chat_model(responses=[_HYDE_RESPONSE])
    hypothetical = str(
        model.invoke(f"Write a plausible one-sentence answer to: {query!r}").content
    )
    return hypothetical


def retrieve_many(
    store: InMemoryVectorStore, queries: list[str], k: int = 2
) -> dict[str, list[SearchResult]]:
    """Retrieve top-k results for each query variant."""
    return {query: store.similarity_search(query, k=k) for query in queries}


def merge_by_best_score(results_by_query: dict[str, list[SearchResult]]) -> list[tuple[str, float]]:
    """Merge retrieval results across query variants, keeping each doc's best score."""
    best: dict[str, float] = {}
    for results in results_by_query.values():
        for result in results:
            doc_id = result.document.id
            best[doc_id] = max(best.get(doc_id, 0.0), result.score)
    return sorted(best.items(), key=lambda pair: pair[1], reverse=True)


def build_store() -> InMemoryVectorStore:
    store = InMemoryVectorStore()
    ids, texts = zip(*KNOWLEDGE_BASE)
    store.add_texts(list(texts), ids=list(ids))
    return store


def main() -> None:
    store = build_store()

    print(f"user_query={USER_QUERY!r}")

    baseline = store.similarity_search(USER_QUERY, k=1)[0]
    print(f"baseline_top id={baseline.document.id} score={baseline.score:.4f}")

    print()
    print("--- multi-query expansion ---")
    variants = expand_query(USER_QUERY)
    for variant in variants:
        print(f"variant={variant!r}")
    results_by_variant = retrieve_many(store, variants, k=2)
    merged = merge_by_best_score(results_by_variant)
    print(f"merged_rank={merged}")

    print()
    print("--- HyDE (hypothetical document embeddings) ---")
    hypothetical = hyde_query(USER_QUERY)
    print(f"hypothetical_answer={hypothetical!r}")
    hyde_top = store.similarity_search(hypothetical, k=1)[0]
    print(
        f"hyde_top id={hyde_top.document.id} score={hyde_top.score:.4f} "
        f"vs baseline_top id={baseline.document.id} score={baseline.score:.4f} "
        f"improvement={hyde_top.score - baseline.score:+.4f}"
    )

    print("=== TRACK5 MODULE 40: QUERY REWRITING COMPLETE ===")


if __name__ == "__main__":
    main()
