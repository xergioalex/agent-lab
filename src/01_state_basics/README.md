
# 01 - State Basics

## Concept

Learn how state flows through functions.

## Key idea

Agents are just:
> state transformations

## Exercise

Build a pipeline:
- input state
- modify state in nodes
- pass between functions

## Run

From the repository root:

```bash
python src/01_state_basics/hello_world.py
```

## Expected output

```
{'message': 'hello | A | B'}
```

## What happens

1. Initial state: `{"message": "hello"}`
2. `node_a` appends `" | A"`
3. `node_b` appends `" | B"`
4. Final state is printed

## Automated test

Covered by `pytest` — `test_state_basics_runs` in `tests/test_smoke.py`.
