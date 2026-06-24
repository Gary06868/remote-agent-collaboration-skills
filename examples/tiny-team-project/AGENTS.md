# Project Agents Guide

## Project Overview

- Project name: Tiny Team Website
- Goal: Build a small project landing page and keep collaboration clear.
- Main users: project owner, one Lead AI thread, and multiple Member AI threads.
- Current stage: early content and review.
- Tech stack: static Markdown and HTML for the example.

## Collaboration Mode

Default: Casual Coordination Mode.

Task Assignment Mode: enabled.

Module Ownership Mode: not enabled yet.

## Project Time

- Project timezone: America/Los_Angeles
- Timestamp format: ISO 8601 with UTC offset, for example `2026-06-24T10:38:00-07:00`.
- Lock stale threshold: 2 hours.

## Actor Identity Protocol

Required fields:

- Human owner:
- Agent platform:
- Collaboration role: Lead | Member
- Functional role:
- Instance:
- Actor ID:
- Display name:

Do not use task names as actor identities. Keep actor IDs stable across collaboration files.

## Actor Registry

### alex-codex-lead-coordinator-01

- Display name: Alex's Codex #01 (Lead - Project Coordinator)
- Human owner: Alex
- Agent platform: Codex
- Collaboration role: Lead
- Functional role: Project Coordinator
- Instance: 01
- Status: active
- Current scope: TASK-LEAD-REVIEW.md review queue
- Registered at: 2026-06-24T10:00:00-07:00
- Last seen: 2026-06-24T11:45:00+00:00

### morgan-claude-member-content-01

- Display name: Morgan's Claude #01 (Member - Content Developer)
- Human owner: Morgan
- Agent platform: Claude
- Collaboration role: Member
- Functional role: Content Developer
- Instance: 01
- Status: active
- Current scope: TASK-LEAD-REVIEW.md, TASK-REVIEW-LOOP.md
- Registered at: 2026-06-24T10:05:00-07:00
- Last seen: 2026-06-24T11:40:00+00:00

### alex-codex-member-test-02

- Display name: Alex's Codex #02 (Member - Test Engineer)
- Human owner: Alex
- Agent platform: Codex
- Collaboration role: Member
- Functional role: Test Engineer
- Instance: 02
- Status: active
- Current scope: README.md review attempt
- Registered at: 2026-06-24T10:10:00-07:00
- Last seen: 2026-06-24T10:18:00+00:00

## Completion Policy

Who may mark tasks DONE: Lead review.

Members mark assigned work `READY_FOR_REVIEW` unless the review target explicitly approves direct `DONE`.

## Startup Checklist

1. Read this file.
2. Read `COLLAB_LOG.md`.
3. Confirm your Actor Registry entry.
4. Check Active Work Locks.
5. Read `TEAM_TASKS.md`.
6. Check Git state before larger edits.
7. Add a soft lock before editing when safe.
8. double-check Active Work Locks after writing your own lock.

## Active Work Lock Rules

Soft locks are coordination notes, not security locks.

Quick reads do not need a lock. Larger research or analysis may use a `reading` lock.

Conflict semantics:

- reading with reading does not conflict by default.
- writing with overlapping writing is a conflict.
- reading with overlapping writing requires a warning.
- paused still reserves the scope.
- stale threshold: 2 hours.
- Do not remove another actor's stale lock without user or Lead confirmation.

Use repository-relative paths for Scope. If a lock overlaps your scope, stop and ask.

## Git Rules

Before larger tasks:

```bash
git rev-parse --is-inside-work-tree
git status --short --branch
git branch -vv
```

Run `git fetch --all --prune` only when a remote exists. If this is not a Git repository, tell the user and continue Markdown coordination if Git is not needed.

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

Major updates include actor ID, display name, role, task, scope, files, result, checks, blockers, and next action.

## Conflict Handling

If a lock overlaps your scope, stop and ask.

If project rules conflict with a user request, explain the conflict and ask which rule wins.

## Completion / Handoff Rules

When done:

1. Remove your lock.
2. Add a Latest Update.
3. Update `TEAM_TASKS.md`.
4. Move resolved handoffs to History / Archived Notes.
5. Run Final Reconciliation.

## Final Reconciliation

Before reporting completion, verify:

- Active Work Locks match the real state.
- TEAM_TASKS.md status matches the real state.
- Current Snapshot reflects the latest work.
- Open Handoffs only contain unresolved items.
- actor_id is consistent across AGENTS.md, COLLAB_LOG.md, TEAM_TASKS.md, and MODULE_OWNERSHIP.md.
- Timestamps use the project timezone and UTC offset.

## When To Ask The User

Ask when scope is unclear, a lock is stale, a lock conflicts, or a task needs a decision.
