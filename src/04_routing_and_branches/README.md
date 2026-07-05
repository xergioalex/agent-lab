
# 04 - Routing & Branching

## Concept

Agents must decide paths dynamically.

## Key idea

Not linear execution → conditional flows.

## Goal

Build intent-based routing.

## Run

From the repository root:

```bash
python src/04_routing_and_branches/router.py
```

## Expected output

```
{'intent': 'blocker'}
```

## What happens

1. Router receives `{"message": "we are blocked"}`
2. Message contains `"block"` → returns `{"intent": "blocker"}`
3. Messages without `"block"` would return `{"intent": "general"}`

## Automated test

Covered by `pytest` — `test_routing_runs` in `tests/test_smoke.py`.
