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

## Advanced curriculum — Tracks 1–9 (modules 11–64)

All modules below are **offline-first** (no API key, no services). Each folder has
a full README (objectives, theory, Mermaid diagrams, runnable example, challenges,
best practices, references) — open it for the exact run command. Design rationale:
[docs/roadmap.md](../docs/roadmap.md) · [docs/agent-architecture.md](../docs/agent-architecture.md).

### Track 1 — Foundations · [docs/langgraph.md](../docs/langgraph.md)
| # | Module | Teaches |
|---|--------|---------|
| 11 | [graph_branching](11_graph_branching/) | Conditional edges & multi-way branching |
| 12 | [parallel_execution](12_parallel_execution/) | Fan-out/fan-in with `Send` + reducers |
| 13 | [async_nodes](13_async_nodes/) | `async` nodes, `ainvoke`, concurrency |
| 14 | [error_handling](14_error_handling/) | Retries, backoff, fallbacks, circuit breaker |

### Track 2 — LLM Engineering · [docs/langchain.md](../docs/langchain.md) · [docs/openai.md](../docs/openai.md)
| # | Module | Teaches |
|---|--------|---------|
| 15 | [chat_models](15_chat_models/) | Typed messages & the model bridge |
| 16 | [structured_outputs](16_structured_outputs/) | Pydantic `with_structured_output` + retry |
| 17 | [function_calling](17_function_calling/) | `bind_tools` + manual tool loop |
| 18 | [prompt_engineering](18_prompt_engineering/) | Templates, system prompts, few-shot |
| 19 | [context_engineering](19_context_engineering/) | Trimming & summarization memory |
| 20 | [model_routing](20_model_routing/) | Route by difficulty/cost |

### Track 3 — Agent Engineering · [docs/tools.md](../docs/tools.md)
| # | Module | Teaches |
|---|--------|---------|
| 21 | [react_agent](21_react_agent/) | Reason→act→observe loop |
| 22 | [planner_agent](22_planner_agent/) | Plan generation |
| 23 | [executor_agent](23_executor_agent/) | Executing plan steps |
| 24 | [reflection](24_reflection/) | Self-critique & revise |
| 25 | [router_agent](25_router_agent/) | Intent routing to sub-graphs |
| 26 | [planning_loops](26_planning_loops/) | Plan → execute → replan |
| 27 | [human_in_the_loop](27_human_in_the_loop/) | `interrupt`/`Command` approve-resume |
| 28 | [supervisor](28_supervisor/) | Supervisor over worker agents |

### Track 4 — Memory · [docs/memory.md](../docs/memory.md)
| # | Module | Teaches |
|---|--------|---------|
| 29 | [conversation_memory](29_conversation_memory/) | Buffer/window/summary |
| 30 | [episodic_memory](30_episodic_memory/) | Timestamped episodes |
| 31 | [semantic_memory](31_semantic_memory/) | Facts in the vector store |
| 32 | [procedural_memory](32_procedural_memory/) | Learned procedures |
| 33 | [memory_writer](33_memory_writer/) | Extract → classify → store |
| 34 | [memory_retrieval](34_memory_retrieval/) | Query → rank → assemble |
| 35 | [memory_scoring](35_memory_scoring/) | Relevance + recency + importance |
| 36 | [memory_consolidation_decay](36_memory_consolidation_decay/) | Consolidation & forgetting |

### Track 5 — Retrieval · [docs/rag.md](../docs/rag.md) · [docs/qdrant.md](../docs/qdrant.md)
| # | Module | Teaches |
|---|--------|---------|
| 37 | [embeddings](37_embeddings/) | Vectors, cosine, chunking |
| 38 | [rag_fundamentals](38_rag_fundamentals/) | Retrieve → augment → generate |
| 39 | [hybrid_search](39_hybrid_search/) | Dense + keyword fusion |
| 40 | [query_rewriting](40_query_rewriting/) | Multi-query / HyDE |
| 41 | [reranking](41_reranking/) | Cross-encoder-style rerank |
| 42 | [qdrant_production](42_qdrant_production/) | Real Qdrant + in-memory fallback |

### Track 6 — Graph Intelligence · [docs/neo4j.md](../docs/neo4j.md)
| # | Module | Teaches |
|---|--------|---------|
| 43 | [neo4j_basics](43_neo4j_basics/) | Nodes/relationships + fallback |
| 44 | [graph_modeling_cypher](44_graph_modeling_cypher/) | Modeling + Cypher queries |
| 45 | [dependency_analysis](45_dependency_analysis/) | Topo-sort & cycle detection |
| 46 | [root_cause_analysis](46_root_cause_analysis/) | Upstream traversal & blast radius |
| 47 | [organizational_graph](47_organizational_graph/) | People/teams/projects queries |

### Track 7 — Multi-Agent · [docs/multi-agent.md](../docs/multi-agent.md)
| # | Module | Teaches |
|---|--------|---------|
| 48 | [agent_collaboration](48_agent_collaboration/) | Cooperation on shared state |
| 49 | [negotiation](49_negotiation/) | Propose/critique negotiation |
| 50 | [task_decomposition](50_task_decomposition/) | Decompose → assign → gather |
| 51 | [shared_memory](51_shared_memory/) | Blackboard memory |
| 52 | [event_bus](52_event_bus/) | Pub/sub event bus |

### Track 8 — Production · [observability](../docs/observability.md) · [testing](../docs/testing.md) · [agent-security](../docs/agent-security.md)
| # | Module | Teaches |
|---|--------|---------|
| 53 | [observability](53_observability/) | Structured logs, spans, run tree |
| 54 | [evaluations](54_evaluations/) | Golden sets & scorers |
| 55 | [testing_agents](55_testing_agents/) | Testing nondeterministic agents |
| 56 | [security](56_security/) | Injection defenses & input validation |
| 57 | [cost_and_multitenancy](57_cost_and_multitenancy/) | Token/cost accounting & isolation |
| 58 | [deployment](58_deployment/) | Docker, CI/CD, deployment shapes |

### Track 9 — Final Projects (capstones)
| # | Module | Integrates |
|---|--------|-----------|
| 59 | [personal_assistant](59_personal_assistant/) | Memory + tools + routing |
| 60 | [research_agent](60_research_agent/) | Planner + RAG + reflection |
| 61 | [coding_agent](61_coding_agent/) | Tool-using code loop |
| 62 | [incident_response_agent](62_incident_response_agent/) | Graph RCA + tools |
| 63 | [company_brain](63_company_brain/) | Memory + RAG + graph + multi-agent |
| 64 | [mini_dailybot_brain](64_mini_dailybot_brain/) | The whole curriculum |

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
