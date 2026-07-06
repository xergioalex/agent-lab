# Development Commands — Agent Lab

Authoritative command reference. All commands run from the repository root.

## Setup

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

## Testing

```bash
pytest                      # Run full smoke test suite (65 tests)
pytest -v                   # Verbose
pytest -k "langgraph"       # Filter by name
pytest tests/test_smoke.py::test_tools_runs -v   # Single test
```

## Run Exercises by Module

> **Full catalog with expected output:** [src/README.md](../src/README.md)

### 01 — State Basics

```bash
python src/01_state_basics/main.py
# Multi-stage pipeline: classify → enrich → validate → route → format
```

### 02 — LangGraph Basics

```bash
python src/02_langgraph_basics/main.py
# 8-node graph with conditional routing after validate
```

### 03 — LLM Nodes (offline by default)

```bash
python src/03_llm_nodes/main.py
# Optional: export OPENAI_API_KEY=sk-your-key for real ChatOpenAI
```

### 04 — Routing and Branches

```bash
python src/04_routing_and_branches/main.py
# 4-way intent router (blocker, billing, technical, general)
```

### 05 — Tools

```bash
python src/05_tools/main.py
# Agent ↔ ToolNode loop (Slack tool)
```

### 06 — Memory Basics

```bash
python src/06_memory_basics/main.py
# Episodic event log inside a LangGraph
```

### 07 — Qdrant Integration

```bash
python src/07_qdrant_integration/main.py
# Vector index + similarity search (InMemoryVectorStore; Qdrant when QDRANT_URL set)
```

### 08 — Graph Memory Neo4j

```bash
python src/08_graph_memory_neo4j/main.py
# Org-graph traversal (InMemoryGraphStore; Neo4j when NEO4J_URI set)
```

### 09 — Multi-Agent Systems

```bash
python src/09_multi_agent_systems/main.py
# Planner → executor → critic with replan loop
```

### 10 — Full Brain Simulation

```bash
python src/10_full_brain_simulation/main.py
# Integrated routing + memory + RAG + graph + tools (deepened in module 64)
```

### Run any module

```bash
make run MODULE=01_state_basics
```

### Optional backends

```bash
make up    # docker compose -f docker-compose.yml up -d  (Qdrant + Neo4j)
```

### Shared utilities (no script)

```bash
pytest tests/test_smoke.py::test_shared_state_typeddict -v
```

## Run All Offline Exercises (batch)

```bash
for script in \
  src/01_state_basics/main.py \
  src/02_langgraph_basics/main.py \
  src/04_routing_and_branches/main.py \
  src/05_tools/main.py \
  src/06_memory_basics/main.py \
  src/07_qdrant_integration/main.py \
  src/08_graph_memory_neo4j/main.py \
  src/09_multi_agent_systems/main.py \
  src/10_full_brain_simulation/main.py; do
  echo "=== $script ==="
  python "$script"
done
```

## Deep Work Plan Commands

These route to the installed `deepworkplan` skill via `.agents/commands/`:

| Command | Purpose |
|---------|---------|
| `/dwp-create <goal>` | Create a structured plan |
| `/dwp-execute` | Execute plan tasks with validation gates |
| `/dwp-refine` | Modify an in-progress plan |
| `/dwp-resume` | Continue an interrupted plan |
| `/dwp-status` | Report plan progress |
| `/dwp-verify` | Check repository conformance |

## Environment Variables

| Variable | Required for | Notes |
|----------|--------------|-------|
| `OPENAI_API_KEY` | `03_llm_nodes` and later LLM work | Never commit; use `.env` locally |

## Scratch Space

```bash
# Ephemeral experiments — gitignored
mkdir -p tmp/scratch
```

Structured plan output goes in `.dwp/`, not `tmp/`.

## Related docs

| Document | Purpose |
|----------|---------|
| [src/README.md](../src/README.md) | Master exercise index with expected output |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | pytest coverage and validation gates |
| [SECURITY.md](SECURITY.md) | API key handling |
