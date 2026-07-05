# ADR 0001: Offline-first with deterministic fakes

**Status:** Accepted

## Context

Agent Lab teaches LLM, vector-DB, and graph-DB engineering. If every exercise
required an OpenAI key, a running Qdrant, and a running Neo4j, the curriculum
would be slow to start, expensive, non-deterministic, and impossible to test in
CI. Learners must be able to `git clone && pytest` and have everything pass.

## Decision

Every exercise and the entire `pytest` suite **must run offline** with no API
keys and no external services. The shared library provides deterministic
fallbacks that share the real interfaces:

- `get_chat_model()` → real `ChatOpenAI` if `OPENAI_API_KEY` is set, else a
  `FakeToolCallingModel` (supports `bind_tools` and `with_structured_output`).
- `get_embeddings()` → real `OpenAIEmbeddings` if keyed, else a pure-Python
  `HashingEmbeddings` (meaningful similarity, no numpy).
- `InMemoryVectorStore` / `InMemoryGraphStore` mirror Qdrant / Neo4j and are the
  default; real clients activate when `QDRANT_URL` / `NEO4J_URI` are present.

Real backends activate **automatically** from environment variables — the same
code runs offline and in production.

## Consequences

- ✅ Zero-config onboarding; fast, deterministic, CI-friendly tests.
- ✅ The same lesson code demonstrates the real API surface.
- ⚠️ Fakes are simplified (e.g. the offline model picks tools heuristically);
  modules must state where behavior differs from a real LLM.
- ⚠️ Real-backend paths need separate, env-gated integration tests (future work).
