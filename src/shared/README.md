# Shared Utilities

Cross-module helpers introduced as exercises graduate from inline definitions.

## Files

| File | Purpose |
|------|---------|
| `state.py` | `State` TypedDict with a `message: str` field — reusable graph state |
| `config.py` | `OPENAI_MODEL` constant (`gpt-4o-mini`) for LLM exercises |

## Usage

Import when an exercise needs a consistent state shape or model name:

```python
from src.shared.state import State  # when package layout is introduced
```

Early modules define state inline; later modules and the capstone should converge
on these shared definitions.

## Run

There is no standalone script. Shared utilities are validated by importing them:

```bash
pytest tests/test_smoke.py::test_shared_state_typeddict -v
```

Or run the full suite:

```bash
pytest
```

## Testing

`tests/test_smoke.py` imports `state.py` to verify the TypedDict annotation.

## Notes

- `config.py` holds only non-secret configuration. API keys belong in environment
  variables — see [docs/SECURITY.md](../../docs/SECURITY.md).
- Do not add heavy dependencies here; keep shared code minimal.
