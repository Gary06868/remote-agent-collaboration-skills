# Protocol Reference

Remote Agent Collaboration Lite is a Markdown-only collaboration workflow for one project Lead and multiple Members. It coordinates humans, Codex threads, Claude threads, and other AI agents through shared files rather than a server.

## Core Files

| File | Required | Purpose |
| --- | --- | --- |
| `AGENTS.md` | Yes | Shared rules, Actor Registry, startup checklist, Git rules, logging rules, and conflict handling. |
| `COLLAB_LOG.md` | Yes | Active Work Locks, Current Snapshot, blockers, Open Handoffs, decisions, updates, and history. |
| `TEAM_TASKS.md` | Optional | Lightweight task blocks when Task Assignment Mode is enabled. |
| `MODULE_OWNERSHIP.md` | Optional | Module owners and path boundaries when Module Ownership Mode is enabled. |

Templates live in [`../templates/`](../templates/). The Lead Skill also carries byte-identical templates in [`../skills/team-lead-collaboration/references/`](../skills/team-lead-collaboration/references/).

## Actor Identity Protocol

Every Lead, Member, lock, task, update, decision, and handoff should use a stable actor identity.

Required fields:

- Human owner:
- Agent platform:
- Collaboration role:
- Functional role:
- Instance:
- Actor ID:
- Display name:

Lead Skill means `Collaboration role: Lead`. Member Skill means `Collaboration role: Member`. Do not ask again whether the actor is Lead or Member after the Skill has been explicitly selected.

## Actor Status Semantics

- `active`: the actor may accept work and acquire, refresh, pause, resume, and release locks.
- `paused`: the actor is temporarily unavailable for new scope. Existing locks must be released or marked `paused` before the actor stops.
- `retired`: the actor no longer accepts new work and must not hold an active lock. Keep historical records intact.
- Allowed transitions: active -> paused -> active, active -> retired, paused -> retired.
- A Member may update only its own Actor Registry entry.
- `Last seen` updates when the actor starts work, acquires a lock, refreshes a lock, pauses, resumes, releases, changes task status, creates a handoff, or responds to a handoff.
- `Current scope` updates when the actor acquires, pauses, resumes, or releases a lock, or when assigned task scope changes.

## Active Work Locks

Soft locks are collaboration notes, not security locks.

```markdown
- Actor ID:
  Display Name:
  Collaboration Role: Lead | Member
  Functional Role:
  Status: reading | writing | paused
  Scope:
  Task:
  Started:
  Last Updated:
  Expected Finish:
  Notes:
```

Shared Workspace Mode uses a local double-check: read locks, write your lock, then double-check Active Work Locks after writing your own lock before editing business files.

Conflict semantics:

- reading with reading does not conflict by default.
- writing with overlapping writing is a conflict.
- reading with overlapping writing requires a warning.
- paused still reserves the scope.
- stale threshold: 2 hours unless `AGENTS.md` overrides it.
- Do not remove another actor's stale lock without user or Lead confirmation.

## Scope Canonicalization

- Use repository-relative paths only.
- Use `/` as the separator.
- Remove a leading `./`.
- Collapse repeated `/` characters.
- Remove trailing `/` except for repository root.
- Separate multiple paths with `;`.
- Trim whitespace around each path.
- Reject absolute paths.
- Reject `..` path segments.
- Scopes overlap when any canonical path is equal, parent/child, or shares a declared module/interface boundary.

## Completion Policy

Task Assignment Mode must record who may mark tasks DONE. The supported policies are:

- Lead review: Member finishes as `READY_FOR_REVIEW`; handoff target type is `actor`; target actor is the concrete Lead `actor_id`.
- User review: Member finishes as `READY_FOR_REVIEW`; handoff target type is `human-user`; do not invent an Actor ID for the user.
- Member self-completion: Member marks the task `DONE` when acceptance notes are met; do not create a review handoff.
- Per-task decision: each task must record the selected completion policy. If it is missing, stop and ask.

Review loops are explicit: `CHANGES_REQUESTED -> IN_PROGRESS -> READY_FOR_REVIEW` for review policies, or `CHANGES_REQUESTED -> IN_PROGRESS -> DONE` for Member self-completion.

## Final Reconciliation

After major work, verify:

- Active Work Locks match the real state.
- TEAM_TASKS.md status matches the real state.
- Current Snapshot reflects the latest work.
- Open Handoffs only contain unresolved items.
- Recent Decisions match the current mode.
- `actor_id` is consistent across `AGENTS.md`, `COLLAB_LOG.md`, `TEAM_TASKS.md`, and `MODULE_OWNERSHIP.md`.
- Timestamps use the project timezone and UTC offset.
- Files do not contradict each other.

## Limits

This is not OS-level enforcement. It works because agents are instructed to read and follow shared Markdown files. It intentionally avoids a server, database, custom collaboration CLI, hook system, session lock, doctor flow, or enterprise permission model.
