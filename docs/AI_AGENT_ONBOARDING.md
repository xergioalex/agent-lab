# AI Agent Onboarding — Agent Lab

First-session checklist for an AI coding agent new to this repository.

## 1. Orient

1. Read [AGENTS.md](../AGENTS.md) — index, rules, and quick commands.
2. Read [PRODUCT_SPEC.md](PRODUCT_SPEC.md) — understand this is a learning lab.
3. Skim [ARCHITECTURE.md](ARCHITECTURE.md) — module progression 01→10.

## 2. Set Up

```bash
cd /path/to/agent-lab
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Validate

```bash
pytest                                    # Must pass — no API key needed
python src/01_state_basics/hello_world.py # Quick sanity check
python src/02_langgraph_basics/basic_graph.py
```

## 4. Understand the Learning Path

Work modules in order unless the user directs otherwise:

| Order | Module | New concept |
|-------|--------|-------------|
| 1 | `01_state_basics` | State as dict |
| 2 | `02_langgraph_basics` | StateGraph |
| 3 | `03_llm_nodes` | LLM nodes |
| 4 | `04_routing_and_branches` | Routing |
| 5 | `05_tools` | Tools |
| 6 | `06_memory_basics` | Memory |
| 7 | `07_qdrant_integration` | Vectors |
| 8 | `08_graph_memory_neo4j` | Graph memory |
| 9 | `09_multi_agent_systems` | Multi-agent |
| 10 | `10_full_brain_simulation` | Capstone |

## 5. Where Things Live

- **Exercises**: `src/NN_*/`
- **Shared types**: `src/shared/`
- **Docs**: `docs/`
- **Agent kit**: `.agents/`
- **Plans**: `.dwp/` (gitignored)
- **Scratch**: `tmp/` (gitignored)

## 6. Before Making Changes

- Read the target module's `README.md` first.
- Run `pytest` after code changes.
- Do not cross-import between numbered modules.
- For LLM work, confirm `OPENAI_API_KEY` is available or use mocks.

## 7. Structured Work

For non-trivial tasks, use Deep Work Plans:

```
/dwp-create <goal>
/dwp-execute
```

## 8. Done Criteria

- Smoke tests pass
- Module README updated if behavior changed
- No secrets committed
