# Performance — Agent Lab

## Scope

Agent Lab is a learning repository, not a performance-critical production system.
This document notes where performance matters as exercises scale up.

## LLM Calls (modules 03+)

- Each `ChatOpenAI.invoke()` is a network round-trip — batch or cache when building
  multi-step agents.
- Default model is `gpt-4o-mini` (`src/shared/config.py`) — cost-efficient for learning.
- For capstone work (`10`), consider streaming responses for better perceived latency.

## LangGraph Execution (module 02+)

- Graphs in early exercises are tiny (2 nodes) — compile overhead is negligible.
- For complex graphs, compile once (`app = g.compile()`) and reuse the compiled app.

## Memory (modules 06–08)

| Approach | Module | Performance note |
|----------|--------|------------------|
| In-memory list | `06` | O(n) reads; fine for demos |
| Vector DB | `07` | Embedding + search dominate; use batch upserts |
| Graph DB | `08` | Query patterns matter; index relationship types |

Mocks in `07` and `08` do not exercise real latency — treat performance guidance
as forward-looking for production implementations.

## Multi-Agent (module 09)

- Sequential planner → executor is simple but adds LLM latency per agent.
- Parallel agent execution requires async patterns not yet introduced.

## Profiling

Not required for current exercises. When the capstone matures:

```bash
python -m cProfile -s cumulative src/10_full_brain_simulation/main.py
```

## Budgets (recommended for capstone)

| Operation | Target |
|-----------|--------|
| Single LLM call (learning) | < 5s |
| Full brain simulation loop | Document actual budget when implemented |
