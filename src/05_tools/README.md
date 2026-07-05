
# 05 - Tools

## Concept

Agents interact with external systems.

## Examples

- Slack
- GitHub
- APIs

## Goal

Understand tool calling pattern.

## Run

From the repository root:

```bash
python src/05_tools/mock_tool.py
```

## Expected output

```
Slack sent: hello
```

## What happens

1. `slack_tool("hello")` simulates sending a Slack message
2. Returns a formatted confirmation string

## Automated test

Covered by `pytest` — `test_tools_runs` in `tests/test_smoke.py`.
