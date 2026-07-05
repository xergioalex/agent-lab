---
name: extend-exercise
description: Scaffold the next step in a module exercise per its README goal
---

# Extend Exercise

## Goal

Add the next learning step to a module exercise without breaking the curriculum flow.

## When to use

- A module README lists a goal not yet implemented in code
- A learner asks to "complete" or "extend" an exercise

## Steps

1. Read `src/<module>/README.md` — the Goal section is the scope boundary.
2. Read the existing `.py` file(s) in that module.
3. Add the minimal code to achieve the README goal.
4. Do not import from other numbered modules.
5. Run the script and `pytest`.
6. Update the README if the goal changed.

## Validation

- Script runs without error (or documents API key requirement)
- `pytest` passes
- No cross-module imports added

## Notes

For capstone work in `10_full_brain_simulation`, coordinate via `/dwp-create`.
