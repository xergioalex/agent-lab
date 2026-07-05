# Security — Agent Lab

## Secrets Handling

| Secret | Location | Rules |
|--------|----------|-------|
| `OPENAI_API_KEY` | Environment variable or local `.env` | **Never** commit to git |
| `QDRANT_API_KEY` | Environment variable or local `.env` | Optional (module 42); never commit |
| `NEO4J_PASSWORD` | Environment variable or local `.env` | Optional (module 43); never commit |
| API keys in general | `.env` (gitignored) | Add `.env` to local setup only |

`.gitignore` excludes `.env`. `.env.example` holds **placeholders only** (all
values blank or clearly non-secret). Agents **MUST NOT** write API keys into
source files, docs, or commit messages.

> `docker-compose.yml` sets a Neo4j default of `please-change-me` via
> `${NEO4J_PASSWORD:-please-change-me}`. This is a **local-dev placeholder**, not
> a secret — override `NEO4J_PASSWORD` in your shell/`.env` for any real use.

## Authentication Model

- **OpenAI API**: Bearer token via `OPENAI_API_KEY` environment variable.
  LangChain reads this automatically for `ChatOpenAI`.
- **No application-level auth**: exercises are local scripts, not networked services.

## Sensitive Data Boundaries

- Exercise scripts use synthetic messages (`"hello"`, `"we are blocked"`).
- Do not use real user data, PII, or production credentials in examples.
- Mock modules (`07`, `08`) must not connect to real Qdrant or Neo4j instances
  without explicit developer consent and updated docs.
- **Offline-first is the default** (see [ADR-0001](adr/0001-offline-first-fakes.md)):
  modules 42 (Qdrant) and 43 (Neo4j) use in-memory fallbacks unless `QDRANT_URL` /
  `NEO4J_URI` are set. No module opens a network connection in the default path.
- Agent-side security patterns (prompt injection, input validation) are taught in
  module 56 and [agent-security.md](agent-security.md).

## What Agents MUST NOT Do

- Commit `.env`, API keys, or tokens
- Log or print full API keys (mask if debugging: `sk-...xxxx`)
- Add network calls to external services without documenting them in `SECURITY.md`
  and `ARCHITECTURE.md`
- Store credentials in `src/shared/config.py` — use environment variables

## Dependency Supply Chain

- Dependencies are pinned with minimum versions in `requirements.txt`.
- Review updates before merging dependency bumps.
- Use `/lib-upgrade` (dependency-upgrade addon) only when explicitly installed.

## Reporting

Report security issues privately via the repository owner's preferred channel.
Do not open public issues for undisclosed vulnerabilities.

## Agent Lab Posture Summary

This is a **local learning repository** with minimal attack surface:

- No deployed endpoints
- No user accounts
- External integration points (all **optional**, env-gated, off by default):
  OpenAI API (modules 03, 15+), Qdrant (module 42), Neo4j (module 43)
- Risk is primarily **credential leakage** — keep `OPENAI_API_KEY`,
  `QDRANT_API_KEY`, and `NEO4J_PASSWORD` in `.env` (gitignored), never in source.
