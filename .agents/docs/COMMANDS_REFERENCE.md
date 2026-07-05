# Commands Reference — Agent Lab

Thin delegators in `.agents/commands/`. Each routes to the installed skill.

## Deep Work Plan

| Command | Delegates to | Purpose |
|---------|--------------|---------|
| `/dwp-create` | `deepworkplan/create` | Create a structured plan |
| `/dwp-execute` | `deepworkplan/execute` | Run plan tasks with gates |
| `/dwp-refine` | `deepworkplan/refine` | Modify in-progress plan |
| `/dwp-resume` | `deepworkplan/resume` | Continue interrupted plan |
| `/dwp-status` | `deepworkplan/status` | Report progress |
| `/dwp-verify` | `deepworkplan/verify` | Conformance check |

## Kit Authoring

| Command | Delegates to | Purpose |
|---------|--------------|---------|
| `/skill-create` | `deepworkplan/author` | Create or update a repo skill |
| `/agent-create` | `deepworkplan/author` | Create or update an agent persona |

## File Locations

```
.agents/commands/
├── dwp-create.md
├── dwp-execute.md
├── dwp-refine.md
├── dwp-resume.md
├── dwp-status.md
├── dwp-verify.md
├── skill-create.md
└── agent-create.md
```

## Invoking from Non-Cursor Agents

Read the corresponding `.md` file and follow the route instruction to the
sub-skill's `SKILL.md` under `.agents/skills/deepworkplan/`.
