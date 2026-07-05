
# 06 - Memory Basics

## Concept

Agents need memory to evolve.

## Types

- short term
- long term (later)

## Goal

Store and retrieve state.

## Run

From the repository root:

```bash
python src/06_memory_basics/memory.py
```

## Expected output

```
[{'event': 'login'}]
```

## What happens

1. An in-memory list acts as event storage
2. `write({"event": "login"})` appends an event
3. `read()` returns the full event log

## Automated test

Covered by `pytest` — `test_memory_basics_runs` in `tests/test_smoke.py`.
