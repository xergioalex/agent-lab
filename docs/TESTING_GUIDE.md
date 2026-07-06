# Testing Guide — Agent Lab

## Current Setup

| Tool | Purpose | Command |
|------|---------|---------|
| **pytest** | Smoke tests for all 64 modules (offline) | `pytest` |
| **Manual script run** | Optional live OpenAI backend | `OPENAI_API_KEY=... python src/03_llm_nodes/main.py` |

Install test dependencies with the main requirements:

```bash
pip install -r requirements.txt
```

## Test Layout

```
tests/
├── conftest.py              # offline_env() + run_module()
├── test_smoke.py            # on-ramp modules 01–10
├── test_track1_foundations.py … test_track9_projects.py
```

## Running Tests

```bash
# All smoke tests (65 tests across 64 modules + shared)
pytest

# Verbose output
pytest -v

# Single test
pytest tests/test_smoke.py::test_state_basics_runs -v

# All exercise script tests
pytest tests/test_smoke.py -k "runs or multi_agent or brain or tools or llm" -v
```

## What Is Covered (automated)

| Test | Module | Script | Assertion |
|------|--------|--------|-----------|
| `test_state_basics_runs` | 01 | `main.py` | exit 0, `"hello"` + `MODULE 01` |
| `test_langgraph_basics_runs` | 02 | `main.py` | exit 0, `"start"` + `MODULE 02` |
| `test_llm_nodes_runs_offline` | 03 | `main.py` | exit 0, offline or openai backend |
| `test_routing_runs` | 04 | `main.py` | exit 0, `"blocker"` in output |
| `test_tools_runs` | 05 | `main.py` | exit 0, `"Slack sent"` |
| `test_memory_basics_runs` | 06 | `main.py` | exit 0, `"login"` |
| `test_qdrant_integration_runs` | 07 | `main.py` | exit 0, `indexed=3` |
| `test_graph_memory_neo4j_runs` | 08 | `main.py` | exit 0, org graph finding |
| `test_multi_agent_runs` | 09 | `main.py` | exit 0, `"done"` |
| `test_brain_simulation_runs` | 10 | `main.py` | exit 0, integrated brain banner |
| `test_shared_state_typeddict` | shared | `state.py` | import + annotation check |

## What Requires Manual Validation

| Module | Reason | Command |
|--------|--------|---------|
| `03_llm_nodes` | Optional live OpenAI backend | `export OPENAI_API_KEY=sk-... && python src/03_llm_nodes/main.py` |
| `07`, `42` | Optional real Qdrant | `docker compose up -d` + `QDRANT_URL=http://localhost:6333` |
| `08`, `43+` | Optional real Neo4j | `NEO4J_URI=bolt://localhost:7687` |

Tests always run offline via `tests/conftest.py` (`offline_env()` strips API keys and service URLs).

## Run All Exercises Manually

See [src/README.md](../src/README.md) for per-module commands, expected output,
and a batch script to run every offline exercise.

Quick reference:

```bash
# Offline modules (all exit 0)
python src/01_state_basics/main.py
python src/02_langgraph_basics/main.py
python src/04_routing_and_branches/main.py
python src/05_tools/main.py
python src/06_memory_basics/main.py
python src/07_qdrant_integration/main.py
python src/08_graph_memory_neo4j/main.py
python src/09_multi_agent_systems/main.py
python src/10_full_brain_simulation/main.py

# LLM module (requires key)
export OPENAI_API_KEY=sk-...
python src/03_llm_nodes/main.py
```

## Validation Results (last run)

All offline scripts exit 0. Module 03 fails without `OPENAI_API_KEY` (expected).
Full `pytest` suite: **11 passed**.

## Proposed Additions (target toolchain)

As the repo matures, adopt these incrementally:

| Tool | Purpose | Proposed command |
|------|---------|------------------|
| **ruff** | Lint + format | `ruff check .` and `ruff format --check .` |
| **mypy** | Type checking on `src/shared/` | `mypy src/shared` |
| **pytest-cov** | Coverage reporting | `pytest --cov=src --cov-report=term-missing` |

Add mocked LLM tests for `03_llm_nodes` using `unittest.mock` to avoid live API
calls in CI while still validating response shape.

## Coverage Expectation

- **Minimum**: all smoke tests pass before merge.
- **Target**: every runnable script has either a smoke test or a documented
  manual validation step in this guide and [src/README.md](../src/README.md).

## Validation Gate for Deep Work Plans

When executing a DWP task that touches code:

1. `pytest` — must pass (11 tests)
2. Run the affected module script manually if behavior changed
3. For LLM changes, confirm behavior with `OPENAI_API_KEY` or a mock
