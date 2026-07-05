# ADR 0003: Module numbering and track structure

**Status:** Accepted

## Context

The curriculum grew from 10 intro exercises to 64 modules. Learners need a clear,
stable path; agents building the modules need unambiguous, conflict-free targets.

## Decision

- **Stable numeric prefixes** (`NN_snake_case`) define both order and identity.
  Numbering is **frozen**: existing `01`–`10` are preserved as the on-ramp;
  new modules are `11`–`64` and are never renumbered.
- Modules are grouped into **9 tracks** (Foundations, LLM Engineering, Agent
  Engineering, Memory, Retrieval, Graph Intelligence, Multi-Agent, Production,
  Final Projects). Tracks are the pedagogical overlay; the number is the address.
- Each track owns disjoint `src/` folders, its topical `docs/*.md` page(s), and
  its own `tests/test_track<k>_*.py` file — so tracks can be built in parallel
  without file conflicts.

## Consequences

- ✅ Deterministic ordering; parallel-safe authoring; no renumbering churn.
- ✅ The track→docs→test mapping keeps the repository navigable at scale.
- ⚠️ Inserting a concept mid-path means appending a higher number (or a suffix),
  not renumbering — order is by curriculum design, not strict difficulty rank.
