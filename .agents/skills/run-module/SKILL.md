---
name: run-module
description: Run an Agent Lab module exercise and capture output for validation
---

# Run Module

## Goal

Execute a numbered module's exercise script and report success or failure.

## When to use

- Validating a module after changes
- Demonstrating output to a learner
- DWP validation gates that require a runnable script

## Steps

1. Identify the module number and script from [docs/DEVELOPMENT_COMMANDS.md](../../docs/DEVELOPMENT_COMMANDS.md).
2. Run: `python src/<module>/<script>.py` from the repo root.
3. For `03_llm_nodes`, confirm `OPENAI_API_KEY` is set or skip with reason.
4. Report exit code and relevant stdout.

## Validation

Exit code 0 and output matches the module README's expected behavior.

## Notes

Prefer `pytest` for offline modules; use this skill for manual demonstration.
