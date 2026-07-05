# ADR 0002: Shared library as the reuse boundary

**Status:** Accepted

## Context

54 modules across 9 tracks risk massive duplication (each re-implementing an LLM
factory, an embedder, a vector store, demo tools). Duplication makes the
curriculum inconsistent and hard to maintain, and obscures the real lesson.

## Decision

All cross-module infrastructure lives in **`src/shared/`** and is imported via
`from src.shared import ...`. Modules compose these primitives; they do not
re-implement them. A module that needs a new primitive **adds it to
`src/shared/` with a test**, rather than inlining a copy.

Public surface: `get_settings`/`Settings`, `get_logger`, `get_chat_model`/
`FakeToolCallingModel`/`is_offline`, `get_embeddings`, `InMemoryVectorStore`/
`Document`/`SearchResult`, `InMemoryGraphStore`/`Node`/`Relationship`,
`DEMO_TOOLS`, `State`/`AgentState`.

Because numbered folders start with digits (not importable as packages), each
runnable script prepends the repo root to `sys.path`, then imports `src.shared`.

## Consequences

- ✅ One place to learn/upgrade the infrastructure; consistent APIs everywhere.
- ✅ Modules stay focused on their concept, not boilerplate.
- ⚠️ The shared surface is a contract — changes ripple across modules, so it is
  covered by tests and evolves deliberately.
