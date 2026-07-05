
# 09 - Multi-Agent Systems

## Concept

Multiple agents working together.

## Roles

- planner
- executor
- reflection

## Goal

Understand collaboration between agents.

## Run

From the repository root:

```bash
python src/09_multi_agent_systems/agents.py
```

## Expected output

```
{'result': 'done'}
```

## What happens

1. `planner` adds `{"plan": ["step1", "step2"]}` to state
2. `executor` adds `{"result": "done"}` to state
3. Final merged state is printed (executor overwrites plan key in this simple demo)

## Automated test

Covered by `pytest` — `test_multi_agent_runs` in `tests/test_smoke.py`.
