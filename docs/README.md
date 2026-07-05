# Agent Lab Documentation

Spec-driven documentation for humans and AI agents working in this repository.

**Start here**: new agents should read [AI_AGENT_ONBOARDING.md](AI_AGENT_ONBOARDING.md),
then [AGENTS.md](../AGENTS.md) at the repository root.

## Guides

| Document | Description |
|----------|-------------|
| [PRODUCT_SPEC.md](PRODUCT_SPEC.md) | What Agent Lab is for and who it serves |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Module layout and learning-path data flow |
| [STANDARDS.md](STANDARDS.md) | Coding conventions and module structure |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | pytest smoke tests and manual validation |
| [DEVELOPMENT_COMMANDS.md](DEVELOPMENT_COMMANDS.md) | Full runnable command reference |
| [SECURITY.md](SECURITY.md) | API keys and sensitive data handling |
| [PERFORMANCE.md](PERFORMANCE.md) | Performance notes for LLM and data stores |
| [AI_AGENT_ONBOARDING.md](AI_AGENT_ONBOARDING.md) | First-session agent checklist |
| [AI_AGENT_COLLAB.md](AI_AGENT_COLLAB.md) | Multi-agent handoff and conflict rules |
| [overview.md](overview.md) | Conceptual overview of agent design patterns |

## Handbook (topical deep-dives)

The curriculum handbook — read alongside the modules. All pages are cross-linked
and include Mermaid diagrams.

| Document | Covers |
|----------|--------|
| [agent-architecture.md](agent-architecture.md) | System-level view: how the layers compose into an agent OS |
| [roadmap.md](roadmap.md) | The 9-track learning path, pacing, capstone progression |
| [glossary.md](glossary.md) | Vocabulary, each linked to the module that teaches it |
| [langgraph.md](langgraph.md) | Execution model: nodes, edges, branching, parallelism, async, errors |
| [langchain.md](langchain.md) | Messages, prompts, tools, structured output, runnables |
| [openai.md](openai.md) | Chat/embedding models, tokens, cost, real-vs-fake backends |
| [tools.md](tools.md) | Tool design, schemas, manual tool loops, safety |
| [memory.md](memory.md) | Conversation/episodic/semantic/procedural memory, write/retrieve/score/decay |
| [rag.md](rag.md) | Retrieval-Augmented Generation, hybrid search, rewriting, reranking |
| [qdrant.md](qdrant.md) | Vector database integration (real + in-memory fallback) |
| [neo4j.md](neo4j.md) | Property graphs, Cypher, graph reasoning |
| [multi-agent.md](multi-agent.md) | Collaboration, negotiation, decomposition, shared memory, event buses |
| [observability.md](observability.md) | Structured logging, traces, spans, metrics |
| [testing.md](testing.md) | Testing nondeterministic agents |
| [agent-security.md](agent-security.md) | Prompt-injection defenses, input validation (agent-side security) |
| [MODULE_TEMPLATE.md](MODULE_TEMPLATE.md) | The canonical anatomy every module follows |
| [adr/](adr/README.md) | Architecture Decision Records (offline-first, shared boundary, numbering) |

> Naming note: `agent-architecture.md` and `agent-security.md` avoid a
> case-insensitive-filesystem collision with the existing `ARCHITECTURE.md` and
> `SECURITY.md` (which cover module layout and secret handling respectively).

## Common Tasks

| Task | Go to |
|------|-------|
| Run an exercise | [src/README.md](../src/README.md) or [DEVELOPMENT_COMMANDS.md](DEVELOPMENT_COMMANDS.md) |
| Understand module order | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Validate changes | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Handle API keys | [SECURITY.md](SECURITY.md) |

## Conceptual Overview

The original [overview.md](overview.md) describes LangGraph architecture, memory
systems, agent design patterns, graph reasoning, and multi-agent systems at a
high level. The guides above add repo-specific, actionable detail.
