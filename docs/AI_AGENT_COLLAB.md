# AI Agent Collaboration — Agent Lab

Rules for multiple agents and humans working on this repository.

## Ownership

- **One module at a time**: an agent working on `05_tools` should not also
  modify `03_llm_nodes` unless the plan explicitly spans modules.
- **Capstone (`10`)** is shared territory — coordinate via a Deep Work Plan so
  tasks do not conflict.

## Handoff Protocol

When handing work to another agent or human:

1. State which module(s) were touched.
2. List commands run (`pytest`, specific `python src/...` scripts).
3. Note any deferred items (e.g. "LLM test needs API key").
4. If a DWP was used, point to `.dwp/plans/PLAN_*/PROGRESS.md`.

## Conflict Avoidance

- Do not edit the same exercise file from parallel sessions without a plan.
- Module READMEs are the source of truth for exercise intent — reconcile code
  changes with README updates.
- `src/shared/` changes affect multiple downstream modules — treat as high-impact.

## Human ↔ Agent Expectations

- Humans may work through modules manually; agents should not skip ahead unless asked.
- Agents should explain concepts in module README terms, not replace the curriculum.
- Ask before replacing placeholder mocks (`07`, `08`) with real service integrations.

## Progress Reporting

After completing a module or 3+ file changes:

- Summarize what changed and why.
- Report test results.
- Never block active work waiting for reporting approval.

## Escalation

Stop and ask the developer when:

- A change requires real Qdrant, Neo4j, or other external infrastructure.
- Test strategy needs live API calls in CI.
- Module ordering or curriculum structure should change.
