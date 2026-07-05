# Testing Guide — Agent Lab

## Current Setup

| Tool | Purpose | Command |
|------|---------|---------|
| **pytest** | Smoke tests for all offline modules | `pytest` |
| **Manual script run** | LLM module with live API key | `OPENAI_API_KEY=... python src/03_llm_nodes/llm_node.py` |

Install test dependencies with the main requirements:

```bash
pip install -r requirements.txt
```

## Test Layout

```
tests/
└── test_smoke.py    # Subprocess runs for every module script + shared import
```

## Running Tests

```bash
# All smoke tests (11 tests)
pytest

# Verbose output
pytest -v

# Single test
pytest tests/test_smoke.py::test_state_basics_runs -v

# All exercise script tests
pytest tests/test_smoke.py -k "runs or placeholder or multi_agent or brain or tools or llm" -v
```

## What Is Covered (automated)

| Test | Module | Script | Assertion |
|------|--------|--------|-----------|
| `test_state_basics_runs` | 01 | `hello_world.py` | exit 0, `"hello"` in output |
| `test_langgraph_basics_runs` | 02 | `basic_graph.py` | exit 0, `"start"` in output |
| `test_llm_nodes_requires_api_key` | 03 | `llm_node.py` | non-zero exit without key |
| `test_routing_runs` | 04 | `router.py` | exit 0, `"blocker"` in output |
| `test_tools_runs` | 05 | `mock_tool.py` | exit 0, `"Slack sent"` in output |
| `test_memory_basics_runs` | 06 | `memory.py` | exit 0, `"login"` in output |
| `test_qdrant_placeholder_runs` | 07 | `mock_qdrant.py` | exit 0, placeholder text |
| `test_neo4j_placeholder_runs` | 08 | `mock_graph.py` | exit 0, placeholder text |
| `test_multi_agent_runs` | 09 | `agents.py` | exit 0, `"done"` in output |
| `test_brain_simulation_runs` | 10 | `brain.py` | exit 0, banner text |
| `test_shared_state_typeddict` | shared | `state.py` | import + annotation check |

## What Requires Manual Validation

| Module | Reason | Command |
|--------|--------|---------|
| `03_llm_nodes` | Live OpenAI API call | `export OPENAI_API_KEY=sk-... && python src/03_llm_nodes/llm_node.py` |

Without an API key, module 03 is still validated automatically — the smoke test
confirms it fails with a clear credentials error.

## Run All Exercises Manually

See [src/README.md](../src/README.md) for per-module commands, expected output,
and a batch script to run every offline exercise.

Quick reference:

```bash
# Offline modules (all exit 0)
python src/01_state_basics/hello_world.py
python src/02_langgraph_basics/basic_graph.py
python src/04_routing_and_branches/router.py
python src/05_tools/mock_tool.py
python src/06_memory_basics/memory.py
python src/07_qdrant_integration/mock_qdrant.py
python src/08_graph_memory_neo4j/mock_graph.py
python src/09_multi_agent_systems/agents.py
python src/10_full_brain_simulation/brain.py

# LLM module (requires key)
export OPENAI_API_KEY=sk-...
python src/03_llm_nodes/llm_node.py
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
