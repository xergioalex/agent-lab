# Agent Lab — Agent Guide

Progressive hands-on laboratory for building AI agents with LangGraph, LangChain,
memory systems, and graph-based reasoning.

## Documentation Index

| Document | Description |
|----------|-------------|
| [docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md) | What Agent Lab is for and who it serves |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Module layout, learning path, and data flow |
| [docs/STANDARDS.md](docs/STANDARDS.md) | Coding conventions and module structure |
| [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) | How to validate exercises and changes |
| [docs/DEVELOPMENT_COMMANDS.md](docs/DEVELOPMENT_COMMANDS.md) | Full command reference |
| [docs/SECURITY.md](docs/SECURITY.md) | API keys, secrets, and sensitive data |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | Performance notes for LLM and vector workloads |
| [docs/AI_AGENT_ONBOARDING.md](docs/AI_AGENT_ONBOARDING.md) | First-session checklist for agents |
| [docs/AI_AGENT_COLLAB.md](docs/AI_AGENT_COLLAB.md) | Multi-agent and human handoff rules |
| [docs/overview.md](docs/overview.md) | Conceptual overview of agent patterns |
| [docs/README.md](docs/README.md) | Master index for all documentation |

### Learning Modules

| Module | Description |
|--------|-------------|
| [src/01_state_basics/](src/01_state_basics/README.md) | State as dict transformations |
| [src/02_langgraph_basics/](src/02_langgraph_basics/README.md) | LangGraph `StateGraph` fundamentals |
| [src/03_llm_nodes/](src/03_llm_nodes/README.md) | LLM-powered nodes via LangChain |
| [src/04_routing_and_branches/](src/04_routing_and_branches/README.md) | Conditional routing logic |
| [src/05_tools/](src/05_tools/README.md) | Tool use patterns |
| [src/06_memory_basics/](src/06_memory_basics/README.md) | In-memory event storage |
| [src/07_qdrant_integration/](src/07_qdrant_integration/README.md) | Vector database integration |
| [src/08_graph_memory_neo4j/](src/08_graph_memory_neo4j/README.md) | Graph memory with Neo4j |
| [src/09_multi_agent_systems/](src/09_multi_agent_systems/README.md) | Planner/executor multi-agent |
| [src/10_full_brain_simulation/](src/10_full_brain_simulation/README.md) | Full agent OS capstone |
| [src/shared/](src/shared/README.md) | Shared `State` type and config |

### Agent Kit

| Resource | Description |
|----------|-------------|
| [.agents/README.md](.agents/README.md) | Cross-agent configuration home |
| [.agents/docs/skills_agents_catalog.md](.agents/docs/skills_agents_catalog.md) | Skills and agents catalog |
| [.agents/docs/COMMANDS_REFERENCE.md](.agents/docs/COMMANDS_REFERENCE.md) | Slash command reference |

## Repository Structure

```
agent-lab/
├── AGENTS.md              # This file — agent entry point
├── CLAUDE.md              # Symlink → AGENTS.md
├── README.md              # Human-facing project intro
├── requirements.txt       # Python dependencies (pip)
├── docs/                  # Spec-driven documentation hub
├── src/                   # Numbered learning modules (01–10) + shared/
│   ├── 01_state_basics/
│   ├── 02_langgraph_basics/
│   ├── …                  # modules 03–09
│   ├── 10_full_brain_simulation/
│   └── shared/            # Shared types and config
├── tests/                 # pytest smoke tests (no API keys required)
├── .agents/               # Cross-agent kit (skills, agents, commands)
├── .dwp/                  # Gitignored Deep Work Plan output
└── tmp/                   # Gitignored scratch space
```

## Mandatory Rules

### Language

All code, comments, commit messages, and documentation **MUST** be in English.

### Conventional Commits

Commits **MUST** follow `type(scope): description`.

Valid scopes: `state`, `langgraph`, `llm`, `routing`, `tools`, `memory`,
`qdrant`, `neo4j`, `multi-agent`, `brain`, `shared`, `docs`, `agents`, `deps`.

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.

### Testing

- Run `pytest` from the repository root before marking work complete.
- Smoke tests in `tests/test_smoke.py` cover modules that do not require API keys.
- Modules `03_llm_nodes` and later LLM-dependent exercises require `OPENAI_API_KEY`
  and are validated manually until mocked tests are added.
- Target coverage: exercise scripts run without error; pytest smoke suite passes.

### Error Handling and Logging

- Exercise scripts use `print()` for learning output — keep output readable.
- Production-style error handling is introduced in later modules; match the style
  of the module you are editing.
- Never swallow exceptions silently in new code.

### Repository Boundaries

- Commit only from this repository root.
- Do not commit `.env`, API keys, or `.dwp/` plan artifacts.
- Use `tmp/` for throwaway experiments; use `.dwp/` for structured plans.
- Do not modify unrelated modules when working on a single exercise.

### Progress Reporting

Report progress after completing a module or significant change. Never block
active work waiting for reporting approval.

## Quick Commands

| Action | Command |
|--------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Run smoke tests | `pytest` |
| Run smoke tests (verbose) | `pytest -v` |
| Run a single module script | `python src/<module>/<script>.py` |
| State basics exercise | `python src/01_state_basics/hello_world.py` |
| LangGraph basics exercise | `python src/02_langgraph_basics/basic_graph.py` |
| LLM node exercise (needs API key) | `OPENAI_API_KEY=... python src/03_llm_nodes/llm_node.py` |
| Create a Deep Work Plan | `/dwp-create <goal>` |
| Execute current plan | `/dwp-execute` |
| Verify repo conformance | `/dwp-verify` |

## Working Directories

- **`.dwp/`** — structured Deep Work Plan output (`plans/`, `drafts/`). Gitignored.
- **`tmp/`** — unstructured scratch space for experiments. Gitignored.
