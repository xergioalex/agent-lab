
# 10 - Full Brain Simulation

## Concept

Combine everything:

- memory
- tools
- graph
- LLM
- routing

## Goal

Build a mini AI Operating System.

## Status

**Stub** — prints a banner; full capstone implementation is a future exercise.

## Run

From the repository root:

```bash
python src/10_full_brain_simulation/brain.py
```

## Expected output

```
Full Brain Simulation
This will combine all systems together
```

## Automated test

Covered by `pytest` — `test_brain_simulation_runs` in `tests/test_smoke.py`.

## Next steps

Wire together modules 01–09 into a single LangGraph that uses:
- Shared `State` from `src/shared/`
- LLM nodes for reasoning
- Tools for external actions
- Memory backends (in-memory, Qdrant, Neo4j)
- Multi-agent planner/executor roles
