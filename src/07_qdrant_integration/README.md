
# 07 - Qdrant Integration

## Concept

Vector database for semantic memory.

## Use case

- search meaning
- retrieve documents

## Goal

Understand embeddings + vector search.

## Status

**Placeholder** — real Qdrant integration is a future exercise.

## Run

From the repository root:

```bash
python src/07_qdrant_integration/mock_qdrant.py
```

## Expected output

```
Qdrant placeholder
```

## Automated test

Covered by `pytest` — `test_qdrant_placeholder_runs` in `tests/test_smoke.py`.

## Next steps

Replace the placeholder with:
- Qdrant client setup
- Embedding generation
- Vector upsert and similarity search
