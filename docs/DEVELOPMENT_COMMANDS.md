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
pytest                      # Run full smoke test suite (11 tests)
pytest -v                   # Verbose
pytest -k "langgraph"       # Filter by name
pytest tests/test_smoke.py::test_tools_runs -v   # Single test
```

## Run Exercises by Module

> **Full catalog with expected output:** [src/README.md](../src/README.md)

### 01 — State Basics

```bash
python src/01_state_basics/hello_world.py
# Expected: {'message': 'hello | A | B'}
```

### 02 — LangGraph Basics

```bash
python src/02_langgraph_basics/basic_graph.py
# Expected: {'message': 'start -> A -> B'}
```

### 03 — LLM Nodes (requires API key)

```bash
export OPENAI_API_KEY=sk-your-key
python src/03_llm_nodes/llm_node.py
# Expected: {'response': '<LLM-generated text>'}
```

### 04 — Routing and Branches

```bash
python src/04_routing_and_branches/router.py
# Expected: {'intent': 'blocker'}
```

### 05 — Tools

```bash
python src/05_tools/mock_tool.py
# Expected: Slack sent: hello
```

### 06 — Memory Basics

```bash
python src/06_memory_basics/memory.py
# Expected: [{'event': 'login'}]
```

### 07 — Qdrant Integration (placeholder)

```bash
python src/07_qdrant_integration/mock_qdrant.py
# Expected: Qdrant placeholder
```

### 08 — Graph Memory Neo4j (placeholder)

```bash
python src/08_graph_memory_neo4j/mock_graph.py
# Expected: Neo4j placeholder
```

### 09 — Multi-Agent Systems

```bash
python src/09_multi_agent_systems/agents.py
# Expected: {'result': 'done'}
```

### 10 — Full Brain Simulation (stub)

```bash
python src/10_full_brain_simulation/brain.py
# Expected: Full Brain Simulation + banner line
```

### Shared utilities (no script)

```bash
pytest tests/test_smoke.py::test_shared_state_typeddict -v
```

## Run All Offline Exercises (batch)

```bash
for script in \
  src/01_state_basics/hello_world.py \
  src/02_langgraph_basics/basic_graph.py \
  src/04_routing_and_branches/router.py \
  src/05_tools/mock_tool.py \
  src/06_memory_basics/memory.py \
  src/07_qdrant_integration/mock_qdrant.py \
  src/08_graph_memory_neo4j/mock_graph.py \
  src/09_multi_agent_systems/agents.py \
  src/10_full_brain_simulation/brain.py; do
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
