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

1. **Sixty-four numbered modules** (`01`–`64`) in a progressive curriculum
2. **Runnable `main.py` exercises** — offline-first with optional real backends
3. **Per-module READMEs** with objectives, architecture diagrams, and run commands
4. **On-ramp capstone** (`10`) and **full capstone** (`64`) integrating all subsystems

## Success Criteria

- A learner can run module `01` with only `pip install` and `python`
- Each subsequent module introduces exactly one new concept
- An agent can navigate the repo using `AGENTS.md` and module READMEs alone
- Smoke tests pass without API keys for offline modules

## Non-Goals

- Production deployment or hosting
- A polished CLI or web UI
- Optional real Qdrant/Neo4j via Docker — exercises default to in-memory fakes
- Replacing official LangGraph or LangChain documentation

## Product Positioning

Think of Agent Lab as a **structured workbook**: each folder is a chapter, each
script is an exercise, and the README is the lesson. The "users" are learners and
the agents helping them complete the curriculum.
