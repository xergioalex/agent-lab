# Standards — Agent Lab

## Module Structure

- Modules are numbered `01` through `10` with zero-padded prefixes for sort order.
- Each module folder name uses `snake_case` describing the topic.
- Every module **MUST** have a `README.md` with: Concept, Key idea, Exercise/Goal.
- Exercise scripts live at the module root, not in subpackages.

## Python Conventions

- Python 3.10+ assumed (for `TypedDict` and modern typing).
- Use `from typing import TypedDict` for graph state definitions.
- Prefer explicit dict returns from LangGraph nodes: `return {"field": value}`.
- Keep exercises short and readable — this is a learning repo, not production code.

## Naming

| Element | Convention | Example |
|---------|------------|---------|
| Module folders | `NN_topic_name` | `04_routing_and_branches` |
| Exercise files | `snake_case.py` | `basic_graph.py`, `hello_world.py` |
| Node functions | single letter or descriptive | `a`, `b`, `call_llm`, `router` |
| State fields | `snake_case` | `message`, `intent`, `response` |

## Import Order

1. Standard library
2. Third-party (`langgraph`, `langchain_openai`)
3. Local/shared (when introduced)

Blank line between groups.

## Error Handling

- Early modules: minimal — let exceptions surface for learning.
- Mock integrations (`07`, `08`): print placeholders; do not require live services.
- LLM modules (`03+`): document that missing `OPENAI_API_KEY` will fail at runtime.

## Forbidden Patterns

- Do not commit API keys or `.env` files.
- Do not add cross-imports between numbered modules (breaks isolated learning).
- Do not convert exercises into a pip-installable package without an explicit plan.
- Do not add heavy frameworks (web servers, databases) without updating docs and tests.

## Documentation

- Update the module `README.md` when changing exercise behavior.
- Update `docs/DEVELOPMENT_COMMANDS.md` when adding new runnable scripts.
- English only for all docs and comments.
