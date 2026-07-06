
# 🧠 Agent Lab

A progressive hands-on laboratory for building AI agents using LangGraph, LangChain, memory systems, and graph-based reasoning.

## 🎯 Goal

Learn how to build a full **AI Agent Operating System** step by step:

- State machines
- LLM-powered agents
- Tool use
- Memory systems
- Vector databases (Qdrant)
- Graph reasoning (Neo4j)
- Multi-agent systems
- Full Brain simulation

---

## 📁 Structure

All exercises live under:

```
src/
```

Each folder contains:
- Code exercises
- A dedicated README explaining the concept

---

## 🚀 How to run

```bash
pip install -r requirements.txt   # or: pip install -e ".[dev]"
pytest                            # validate ALL offline exercises — no keys/services
python src/01_state_basics/main.py
make help                         # task runner: test, lint, typecheck, run, up/down
```

Everything is **offline-first**: the whole suite runs green with no API keys and
no external services (deterministic fakes + in-memory stores). Provide
`OPENAI_API_KEY`, `QDRANT_URL`, or `NEO4J_URI` in `.env` to activate real
backends automatically. See [docs/adr/0001-offline-first-fakes.md](docs/adr/0001-offline-first-fakes.md).

**Full exercise catalog** (every module, script, what it teaches):
[src/README.md](src/README.md) · **Learning path & pacing:** [docs/roadmap.md](docs/roadmap.md)
· **System handbook:** [docs/agent-architecture.md](docs/agent-architecture.md)

---

## 🧠 Curriculum — 9 tracks, 64 modules

A book + bootcamp + reference implementation for building production-grade AI
agent systems. Modules `01`–`10` are the on-ramp; `11`–`64` are grouped into
tracks that each build on the last.

| Track | Modules | Focus |
|-------|---------|-------|
| **0 — On-ramp** | 01–10 | State, graphs, LLM nodes, routing, tools, memory, Qdrant, Neo4j, multi-agent |
| **1 — Foundations** | 11–14 | Branching, parallel execution, async nodes, error handling |
| **2 — LLM Engineering** | 15–20 | Chat models, structured outputs, function calling, prompting, context, routing |
| **3 — Agent Engineering** | 21–28 | ReAct, planner, executor, reflection, router, planning loops, HITL, supervisor |
| **4 — Memory** | 29–36 | Conversation, episodic, semantic, procedural, write/retrieve/score/consolidate |
| **5 — Retrieval** | 37–42 | Embeddings, RAG, hybrid search, query rewriting, reranking, Qdrant |
| **6 — Graph Intelligence** | 43–47 | Neo4j, modeling, Cypher, dependency & root-cause analysis, org graphs |
| **7 — Multi-Agent** | 48–52 | Collaboration, negotiation, decomposition, shared memory, event buses |
| **8 — Production** | 53–58 | Observability, evaluations, testing, security, cost/multi-tenancy, deployment |
| **9 — Capstones** | 59–64 | Personal assistant, research/coding/incident agents, Company & Mini DailyBot Brain |

Start here → [docs/roadmap.md](docs/roadmap.md)
