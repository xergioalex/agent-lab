# 10 — Full Brain Simulation

## Learning Objectives

After this module you can:

- Integrate routing, episodic memory, RAG, graph memory, and tools in **one**
  LangGraph coordinator.
- Trace a request through `plan` → specialist nodes → optional tool loop → `aggregate`.
- Explain how module `64` extends this on-ramp capstone with observability and
  multi-turn session memory.
- Name which earlier module (`01`–`09`) supplies each subsystem in the brain.

## Theory

Modules `01`–`09` each taught one capability. A production agent needs them
**composed**: classify which knowledge sources apply, let specialists contribute,
optionally execute tools, then merge findings into one answer.

`main.py` implements a working mini brain:

- **plan** — keyword router picks `memory`, `graph`, `rag`, `tools` subsystems.
- **memory / graph / rag** — specialist nodes write into `context.findings`.
- **agent ↔ tools** — conditional loop when `tools` is needed (`create_task`, `send_slack`).
- **aggregate** — merges findings (+ tool observations) into the final reply.

Module `64` adds structured observability logging and multi-turn `memory_log` persistence.

## Mental Models

Think of modules `01`–`09` as rooms in a house. Module `10` is the hallway system
that connects them: one front desk (`plan`) decides which rooms to visit, then a
concierge (`aggregate`) writes the unified answer.

## Architecture

```mermaid
flowchart TD
    START([START]) --> plan["plan: _needed_subsystems"]
    plan --> memory["memory_specialist"]
    memory --> graph["graph_specialist"]
    graph --> rag["rag_specialist"]
    rag --> route_tools{"tools needed?"}
    route_tools -->|yes| agent["agent: bind_tools"]
    agent --> route_model{"tool_calls?"}
    route_model -->|yes| tools["tools: ToolNode"]
    tools --> agent
    route_model -->|no| aggregate["aggregate"]
    route_tools -->|no| aggregate
    aggregate --> END([END])
```

Legend: specialists always run in sequence; tools are optional via conditional edges.

Flow notes:

- `plan` inspects the latest human message and sets `context.needed`.
- Specialists no-op when not listed in `needed` — pattern reused in modules `63`/`64`.
- `aggregate` builds `answer` from `[subsystem] finding` parts and appends to `memory_log`.

## Runnable Example

```bash
python src/10_full_brain_simulation/main.py
```

## Expected output

```
=== Full Brain Simulation ===
needed_subsystems=['graph', 'rag', 'tools']
answer='[graph] Engineering led by Carol || [rag] Production deploys require ... || [tools] Created task ...'
=== MODULE 10: FULL BRAIN SIMULATION COMPLETE ===
```

Exact tool observations vary slightly offline vs. live LLM; subsystem list is stable.

## Challenge

1. Add an LLM synthesis node after `aggregate` that rewrites findings as one paragraph.
2. Run two turns in one script and prove `memory_log` grows between turns.
3. Diagram module `64` and label every node that module `10` does not yet have.

## Stretch Goals

- Add a `route_intent` node from module `04` before `plan`.
- Log `subsystems=[...] tool_calls=N` like module `64` does.

## Common Mistakes

- **Running specialists in parallel without shared plan** — `plan` must set
  `needed` before specialists execute.
- **Hard-coding all subsystems every turn** — respect `needed` so nodes no-op when irrelevant.
- **Skipping the tool loop** — some requests require action, not just retrieval.

## Best Practices

- Keep each subsystem in its own node — composition, not a monolith.
- Use `context.findings` as the shared blackboard between specialists.
- End with a deterministic banner (`=== MODULE 10: ... ===`) for smoke tests.

## References

- Module [`64_mini_dailybot_brain`](../64_mini_dailybot_brain/README.md) — full capstone.
- Module [`63_company_brain`](../63_company_brain/README.md) — specialist pattern without tools loop.
- Modules [`04`](../04_routing_and_branches/README.md), [`06`](../06_memory_basics/README.md),
  [`07`](../07_qdrant_integration/README.md), [`08`](../08_graph_memory_neo4j/README.md),
  [`09`](../09_multi_agent_systems/README.md) — subsystem building blocks.
- [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) — curriculum map.

## What Comes Next

Track 1 continues at module [`11_graph_branching`](../11_graph_branching/README.md)
with advanced LangGraph routing patterns, then Tracks 2–9 deepen each subsystem.

## Automated test

Covered by `pytest` — `test_brain_simulation_runs` in `tests/test_smoke.py`.
