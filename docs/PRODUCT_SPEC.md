# Product Specification — Agent Lab

## Problem

Building production AI agents requires understanding state machines, graph
orchestration, tool use, memory, vector search, and multi-agent coordination.
Most tutorials cover these topics in isolation, leaving developers without a
coherent path from "hello state" to a working agent operating system.

## Who It Is For

- Developers learning LangGraph and LangChain hands-on
- Engineers prototyping agent architectures before production adoption
- AI coding agents extending or completing the exercise curriculum

## Key Capabilities

Agent Lab is a **progressive learning laboratory** — not a deployed product. It
delivers:

1. **Ten numbered modules** (`01`–`10`) that build on each other
2. **Runnable Python exercises** demonstrating one concept per module
3. **Per-module READMEs** explaining the concept before the code
4. **A capstone** (`10_full_brain_simulation`) that combines all systems

## Success Criteria

- A learner can run module `01` with only `pip install` and `python`
- Each subsequent module introduces exactly one new concept
- An agent can navigate the repo using `AGENTS.md` and module READMEs alone
- Smoke tests pass without API keys for offline modules

## Non-Goals

- Production deployment or hosting
- A polished CLI or web UI
- Complete implementations of Qdrant, Neo4j, or Slack integrations (mocks/placeholders
  are used where external services would be required)
- Replacing official LangGraph or LangChain documentation

## Product Positioning

Think of Agent Lab as a **structured workbook**: each folder is a chapter, each
script is an exercise, and the README is the lesson. The "users" are learners and
the agents helping them complete the curriculum.
