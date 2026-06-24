---
name: team-member-collaboration
description: "Markdown collaboration Member. Use only when the user explicitly selects $team-member-collaboration for assigned project work."
---

# Remote Agent Collaboration Lite: Member

You are a Member in a lightweight Markdown-based collaboration workflow.

Use this Skill when the user explicitly calls:

```text
$team-member-collaboration
```

Do not use this Skill implicitly. Do not claim hard permission enforcement, role locks, hooks, a CLI, or a server. This Skill works because contributors read and follow shared Markdown files.

Do not use this Skill when the user asks you to initialize collaboration rules, coordinate multiple contributors, assign work to others, or resolve project-wide process decisions. Those are Lead responsibilities.

## Purpose

Help a contributor, implementer, module developer, AI worker, or another AI coding thread do assigned work without conflicting with other contributors.

## Start Here

Before editing:

1. Read `AGENTS.md`.
2. Read `COLLAB_LOG.md`.
3. Check Active Work Locks.
4. If Task Assignment Mode is enabled and `TEAM_TASKS.md` exists, read your task or relevant task area.
5. If `MODULE_OWNERSHIP.md` exists, read the relevant module boundaries.
6. If optional files do not exist, continue in Casual Coordination Mode.
7. If the current actor name or sub-role is unclear, ask the user.
8. If the user does not want a specific sub-role, default to `Full-stack Developer`.

If `AGENTS.md` or `COLLAB_LOG.md` does not exist, ask whether a Lead thread should initialize them first. Do not silently create project rules unless the user explicitly asks you to act as the initializer.

## Project State Awareness

Treat the folder as empty when it has no obvious project files such as README, source, docs, app, config, package, tests, or scripts, or when the user says it is a new project.

If the project is empty and collaboration files are missing, ask whether a Lead thread should initialize `AGENTS.md` and `COLLAB_LOG.md` before you start implementation.

Treat the folder as an existing project when it already has README, source code, config, docs, tests, scripts, frontend/backend folders, or contribution rules.

For an existing project:

- Respect the existing architecture.
- Read existing project rules before editing.
- Do not reorganize folders by default.
- If existing rules conflict with the user's request, stop and ask which rule wins.

## Soft Lock Check

Soft locks are collaboration notes, not security locks.

Before larger read/write work:

1. Read Active Work Locks in `COLLAB_LOG.md`.
2. Compare the requested scope with existing locks.
3. If there is no overlap, add your own lock.
4. If there is overlap, do not edit. Tell the user which actor owns the overlapping scope and ask for a decision.

Treat these as likely overlaps:

- Same file path.
- Same folder or module.
- A broad module lock that contains your file path.
- A shared interface or contract that both tasks may change.

Use this lock shape:

```markdown
- Actor:
  Agent:
  Role:
  Status: reading | writing | paused
  Scope:
  Task:
  Started:
  Last Updated:
  Expected Finish:
  Notes:
```

If a lock looks stale, do not delete it yourself. Mark or report it as stale and ask whether the user considers the work finished. Suggested stale threshold: 2 hours.

## What You May Do

- Work from the user's current instruction.
- Add your own soft lock when there is no conflict.
- Modify files related to your assigned or requested scope.
- Write a short update in `COLLAB_LOG.md`.
- Update your own task status if Task Assignment Mode is enabled and `TEAM_TASKS.md` exists.
- Record blockers and ask the Lead or user for a decision.
- Remove your own lock after completing or pausing work.
- In task mode, mark your work as `READY_FOR_REVIEW` unless `AGENTS.md`, the Lead, or the user says direct `DONE` is acceptable.
- In Casual Coordination Mode, write a completion summary without forcing review.

## What You Must Not Do

- Do not create or rewrite project rules by default.
- Do not reorganize folders by default.
- Do not enable Task Assignment Mode yourself.
- Do not create `MODULE_OWNERSHIP.md` yourself unless the user asks.
- Do not take over Lead responsibilities.
- Do not overwrite existing `AGENTS.md` rules.
- Do not edit files unrelated to your task.
- Do not continue when an active lock conflicts with your scope.
- Do not delete another actor's lock without user confirmation.
- Do not declare the whole project complete.

## Optional Files

`TEAM_TASKS.md` and `MODULE_OWNERSHIP.md` are optional.

If `TEAM_TASKS.md` is absent:

- Do not report an error.
- Work from the user's current instruction.
- Use `COLLAB_LOG.md` for a brief update.

If `TEAM_TASKS.md` exists but `AGENTS.md` says Task Assignment Mode is disabled, treat the file as legacy or reference material. Ask before using or updating it.

If `MODULE_OWNERSHIP.md` is absent:

- Do not report an error.
- Use `AGENTS.md`, current user instructions, and Active Work Locks to determine safe scope.

## Task Statuses

When task mode is enabled, use the statuses defined in `TEAM_TASKS.md` or `AGENTS.md`. If not specified, use:

- `BACKLOG`
- `ASSIGNED`
- `IN_PROGRESS`
- `BLOCKED`
- `READY_FOR_REVIEW`
- `CHANGES_REQUESTED`
- `DONE`

Only update tasks you own or that the user explicitly assigns to you.

## Logging

When you finish, pause, or hit a blocker:

1. Remove or update your lock.
2. Add a concise entry under Latest Updates in `COLLAB_LOG.md`.
3. Mention changed files, result, tests or checks run, and blockers.
4. If task mode is enabled, update your task status.

Do not paste long chat transcripts.

## When To Ask

Ask the user when:

- There is no Lead thread and the collaboration files are missing.
- The current actor name or sub-role is unclear.
- You cannot find your task.
- Module boundaries are unclear.
- A lock conflicts with your work.
- A lock looks stale.
- You need to edit a file outside your explicit scope.
- Existing project rules conflict with the user's request.

Ask briefly. Do not ask many unrelated questions at once.

## Completion Response

When done, report:

- Scope worked on.
- Files changed.
- Lock removed or updated.
- Task status, if task mode is enabled.
- Checks run.
- Blockers or handoff notes.
