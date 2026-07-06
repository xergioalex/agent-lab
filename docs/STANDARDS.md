# Standards — Agent Lab

## Module Structure

- Modules are numbered `01` through `64` with zero-padded prefixes for sort order.
- Each module folder name uses `snake_case` describing the topic.
- Every module **MUST** have a `README.md` with objectives, theory, run command, and challenges.
- Every module **MUST** expose exactly one exercise entrypoint: `main.py` at the module root.

## Python Conventions

- Python 3.10+ assumed (for `TypedDict` and modern typing).
- Use `from typing import TypedDict` for graph state definitions.
- Prefer explicit dict returns from LangGraph nodes: `return {"field": value}`.
- Every `main.py` **SHOULD** define `main()` and guard with `if __name__ == "__main__":`.
- Import shared infrastructure from `src.shared`; gate real backends behind `get_settings()`.

## Naming

| Element | Convention | Example |
|---------|------------|---------|
| Module folders | `NN_topic_name` | `04_routing_and_branches` |
| Exercise file | `main.py` (fixed) | `src/04_routing_and_branches/main.py` |
| Node functions | descriptive | `classify`, `call_llm`, `route_intent` |
| State fields | `snake_case` | `message`, `intent`, `response` |

## Running Exercises

```bash
python src/01_state_basics/main.py
make run MODULE=01_state_basics
```

Optional backends (Qdrant, Neo4j):

```bash
docker compose -f docker-compose.yml up -d
# set QDRANT_URL / NEO4J_URI in .env — see .env.example
```

## Import Order

1. Standard library
2. Third-party (`langgraph`, `langchain_core`)
3. Local/shared (`src.shared`)

Blank line between groups.

## Error Handling

- Exercises use `get_logger` for structured output; let unexpected errors surface.
- Real service imports (`qdrant_client`, `neo4j`) must be **lazy** inside configured branches.
- All modules run offline by default via deterministic fakes in `src.shared`.

## Forbidden Patterns

- Do not commit API keys or `.env` files.
- Do not add cross-imports between numbered modules (breaks isolated learning).
- Do not use placeholder-only scripts (`print("stub")`) in the on-ramp.
- Do not name exercise files anything other than `main.py`.

## Documentation

- Update the module `README.md` when changing exercise behavior.
- Update `docs/DEVELOPMENT_COMMANDS.md` when adding new runnable scripts.
- English only for all docs and comments.
