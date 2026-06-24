# Project Agents Guide

## Project Overview

- Project name: Tiny Team Website
- Goal: Build a small project landing page and keep collaboration clear.
- Main users: project owner, one Lead AI thread, one Member AI thread.
- Current stage: early content and layout iteration.
- Tech stack: static Markdown and HTML for the example.

## Collaboration Mode

Default: Casual Coordination Mode.

Task Assignment Mode: enabled.

Module Ownership Mode: not enabled yet.

## Actor Naming

Actors:

- Lead: Project Lead
- Member: Content Worker

If a new member has no specific sub-role, use `Full-stack Developer`.

## Startup Checklist

1. Read this file.
2. Read `COLLAB_LOG.md`.
3. Check `# Active Work Locks`.
4. Read `TEAM_TASKS.md`.
5. Check Git status before larger edits.
6. Add a soft lock before editing when safe.

## Active Work Lock Rules

Soft locks are coordination notes, not security locks.

Before editing, check `COLLAB_LOG.md`.

If another actor has a lock on the same scope, stop and ask the user.

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

- Do not use blind `git add .`.
- Explicitly stage only files related to the current change.
- Do not commit secrets, caches, dependency folders, or runtime data.
- Do not force push or hard reset unless the user explicitly approves.
- Confirm branch and remote before pushing.

## File Organization Rules

- Keep collaboration files at the project root.
- Do not introduce a large framework for this tiny example.
- Prefer small, readable changes.

## Logging Rules

Write short updates in `COLLAB_LOG.md`.

Include changed files, result, checks, and blockers.

## Conflict Handling

If a lock overlaps your scope, stop and ask.

If project rules conflict with a user request, explain the conflict and ask which rule wins.

## Completion / Handoff Rules

When done:

1. Remove your lock.
2. Add a Latest Update.
3. Update `TEAM_TASKS.md`.

## When To Ask The User

Ask when scope is unclear, a lock is stale, a lock conflicts, or a task needs a decision.
