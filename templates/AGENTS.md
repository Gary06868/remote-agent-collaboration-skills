# Project Agents Guide

## Project Overview

- Project name:
- Goal:
- Main users:
- Current stage:
- Tech stack:

## Collaboration Mode

Default mode: Casual Coordination Mode.

Optional modes:

- Task Assignment Mode: disabled by default. Enable only when the user wants `TEAM_TASKS.md`.
- Module Ownership Mode: disabled by default. Enable only when the user wants `MODULE_OWNERSHIP.md`.

## Actor Naming

Each contributor should identify:

- Actor:
- Agent:
- Role:
- Current scope:

If no specific sub-role is defined, use `Full-stack Developer`.

## Startup Checklist

Before larger work:

1. Read this file.
2. Read `COLLAB_LOG.md`.
3. Check `# Active Work Locks`.
4. Read `TEAM_TASKS.md` if Task Assignment Mode is enabled.
5. Read `MODULE_OWNERSHIP.md` if Module Ownership Mode is enabled.
6. Check Git state.
7. Add a soft lock before editing when safe.

## Active Work Lock Rules

Soft locks are coordination notes, not security locks.

Before larger read/write work, check `COLLAB_LOG.md`.

If no lock overlaps your scope, add a lock under `# Active Work Locks`.

If a lock overlaps your scope, stop and ask the user or Lead before editing.

Do not delete another actor's lock without confirmation.

Suggested stale threshold: 2 hours.

## Git Rules

Before larger tasks:

```bash
git fetch --all --prune
git status --short --branch
git branch -vv
```

Rules:

- If the local branch is behind remote, understand the remote changes before continuing.
- Stop and ask if a change might overwrite someone else's work.
- Do not use blind `git add .`.
- Explicitly stage only files related to the current change.
- Do not commit `.env`, caches, temporary files, dependency folders, virtualenvs, or runtime data.
- Do not force push unless the user explicitly approves.
- Do not use `git reset --hard` unless the user explicitly approves.
- Do not delete someone else's branch unless the user explicitly approves.
- Before committing, summarize what changed.
- Before pushing, confirm the current branch and target remote.

## File Organization Rules

- Respect the existing project structure.
- Do not reorganize folders just to match this template.
- Keep new collaboration files at the project root unless the user says otherwise.
- Avoid adding process files that duplicate existing project systems.

## Logging Rules

Use `COLLAB_LOG.md`.

Log entries should be short and useful:

- Date/time.
- Actor.
- Scope.
- Files changed.
- Result.
- Checks run.
- Blockers or follow-up.

Do not paste full chat transcripts.

## Conflict Handling

Stop and ask when:

- An active lock overlaps your requested work.
- Existing project rules conflict with a requested change.
- You need to edit outside your assigned scope.
- You are unsure whether another contributor owns the area.

## Completion / Handoff Rules

When done:

1. Remove or update your soft lock.
2. Add a Latest Update in `COLLAB_LOG.md`.
3. Update your task in `TEAM_TASKS.md` if task mode is enabled.
4. Note blockers or handoff details.

## When To Ask The User

Ask when:

- The current actor or role is unclear.
- Task Assignment Mode is not decided.
- Module Ownership Mode is not decided.
- A lock is stale or conflicting.
- Existing rules conflict with this workflow.
- The requested change affects unclear ownership or protected areas.
