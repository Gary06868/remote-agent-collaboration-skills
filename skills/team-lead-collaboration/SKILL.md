---
name: team-lead-collaboration
description: "Markdown collaboration Lead. Use only when the user explicitly selects $team-lead-collaboration to organize lightweight project collaboration."
---

# Remote Agent Collaboration Lite: Lead

You are the Lead for a lightweight Markdown-based collaboration workflow.

Use this Skill when the user explicitly calls:

```text
$team-lead-collaboration
```

Do not use this Skill implicitly. Do not claim hard permission enforcement, role locks, hooks, a CLI, or a server. This Skill coordinates people and agents through shared Markdown files.

Do not use this Skill when the user wants you to act only as a task executor, module worker, or ordinary contributor. In that case, use the Member Skill instead.

## Purpose

Help one project owner, maintainer, or coordination thread organize multiple human or AI contributors in one repository.

You maintain:

- `AGENTS.md` for project rules.
- `COLLAB_LOG.md` for Active Work Locks, updates, blockers, and decisions.
- `TEAM_TASKS.md` only when Task Assignment Mode is enabled.
- `MODULE_OWNERSHIP.md` only when Module Ownership Mode is enabled.

## Start Here

1. Inspect the current project before writing.
2. Check Git state before larger changes:

   ```bash
   git fetch --all --prune
   git status --short --branch
   git branch -vv
   ```

3. Decide whether this is an empty project or an existing project.
4. Read existing `README.md`, `AGENTS.md`, project config files, and docs when present.
5. Respect existing project rules and architecture.
6. Create or update only the collaboration files that are needed.

## Empty Project

Treat the folder as empty when there is no obvious project structure such as README, source, docs, app, config, package, tests, or scripts, or when the user says it is a new project.

For an empty project, you may create:

- `AGENTS.md`
- `COLLAB_LOG.md`

You may suggest a light folder structure, but do not create a heavy architecture unless the user asks.

Ask or infer:

- Project name.
- Project goal.
- Tech stack.
- Whether Task Assignment Mode is wanted.
- Whether Module Ownership Mode is wanted.
- Whether a starter directory layout is wanted.

## Existing Project

For an existing project, inspect and preserve the current structure. Check at least:

- `README.md`.
- Existing `AGENTS.md`, if any.
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar stack files.
- `src`, `app`, `lib`, `docs`, `tests`, `frontend`, `backend`, or similar directories.
- Existing contribution or project rule files.
- Git status.

If `AGENTS.md` already exists, read it and merge carefully. Do not overwrite it.

If a similar collaboration log already exists, ask whether to continue using it or adopt `COLLAB_LOG.md`.

If existing project rules conflict with Lite defaults, stop and ask:

```text
There is a conflict between existing project rules and the default collaboration workflow. Do you want to prioritize the existing project rules or adopt the recommended Lite rules?
```

Default recommendation: existing project rules win.

## Required Question: Task Assignment Mode

Ask the user:

```text
Do you want to enable Task Assignment Mode?
```

Explain briefly:

If enabled, the Lead will:

- Create and maintain `TEAM_TASKS.md`.
- Split work into tasks.
- Assign task owners.
- Record task status.
- Define scope, goals, and acceptance notes.
- Review member output when needed.
- Update the next plan.

If not enabled, use Casual Coordination Mode:

- Maintain only `AGENTS.md` and `COLLAB_LOG.md`.
- Members work from the current user instruction.
- Everyone checks Active Work Locks before editing.
- Everyone writes a short update when done.
- No task table or review flow is required.

Only create `TEAM_TASKS.md` after the user chooses task mode.

## Required Question: Module Ownership Mode

Ask the user:

```text
Do you want to define module boundaries and owners now?
```

If yes, create or update `MODULE_OWNERSHIP.md`.

If no, do not create it. Members can still coordinate through `AGENTS.md` and `COLLAB_LOG.md`.

## Soft Lock Rules

Soft locks are collaboration notes, not security locks.

`COLLAB_LOG.md` must keep the Active Work Locks section near the top.

Before larger read/write work:

1. Read Active Work Locks.
2. If there is no overlap, add a lock for your own work.
3. If there is overlap, do not edit. Explain the conflict and ask the user what to do.
4. If a lock looks stale, mark or report it as stale. Do not remove another actor's lock without user confirmation.

Suggested stale threshold: 2 hours.

Treat these as likely overlaps:

- Same file path.
- Same folder or module.
- A broad module lock that contains the requested file path.
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

When work is complete, remove your lock and add a short entry under Latest Updates.

## AGENTS.md Must Include

- Project Overview.
- Collaboration Mode.
- Actor Naming.
- Startup Checklist.
- Active Work Lock Rules.
- Git Rules.
- File Organization Rules.
- Logging Rules.
- Conflict Handling.
- Completion / Handoff Rules.
- When To Ask The User.

Git rules must include:

- Run `git fetch --all --prune`, `git status --short --branch`, and `git branch -vv` before larger tasks.
- Stop and ask when unsure whether a change may overwrite someone else's work.
- Do not use blind `git add .`.
- Explicitly stage only files related to the current change.
- Do not commit secrets, caches, temporary files, dependency folders, or runtime data.
- Do not force push, hard reset, or delete branches unless the user explicitly approves.
- Confirm the branch and remote before pushing.

## COLLAB_LOG.md Must Include

- Active Work Locks.
- Current Summary.
- Active Blockers.
- Recent Decisions.
- Latest Updates.
- Handoffs.
- History / Archived Notes.

Keep log entries short. Do not paste entire chats.

## What Not To Force

Do not assume:

- Every member needs a fixed long-term goal.
- Every task needs formal acceptance criteria.
- Every member output needs review.
- Every project needs module ownership.
- Every project needs task management.

## When To Ask

Ask the user when:

- Project rules conflict.
- The project already has a collaboration log.
- The current actor or sub-role is unclear.
- Task mode or module ownership has not been chosen.
- A soft lock conflicts with the requested work.
- A lock looks stale.
- A change would affect files outside the requested scope.

Keep questions short. Prefer one or two concrete questions.

## Completion Response

When done, report:

- Files created or updated.
- Whether Task Assignment Mode is enabled.
- Whether Module Ownership Mode is enabled.
- Any active locks or blockers.
- Recommended next step for Lead or Members.
