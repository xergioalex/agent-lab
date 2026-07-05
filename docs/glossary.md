# Glossary — Agent Lab

Core vocabulary, each with a one-line definition and the module that teaches it.

## Execution & graphs

- **State** — the typed dict passed between nodes. → [01](../src/01_state_basics/), [`AgentState`](../src/shared/state.py)
- **Node** — a function `state -> partial state`. → [02](../src/02_langgraph_basics/)
- **Edge** — a transition between nodes; **conditional edge** routes on state. → [11](../src/11_graph_branching/)
- **Super-step** — one synchronized round of node execution; parallel nodes run within one. → [12](../src/12_parallel_execution/)
- **Reducer** — a function that merges concurrent updates to a state channel (e.g. `add_messages`, `operator.add`). → [12](../src/12_parallel_execution/)
- **`Send`** — a directive to fan a node out over many inputs (map-reduce). → [12](../src/12_parallel_execution/)
- **Async node** — an `async def` node awaited via `ainvoke`. → [13](../src/13_async_nodes/)
- **Checkpoint** — a saved graph state (via `MemorySaver`) enabling resume & HITL. → [16](../src/16_structured_outputs/), [27](../src/27_human_in_the_loop/)

## LLM engineering

- **Chat model** — a message-in/message-out LLM (`ChatOpenAI` or the offline fake). → [15](../src/15_chat_models/)
- **Structured output** — forcing the model to emit a validated Pydantic object. → [16](../src/16_structured_outputs/)
- **Function / tool calling** — the model requests a tool; the runtime executes it and returns the result. → [17](../src/17_function_calling/)
- **Prompt template** — a parameterized message list (`ChatPromptTemplate`). → [18](../src/18_prompt_engineering/)
- **Context engineering** — budgeting/trimming/summarizing what fits in the window. → [19](../src/19_context_engineering/)
- **Model routing** — sending a request to a cheaper or stronger model by difficulty. → [20](../src/20_model_routing/)

## Agents

- **ReAct** — interleaved Reason → Act → Observe loop. → [21](../src/21_react_agent/)
- **Planner / Executor** — split "decide the steps" from "run the steps". → [22](../src/22_planner_agent/), [23](../src/23_executor_agent/)
- **Reflection** — self-critique then revise. → [24](../src/24_reflection/)
- **Router agent** — classify intent, dispatch to a sub-graph. → [25](../src/25_router_agent/)
- **Planning loop** — plan → execute → replan until done (bounded). → [26](../src/26_planning_loops/)
- **Human-in-the-loop (HITL)** — pause at `interrupt()`, get human input, resume with `Command`. → [27](../src/27_human_in_the_loop/)
- **Supervisor** — an agent that orchestrates worker agents. → [28](../src/28_supervisor/)

## Memory

- **Conversation memory** — the running message buffer/window. → [29](../src/29_conversation_memory/)
- **Episodic memory** — timestamped events/episodes. → [30](../src/30_episodic_memory/)
- **Semantic memory** — facts stored/retrieved via embeddings. → [31](../src/31_semantic_memory/)
- **Procedural memory** — learned how-to procedures. → [32](../src/32_procedural_memory/)
- **Memory scoring** — relevance + recency + importance ranking. → [35](../src/35_memory_scoring/)
- **Consolidation / decay** — merging duplicates and forgetting stale traces. → [36](../src/36_memory_consolidation_decay/)

## Retrieval

- **Embedding** — a vector representation of text; similarity via cosine. → [37](../src/37_embeddings/)
- **RAG** — Retrieval-Augmented Generation: retrieve → augment prompt → generate. → [38](../src/38_rag_fundamentals/)
- **Hybrid search** — fusing dense (vector) and sparse (keyword/BM25) results. → [39](../src/39_hybrid_search/)
- **Query rewriting** — expanding/reformulating the query (multi-query, HyDE). → [40](../src/40_query_rewriting/)
- **Reranking** — reordering candidates with a stronger scorer. → [41](../src/41_reranking/)

## Graph

- **Property graph** — nodes with labels/properties + typed, directed relationships. → [43](../src/43_neo4j_basics/)
- **Cypher** — Neo4j's graph query language. → [44](../src/44_graph_modeling_cypher/)
- **Dependency / root-cause analysis** — traversal to find order, cycles, and blast radius. → [45](../src/45_dependency_analysis/), [46](../src/46_root_cause_analysis/)

## Multi-agent & production

- **Blackboard / shared memory** — a shared workspace multiple agents read/write. → [51](../src/51_shared_memory/)
- **Event bus** — pub/sub message routing between agents. → [52](../src/52_event_bus/)
- **Observability / trace / span** — structured recording of a run's steps and metrics. → [53](../src/53_observability/)
- **Evaluation** — scoring outputs against a golden set. → [54](../src/54_evaluations/)
- **Prompt injection** — malicious input trying to hijack the model; defended by validation/sanitization. → [56](../src/56_security/)
- **Multi-tenancy** — isolating state/memory per tenant. → [57](../src/57_cost_and_multitenancy/)
