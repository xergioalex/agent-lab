# Architecture — Agent Lab

## Overview

Agent Lab is a flat Python learning repository. There is no package install step —
exercises are run as standalone scripts. Modules are numbered to enforce a
linear learning path.

```
Learner / Agent
      │
      ▼
  src/01_state_basics     ──► state as dict transformations
      │
      ▼
  src/02_langgraph_basics ──► LangGraph StateGraph
      │
      ▼
  src/03_llm_nodes        ──► ChatOpenAI integration
      │
      ▼
  src/04_routing          ──► conditional edges / intent routing
      │
      ▼
  src/05_tools            ──► tool invocation patterns
      │
      ▼
  src/06_memory_basics    ──► in-process memory list
      │
      ▼
  src/07_qdrant           ──► vector index + similarity search (Qdrant optional)
      │
      ▼
  src/08_neo4j            ──► graph memory + traversal (Neo4j optional)
      │
      ▼
  src/09_multi_agent      ──► planner + executor + critic loop
      │
      ▼
  src/10_full_brain       ──► integrated mini brain (extended in 64)
```

## Components

### Learning modules (`src/01_*` – `src/10_*`)

Each module is self-contained:

- One `main.py` exercise entrypoint per module
- A `README.md` with concept, key idea, and exercise goal
- No cross-imports between numbered modules (learners copy patterns forward)

### Shared utilities (`src/shared/`)

| File | Purpose |
|------|---------|
| `state.py` | Reusable `TypedDict` state definition |
| `config.py` | Model name constant (`OPENAI_MODEL`) |

Used when exercises graduate from inline types to shared definitions.

### Documentation (`docs/`)

Spec-driven guides for humans and agents. See [docs/README.md](README.md).

### Agent harness (`.agents/`, `AGENTS.md`)

Cross-agent configuration: DWP commands, repo-specific skills, and personas.

### Validation (`tests/`)

pytest smoke tests run offline modules without API keys.

## Data Flow (typical LangGraph exercise)

1. **Input state** — a dict or `TypedDict` with fields like `message`
2. **Nodes** — functions that return partial state updates
3. **Graph** — `StateGraph` wires nodes with edges or conditional routing
4. **Output** — `app.invoke(initial_state)` produces final state

Early modules (`01`) use plain functions before introducing LangGraph (`02`).

## External Dependencies

| Dependency | Used in | Notes |
|------------|---------|-------|
| `langgraph` | `02+` | Graph compilation and execution |
| `langchain-openai` | `03+` | Optional — `get_chat_model()` fakes offline |
| Qdrant | `07`, `42` | Optional — `InMemoryVectorStore` offline default |
| Neo4j | `08`, `43+` | Optional — `InMemoryGraphStore` offline default |

## Deployment Shape

None. All exercises run locally via `python src/<module>/main.py`.
