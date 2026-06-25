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

Workspace modes:

- Shared Workspace Mode: multiple agents use the same working directory.
- Remote Git Mode: different machines, clones, or worktrees coordinate through a Git remote.

Do not mix assumptions between these modes. Shared Workspace Mode relies on the same working directory and local Markdown state. Remote Git Mode must assume another participant may push from a different clone between any two local commands.

## Project Time

- Project timezone:
- Timestamp format: ISO 8601 with UTC offset, for example `2026-06-24T10:38:00-07:00`.
- Lock stale threshold: 2 hours unless this project overrides it.

## Actor Identity Protocol

Each actor must use a stable identity. Do not use a task name as actor identity.

Required fields:

- Human owner:
- Agent platform:
- Collaboration role: Lead | Member
- Functional role:
- Instance:
- Actor ID:
- Display name:

Identity rules:

- The Lead Skill fixes `Collaboration role: Lead`.
- The Member Skill fixes `Collaboration role: Member`.
- Do not ask again whether the actor is Lead or Member.
- If the human owner is unknown, ask the user.
- If the agent platform cannot be determined reliably, ask the user.
- If the functional role is unclear, ask the user.
- Use `Full-stack Developer` only when the user does not need a specific functional role.
- Use different instances such as `01`, `02`, or a user-chosen alias when the same owner opens multiple agents on the same platform.
- Keep `actor_id` stable after it is written into the project.
- `display_name` may change, but `actor_id` should not change.

Example:

```yaml
human_owner: Gary
agent_platform: Codex
collaboration_role: Member
functional_role: Frontend Developer
instance: 01
actor_id: gary-codex-member-frontend-01
display_name: Gary's Codex #01 (Member - Frontend Developer)
```

## Actor Registry

Lead may register and maintain team actors. A Member who is not registered must ask the user for identity details first. After user confirmation, the Member may add or update only its own Actor Registry entry. Member self-registration is not taking over Lead project-rule responsibility.

Actor IDs must be unique. The same actor must use the same `actor_id` across `AGENTS.md`, `COLLAB_LOG.md`, `TEAM_TASKS.md`, and `MODULE_OWNERSHIP.md`.

### <actor-id>

- Display name:
- Human owner:
- Agent platform:
- Collaboration role: Lead | Member
- Functional role:
- Instance:
- Status: active | paused | retired
- Current scope:
- Registered at:
- Last seen:

## Actor Status Semantics

- `active`: the actor may accept work and acquire, refresh, pause, resume, and release locks.
- `paused`: the actor is temporarily unavailable for new scope. Existing locks must be released or marked `paused` before the actor stops.
- `retired`: the actor no longer accepts new work and must not hold an active lock. Keep historical records intact.
- Allowed transitions: active -> paused -> active, active -> retired, paused -> retired.
- A Member may update only its own Actor Registry entry.
- `Last seen` updates when the actor starts work, acquires a lock, refreshes a lock, pauses, resumes, releases, changes task status, creates a handoff, or responds to a handoff.
- `Current scope` updates when the actor acquires, pauses, resumes, or releases a lock, or when assigned task scope changes.

## Completion Policy

Who may mark tasks DONE:

- Lead review
- User review
- Member self-completion
- Per-task decision

Default for this project:

- Who may mark tasks DONE:

## Startup Checklist

Before larger work:

1. Read this file.
2. Read `COLLAB_LOG.md`.
3. Confirm or register your actor identity.
4. Check Active Work Locks.
5. Read `TEAM_TASKS.md` if Task Assignment Mode is enabled and the file exists.
6. Read `MODULE_OWNERSHIP.md` if Module Ownership Mode is enabled.
7. Check Git state when the folder is a Git repository.
8. Add a soft lock before larger editing when safe.
9. After writing the lock, double-check Active Work Locks after writing your own lock before editing business files.

## Active Work Lock Rules

Soft locks are coordination notes, not security locks.

Quick reads of `AGENTS.md`, `COLLAB_LOG.md`, and task files do not need a lock. Larger research or analysis may use a `reading` lock.

Shared Workspace Mode uses root Markdown state and a local double-check: read locks, write your lock, then double-check Active Work Locks after writing your own lock before editing business files.

Remote Git Mode uses low-conflict Markdown state:

| Path | Type | Rule |
| --- | --- | --- |
| `.collab/locks/<actor-id>.md` | authoritative state | One actor owns one lock file. |
| `.collab/tasks/<task-id>.md` | authoritative state | One task owns one task file. |
| `.collab/events/<timestamp>-<actor-id>.md` | append-only event | One event per file. |
| `.collab/snapshots/COLLAB_LOG.md` | derived snapshot | Lead may rebuild it from locks, tasks, and events. |
| `COLLAB_LOG.md` | derived snapshot | Lead may rebuild it as a human-readable aggregate. |

Conflict semantics:

- reading with reading does not conflict by default.
- writing with overlapping writing is a conflict.
- reading with overlapping writing requires a warning.
- If reading is only observation, it may continue.
- If reading is likely to become editing soon, ask first or switch scope.
- paused still reserves the scope.
- stale threshold: 2 hours unless this project overrides it.
- Do not remove another actor's stale lock without user or Lead confirmation.

Scope rules:

- Use repository-relative paths only.
- Prefer concrete files or directories.
- Do not record local absolute paths.
- Avoid broad scopes such as `project` or `frontend` unless the project is that small.
- Multiple paths are allowed.

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

Before larger read/write work:

1. Read the latest `COLLAB_LOG.md`.
2. Check for overlapping locks.
3. If there is no overlap, add your own lock under Active Work Locks.
4. Immediately re-read `COLLAB_LOG.md`.
5. Check again for another actor that created an overlapping lock at the same time.
6. If a race appears, do not edit business files. Explain the conflicting actors and scopes and wait for a user or Lead decision.

Suggested lock format:

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

## Remote Git Mode Lock Protocol

Before modifying business files in Remote Git Mode:

1. fetch the latest remote state.
2. Re-read `.collab/locks/*.md` and `.collab/tasks/*.md`.
3. Check existing locks for scope overlap.
4. create a candidate lock record in `.collab/locks/<actor-id>.md`.
5. commit only the candidate lock.
6. push the candidate lock to the collaboration branch.
7. If push reports non-fast-forward, fetch, rebase or reapply the candidate lock, re-read all locks, and re-evaluate scope overlap.
8. Do not blindly repeat push.
9. Do not force push.
10. Only edit business files after the candidate lock is published and rechecked on the latest remote state.

Lock lifecycle:

- acquire: publish a candidate lock, re-check latest remote state, then continue.
- refresh: update `Last Updated` before continuing long work.
- pause: keep the scope reserved while temporarily stopped.
- resume: the same actor returns and refreshes the lock before editing.
- release: remove or mark the actor's lock released after work and reconciliation.
- stale: older than the stale threshold; Members report but do not delete another actor's stale lock.
- abandoned: Lead or explicit user decision marks a stale/crashed lock abandoned so others can proceed.

## Git Rules

Before larger tasks, check whether this is a Git repository:

```bash
git rev-parse --is-inside-work-tree
```

If it is not a Git repository:

- Tell the user.
- Ask whether they want to initialize Git.
- Continue Markdown collaboration setup if Git is not needed.
- Do not run `git fetch`.

If it is a Git repository:

```bash
git status --short --branch
git branch -vv
```

Run `git fetch --all --prune` only when a remote exists. If remote or network fetch fails, report it plainly. Do not pretend synchronization succeeded. Do not block Markdown-only collaboration unless overwrite risk is involved.

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

Small updates may be one line. Major work should use:

```markdown
### <timestamp> - <actor-id>

- Display Name:
- Collaboration Role:
- Functional Role:
- Type:
- Task:
- Scope:
- Files:
- Result:
- Checks:
- Git:
- Blockers:
- Next:
```

If there is no commit, write `Not committed`. Do not invent commit SHAs. Do not paste full chat transcripts.

## Conflict Handling

Stop and ask when:

- An active lock overlaps your requested work.
- Existing project rules conflict with a requested change.
- You need to edit outside your assigned scope.
- You are unsure whether another contributor owns the area.
- A stale lock needs release and you are not the same actor.

## Completion / Handoff Rules

When done:

1. Remove or update your soft lock.
2. Add a Latest Update in `COLLAB_LOG.md`.
3. Update your task in `TEAM_TASKS.md` if task mode is enabled.
4. Move resolved or cancelled handoffs to History / Archived Notes.
5. Run Final Reconciliation against `AGENTS.md`, `COLLAB_LOG.md`, and task files.

Completion Policy rules:

- Lead review: Member finishes as `READY_FOR_REVIEW`; handoff target type is `actor`; target actor is the concrete Lead `actor_id`.
- User review: Member finishes as `READY_FOR_REVIEW`; handoff target type is `human-user`; do not invent an Actor ID for the user.
- Member self-completion: Member marks the task `DONE` when acceptance notes are met; do not create a review handoff.
- Per-task decision: each task must record the selected completion policy. If it is missing, stop and ask.
- Review loops are explicit: `CHANGES_REQUESTED -> IN_PROGRESS -> READY_FOR_REVIEW` for review policies, or `CHANGES_REQUESTED -> IN_PROGRESS -> DONE` for Member self-completion.

## Final Reconciliation

Before reporting completion, verify:

- Active Work Locks match the real state.
- Your completed work no longer leaves a stale writing lock.
- TEAM_TASKS.md status matches the real state.
- Current Snapshot reflects the latest work.
- Next action matches the latest state.
- Open Handoffs only contain unresolved items.
- No old handoff asks a Member to redo an already completed task.
- Recent Decisions match the current mode.
- actor_id is consistent across AGENTS.md, COLLAB_LOG.md, TEAM_TASKS.md, and MODULE_OWNERSHIP.md.
- Timestamps use the project timezone and UTC offset.
- Files do not contradict each other.

## When To Ask The User

Ask when:

- The human owner is unknown.
- The agent platform cannot be determined reliably.
- The functional role is unclear.
- Task Assignment Mode is not decided.
- Module Ownership Mode is not decided.
- A lock is stale or conflicting.
- Existing rules conflict with this workflow.
- The requested change affects unclear ownership or protected areas.
