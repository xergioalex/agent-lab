# Agent Lab — Exercise Index

Progressive hands-on exercises under `src/`. Run every script from the **repository root**.

## Prerequisites

```bash
pip install -r requirements.txt
```

Optional for module 03 only:

```bash
export OPENAI_API_KEY=sk-your-key   # never commit this value
```

## Quick validation

Run the full offline smoke suite (covers modules 01, 02, 04–10 and shared state):

```bash
pytest
```

Module 03 is validated separately — it requires `OPENAI_API_KEY` (see below).

---

## Exercise catalog

| # | Module | Script | API key | Status |
|---|--------|--------|---------|--------|
| 01 | [State basics](01_state_basics/) | `hello_world.py` | No | Runnable |
| 02 | [LangGraph basics](02_langgraph_basics/) | `basic_graph.py` | No | Runnable |
| 03 | [LLM nodes](03_llm_nodes/) | `llm_node.py` | **Yes** | Runnable (needs key) |
| 04 | [Routing & branches](04_routing_and_branches/) | `router.py` | No | Runnable |
| 05 | [Tools](05_tools/) | `mock_tool.py` | No | Runnable |
| 06 | [Memory basics](06_memory_basics/) | `memory.py` | No | Runnable |
| 07 | [Qdrant integration](07_qdrant_integration/) | `mock_qdrant.py` | No | Placeholder |
| 08 | [Graph memory (Neo4j)](08_graph_memory_neo4j/) | `mock_graph.py` | No | Placeholder |
| 09 | [Multi-agent systems](09_multi_agent_systems/) | `agents.py` | No | Runnable |
| 10 | [Full brain simulation](10_full_brain_simulation/) | `brain.py` | No | Stub |
| — | [Shared utilities](shared/) | — | No | Library (no script) |

---

## Run every script

### 01 — State basics

```bash
python src/01_state_basics/hello_world.py
```

**Expected output:**

```
{'message': 'hello | A | B'}
```

**What it teaches:** State is a dict passed through node functions that mutate and return it.

---

### 02 — LangGraph basics

```bash
python src/02_langgraph_basics/basic_graph.py
```

**Expected output:**

```
{'message': 'start -> A -> B'}
```

**What it teaches:** A `StateGraph` with two nodes (`A` → `B`) and compiled invocation.

---

### 03 — LLM nodes (requires API key)

```bash
export OPENAI_API_KEY=sk-your-key
python src/03_llm_nodes/llm_node.py
```

**Expected output:** A dict with an LLM-generated `response` field, for example:

```
{'response': 'Hello! How can I assist you today?'}
```

Exact text varies per model call. Without `OPENAI_API_KEY` the script exits with an
OpenAI credentials error — this is expected.

**What it teaches:** Calling `ChatOpenAI` from a node function.

---

### 04 — Routing and branches

```bash
python src/04_routing_and_branches/router.py
```

**Expected output:**

```
{'intent': 'blocker'}
```

**What it teaches:** Conditional routing based on message content (`"block"` → blocker intent).

---

### 05 — Tools

```bash
python src/05_tools/mock_tool.py
```

**Expected output:**

```
Slack sent: hello
```

**What it teaches:** A mock external tool (Slack) returning a formatted result.

---

### 06 — Memory basics

```bash
python src/06_memory_basics/memory.py
```

**Expected output:**

```
[{'event': 'login'}]
```

**What it teaches:** In-memory event log with `write()` and `read()` helpers.

---

### 07 — Qdrant integration (placeholder)

```bash
python src/07_qdrant_integration/mock_qdrant.py
```

**Expected output:**

```
Qdrant placeholder
```

**What it teaches:** Stub for future vector-database / embedding exercises.

---

### 08 — Graph memory Neo4j (placeholder)

```bash
python src/08_graph_memory_neo4j/mock_graph.py
```

**Expected output:**

```
Neo4j placeholder
```

**What it teaches:** Stub for future graph-database / relationship exercises.

---

### 09 — Multi-agent systems

```bash
python src/09_multi_agent_systems/agents.py
```

**Expected output:**

```
{'result': 'done'}
```

**What it teaches:** Planner → executor pipeline where each agent enriches shared state.

---

### 10 — Full brain simulation (stub)

```bash
python src/10_full_brain_simulation/brain.py
```

**Expected output:**

```
Full Brain Simulation
This will combine all systems together
```

**What it teaches:** Capstone placeholder that will eventually combine memory, tools,
graph, LLM, and routing.

---

### Shared utilities (no script)

Import-only helpers used by later modules:

| File | Purpose |
|------|---------|
| `shared/state.py` | `State` TypedDict with `message: str` |
| `shared/config.py` | `OPENAI_MODEL = "gpt-4o-mini"` |

Validated by `pytest` via import check — no standalone script to run.

---

## Run all offline scripts at once

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

Then run the LLM module separately when you have a key:

```bash
export OPENAI_API_KEY=sk-your-key
python src/03_llm_nodes/llm_node.py
```

---

## Further reading

- [docs/DEVELOPMENT_COMMANDS.md](../docs/DEVELOPMENT_COMMANDS.md) — full command reference
- [docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) — pytest and validation gates
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — learning path and data flow
