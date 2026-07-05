"""31 -- Semantic Memory: timeless facts stored and retrieved by similarity.

Contrasts semantic memory (context-free facts, e.g. "Paris is the capital of
France") with episodic memory (module 30: timestamped events). Facts are
embedded with ``get_embeddings`` and stored in ``InMemoryVectorStore``
(offline: the deterministic ``HashingEmbeddings`` fallback), then retrieved by
semantic similarity to a query.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/31_semantic_memory/semantic_memory.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryVectorStore, get_embeddings, get_logger  # noqa: E402

logger = get_logger(__name__)

FACTS: list[tuple[str, dict[str, str]]] = [
    ("The Eiffel Tower is located in Paris, France.", {"topic": "geography"}),
    ("Photosynthesis converts sunlight into chemical energy in plants.", {"topic": "biology"}),
    ("Python is a dynamically typed programming language.", {"topic": "programming"}),
    ("The mitochondria is the powerhouse of the cell.", {"topic": "biology"}),
    ("Paris is the capital of France.", {"topic": "geography"}),
]


class SemanticMemory:
    """Facts store: write once, retrieve by meaning (not by keyword or time)."""

    def __init__(self) -> None:
        self._store = InMemoryVectorStore(embeddings=get_embeddings())

    def write_facts(self, facts: list[tuple[str, dict[str, str]]]) -> list[str]:
        texts = [text for text, _ in facts]
        metas = [meta for _, meta in facts]
        ids = self._store.add_texts(texts, metadatas=metas)
        logger.info("wrote %d fact(s) to semantic memory", len(ids))
        return ids

    def recall(self, query: str, k: int = 2) -> list[tuple[str, float]]:
        results = self._store.similarity_search(query, k=k)
        return [(r.document.text, round(r.score, 4)) for r in results]


def main() -> None:
    memory = SemanticMemory()
    memory.write_facts(FACTS)

    for query in ("What is the capital of France?", "How do cells produce energy?"):
        hits = memory.recall(query, k=2)
        print(f"query={query!r}")
        for text, score in hits:
            print(f"  score={score} fact={text!r}")

    print("=== TRACK4 MODULE 31: SEMANTIC MEMORY COMPLETE ===")


if __name__ == "__main__":
    main()
