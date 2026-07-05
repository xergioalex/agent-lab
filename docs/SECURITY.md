# Security — Agent Lab

## Secrets Handling

| Secret | Location | Rules |
|--------|----------|-------|
| `OPENAI_API_KEY` | Environment variable or local `.env` | **Never** commit to git |
| API keys in general | `.env` (gitignored) | Add `.env` to local setup only |

`.gitignore` excludes `.env`. Agents **MUST NOT** write API keys into source files,
docs, or commit messages.

## Authentication Model

- **OpenAI API**: Bearer token via `OPENAI_API_KEY` environment variable.
  LangChain reads this automatically for `ChatOpenAI`.
- **No application-level auth**: exercises are local scripts, not networked services.

## Sensitive Data Boundaries

- Exercise scripts use synthetic messages (`"hello"`, `"we are blocked"`).
- Do not use real user data, PII, or production credentials in examples.
- Mock modules (`07`, `08`) must not connect to real Qdrant or Neo4j instances
  without explicit developer consent and updated docs.

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
- One external integration point: OpenAI API (modules 03+)
- Risk is primarily **credential leakage** — treat `OPENAI_API_KEY` as the only
  secret that matters today.
