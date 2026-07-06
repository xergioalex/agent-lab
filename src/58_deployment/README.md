# 58 — Deployment

## Learning Objectives

After this module you can:

- Explain the service topology defined by the repo's `docker-compose.yml`
  (optional Qdrant + Neo4j backends for local dev).
- Explain the CI pipeline shape in `.github/workflows/ci.yml` (offline test
  matrix, advisory lint/type gates).
- Map the three deployment stages every module in this repo already
  supports: local dev script -> containerized backend -> CI pipeline.
- Write an offline **readiness check** that validates deployment
  configuration without needing Docker or GitHub Actions running.

## Theory

This module does not introduce new infrastructure — Task 1 already shipped
the compose file and CI workflow this repo uses. Module 58's job is to make
that shape *legible* and *checkable*:

- **`docker-compose.yml`** (repo root) defines two **optional** services,
  `qdrant` and `neo4j`, used only when a learner wants to exercise the real
  vector/graph backends instead of the offline `InMemoryVectorStore` /
  `InMemoryGraphStore` fakes from `src.shared`. Every exercise in this
  curriculum runs without them — compose is additive, never required.
- **`.github/workflows/ci.yml`** runs the **offline test suite**
  (`python -m pytest`) across a Python version matrix on every push and pull
  request — the same **hard gate** this task's own validation follows: no
  script may require a key or a running service. Lint (`ruff`) and type
  checks (`mypy`) run too, but as advisory (`continue-on-error: true`) gates
  in a teaching repo, so a style nit never blocks a contribution.
- **Health checks** in this context are the offline **readiness checks** this
  module performs: instead of pinging a live container, `build_readiness_report`
  parses the compose and CI files and asserts they still declare the expected
  shape (services present, Python matrix declared, pytest wired in). This is
  the same idea as a container health check, applied to configuration.

The mapping from **local dev** to **container** to **pipeline** is the
throughline: the exact same `python src/NN_name/script.py` command a learner
runs locally is what CI runs (just repeated across a matrix), and the compose
file is a purely optional upgrade path when a module needs a real backend.

## Mental Models

Think of this three-stage mapping like a recipe moving from **home kitchen**
(local dev — no special equipment, run the script) to **food truck**
(container — same recipe, now backed by real equipment like a commercial
fridge/oven when needed) to **certified commercial kitchen inspection**
(CI pipeline — the same recipe, verified reproducibly on a schedule, by
someone else's oven). The recipe (the script) never changes between stages.

## Architecture

```mermaid
flowchart TD
    START(["START"]) --> MAP["print_deployment_map(): local -> container -> pipeline"]
    MAP --> READC["_read_text(docker-compose.yml)"]
    READC -->|"file missing"| FAIL1["raise FileNotFoundError"]
    READC -->|"ok"| EXTC["extract_compose_services(text)"]
    EXTC --> CHK1{"'qdrant' in services?"}
    CHK1 -->|"yes"| PASS1["PASS compose_defines_qdrant"]
    CHK1 -->|"no"| FAILCHK1["FAIL compose_defines_qdrant"]
    EXTC --> CHK2{"'neo4j' in services?"}
    CHK2 -->|"yes"| PASS2["PASS compose_defines_neo4j"]
    CHK2 -->|"no"| FAILCHK2["FAIL compose_defines_neo4j"]

    MAP --> READCI["_read_text(ci.yml)"]
    READCI -->|"file missing"| FAIL1
    READCI -->|"ok"| EXTV["extract_ci_python_versions(text)"]
    EXTV --> CHK3{"len(versions) >= 1?"}
    CHK3 -->|"yes"| PASS3["PASS ci_declares_python_matrix"]
    CHK3 -->|"no"| FAILCHK3["FAIL ci_declares_python_matrix"]
    READCI --> EXTR["extract_ci_run_commands(text)"]
    EXTR --> CHK4{"any run command contains 'pytest'?"}
    CHK4 -->|"yes"| PASS4["PASS ci_runs_offline_pytest"]
    CHK4 -->|"no"| FAILCHK4["FAIL ci_runs_offline_pytest"]

    PASS1 & PASS2 & PASS3 & PASS4 --> ALLOK{"all_passed?"}
    FAILCHK1 & FAILCHK2 & FAILCHK3 & FAILCHK4 --> ALLOK
    ALLOK -->|"False"| FAIL2["raise AssertionError: readiness check failed"]
    ALLOK -->|"True"| DONE["print MODULE 58 COMPLETE"]
    DONE --> END(["END"])
    FAIL1 --> END
    FAIL2 --> END
```

Legend: diamonds are the boolean checks `build_readiness_report` runs;
every `FAIL*` branch converges into `all_passed=False`, which raises before
the completion banner ever prints.

Sequence of the offline readiness read over time:

```mermaid
sequenceDiagram
    participant Main as main()
    participant FS as filesystem
    participant Ext as extract_* helpers
    participant Rep as build_readiness_report

    Main->>Main: print_deployment_map()
    Main->>Rep: build_readiness_report()
    Rep->>FS: _read_text(docker-compose.yml)
    FS-->>Rep: compose text
    Rep->>Ext: extract_compose_services(text)
    Ext-->>Rep: ["qdrant", "neo4j"]
    Rep->>FS: _read_text(ci.yml)
    FS-->>Rep: ci text
    Rep->>Ext: extract_ci_python_versions(text)
    Ext-->>Rep: ["3.11", "3.12"]
    Rep->>Ext: extract_ci_run_commands(text)
    Ext-->>Rep: ["python -m pytest", "ruff check ...", "mypy ..."]
    Rep-->>Main: [ReadinessCheck, ...]
    Main->>Main: print PASS/FAIL per check
    alt any check failed
        Main-->>Main: raise AssertionError
    else all passed
        Main-->>Main: print MODULE 58 COMPLETE
    end
```

Flow notes:

- Each `_read_text` call raises `FileNotFoundError` immediately if the
  compose or CI file is missing — a broken deployment file fails loudly
  instead of silently skipping checks.
- `compose_defines_qdrant` / `compose_defines_neo4j` both branch on the same
  `extract_compose_services` result; either service missing flips that
  check to `FAIL`.
- `ci_declares_python_matrix` branches on whether `extract_ci_python_versions`
  found at least one version; `ci_runs_offline_pytest` branches on whether
  any extracted run command contains `"pytest"`.
- `all_passed` aggregates all four checks — a single `FAIL` flips it to
  `False` and `main()` raises `AssertionError`; the completion banner only
  prints when every check passes.

## Runnable Example

```bash
python src/58_deployment/main.py
```

Expected output (deterministic; reflects the repo's actual compose/CI files):

```
deployment map:
  local dev   -> `python src/NN_name/script.py` (offline, no services required)
  container   -> `docker compose up -d` starts optional Qdrant + Neo4j backends
  pipeline    -> `.github/workflows/ci.yml` runs `pytest` offline on every push/PR
[PASS] compose_defines_qdrant: services found: ['qdrant', 'neo4j']
[PASS] compose_defines_neo4j: services found: ['qdrant', 'neo4j']
[PASS] ci_declares_python_matrix: python-version matrix: ['3.11', '3.12']
[PASS] ci_runs_offline_pytest: run commands: ['|', 'python -m pytest', 'ruff check src tests', 'mypy src/shared']
=== MODULE 58: DEPLOYMENT COMPLETE ===
```

## Challenge

1. Add a check confirming the CI workflow declares `continue-on-error: true`
   for the `ruff` and `mypy` steps (advisory, not blocking).
2. Add a check confirming `docker-compose.yml` mounts a named volume for each
   service (data persistence).
3. Break one of the checks intentionally (rename a service in a local copy of
   the compose text) and confirm `main()` raises with a clear message.

## Stretch Goals

- Extend `extract_compose_services` to also report each service's exposed
  ports, and assert `qdrant` exposes `6333`.
- Add a Dockerfile readiness check (does `docker/local/Dockerfile` exist,
  does it install `requirements.txt`) alongside the compose/CI checks.
- Write a `--strict` mode that also fails on advisory CI gates being marked
  `continue-on-error: true`, to model a stricter production pipeline.

## Common Mistakes

- Treating the compose file as required infrastructure — in this repo it is
  strictly optional; every exercise must still pass the offline hard gate
  without it running.
- Adding a new CI step that calls out to a real API/service — that would
  break the "offline hard gate" this whole curriculum depends on.
- Parsing YAML with regex for anything beyond a light structural read (as
  done here) — for real config validation, use a proper YAML parser; this
  module intentionally stays light to avoid a new dependency.

## Best Practices

- Keep local dev, container, and CI running the **exact same command** —
  divergence between "works on my machine" and "works in CI" usually comes
  from scripts that differ per environment.
- Make infrastructure additive: real backends (Qdrant, Neo4j, a real LLM)
  should always be an *upgrade* over a working offline default, never a
  requirement to get started.
- Fail loudly on missing/misconfigured deployment files (`_read_text` raises
  `FileNotFoundError`) rather than silently skipping checks.

## Suggested Improvements

- Add a `docs/deployment.md` (future work) mirroring `docs/observability.md`
  / `docs/security.md` / `docs/testing.md` if this track grows a fourth doc.
- Generate this readiness report as a CI step itself, so compose/CI drift is
  caught automatically.

## References

- [`docker-compose.yml`](../../docker-compose.yml) — the service topology
  this module validates.
- [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — the CI
  pipeline this module validates.
- [`docs/DEVELOPMENT_COMMANDS.md`](../../docs/DEVELOPMENT_COMMANDS.md) — the
  full local command reference.
- Module [57_cost_and_multitenancy](../57_cost_and_multitenancy/README.md) —
  the multi-tenant agent this deployment shape ultimately hosts.

## What Comes Next

This closes Track 8 (Production). From here, revisit
[10_full_brain_simulation](../10_full_brain_simulation/README.md) or the
capstone modules with an eye toward applying observability, evaluation,
testing, security, cost, and deployment practices to a complete agent
system.
