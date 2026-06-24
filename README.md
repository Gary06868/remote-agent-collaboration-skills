# Remote Agent Collaboration Lite

If you and a few friends, cofounders, or AI agents are vibe coding together, your project can quickly turn into scattered chats, duplicate edits, and unclear ownership. Remote Agent Collaboration Lite gives you two Markdown Skills, Lead and Member, plus simple project files for rules, soft locks, logs, optional tasks, and optional module boundaries. No server, no database, no CLI, no hooks.

Install both Skills:

- `team-lead-collaboration`
- `team-member-collaboration`

Open one Lead thread with:

```text
$team-lead-collaboration Set up lightweight collaboration for this project.
```

Open Member threads with:

```text
$team-member-collaboration Work on my assigned scope and update the shared collaboration log.
```

The team coordinates through Markdown files:

- `AGENTS.md` for shared project rules.
- `COLLAB_LOG.md` for active work locks, updates, blockers, and decisions.
- `TEAM_TASKS.md` when you choose task assignment mode.
- `MODULE_OWNERSHIP.md` when you choose module ownership mode.

## What This Is

Remote Agent Collaboration Lite is a Markdown-only collaboration workflow for one project lead and multiple contributors. Contributors can be humans, Codex threads, Claude threads, other AI agents, or a mix of all of them.

It does not try to enforce permissions. It gives agents explicit instructions to read the same project files, claim work before editing, avoid conflicting scopes, and leave short handoff notes.

## Who It Is For

Use it when:

- A small team or tiny company is building in one repository.
- Several AI threads may edit related files.
- You want a lead agent to coordinate work without introducing infrastructure.
- You need lightweight logs and soft locks instead of a full project management system.
- You want a new contributor to understand the collaboration rules in five minutes.

## What Problems It Solves

- Scattered chat history becomes shared Markdown context.
- Duplicate edits are reduced by checking Active Work Locks first.
- Ownership is visible when optional module boundaries are enabled.
- Task mode is available when useful, but casual coordination stays the default.
- Members know when to stop and ask instead of guessing through conflicts.

## Quick Start

1. Install both Skills in your AI coding environment.
2. Start a Lead thread:

   ```text
   $team-lead-collaboration Initialize collaboration for this existing project.
   ```

3. The Lead checks whether the project is empty or already has structure.
4. The Lead creates or updates `AGENTS.md` and `COLLAB_LOG.md`.
5. The Lead asks whether to enable Task Assignment Mode.
6. The Lead asks whether to enable Module Ownership Mode.
7. Start one or more Member threads:

   ```text
   $team-member-collaboration Read the collaboration files and work on the scope I give you.
   ```

8. Each Member checks Active Work Locks before editing, adds a lock when safe, removes it when done, and writes a short update.

## Lead Thread Workflow

The Lead is for the project owner, project maintainer, collaboration organizer, or an AI thread responsible for coordinating multiple workers.

The Lead should:

- Read the existing project structure before writing.
- Create or maintain `AGENTS.md`.
- Create or maintain `COLLAB_LOG.md`.
- Explain that soft locks are coordination notes, not security controls.
- Ask: "Do you want to enable Task Assignment Mode?"
- If enabled, create or update `TEAM_TASKS.md`.
- Ask: "Do you want to define module boundaries and owners now?"
- If enabled, create or update `MODULE_OWNERSHIP.md`.
- Assign work when task mode is useful.
- Review member output when needed.
- Resolve conflicts and blockers.
- Summarize or compress long collaboration logs.

The Lead should not force every project into formal task tracking or module ownership.

## Member Thread Workflow

The Member is for a contributor, implementer, module developer, AI worker, or another AI coding thread.

At startup, the Member should:

1. Read `AGENTS.md`.
2. Read `COLLAB_LOG.md`.
3. Check `# Active Work Locks`.
4. Read `TEAM_TASKS.md` if it exists.
5. Read `MODULE_OWNERSHIP.md` if it exists.
6. Continue in Casual Coordination Mode if optional files are absent.
7. Ask the user for the current actor name or sub-role if it is unclear.

During work, the Member should:

- Add a soft lock before larger read/write work if no conflict exists.
- Stop and ask if another active lock overlaps the requested scope.
- Edit only files related to the assigned or requested work.
- Write a short update when done.
- Update its own task status if task mode is enabled.
- Remove its own lock when work is complete.

## Empty Project Setup

For an empty or nearly empty folder, the Lead may create:

- `AGENTS.md`
- `COLLAB_LOG.md`

The Lead may also suggest a light folder structure, but should not generate a heavy architecture unless the user asks for it.

The Lead should ask for or infer:

- Project name.
- Project goal.
- Expected tech stack.
- Whether task assignment mode is needed.
- Whether module ownership mode is needed.
- Whether a starter directory layout is wanted.

## Existing Project Setup

For an existing project, the Lead must inspect the current structure before adding collaboration files. At minimum, check:

- Existing `README.md`.
- Existing `AGENTS.md`, if present.
- Tech stack files such as `package.json`, `pyproject.toml`, `Cargo.toml`, or `go.mod`.
- Directories such as `src`, `app`, `lib`, `docs`, `tests`, `frontend`, or `backend`.
- Existing contribution or project rule files.
- Current Git status.

The Lead should respect the existing architecture. Do not rearrange folders just to match this workflow.

If the project already has rules or logs, merge carefully. If there is a conflict between existing project rules and the default Lite workflow, stop and ask:

```text
There is a conflict between existing project rules and the default collaboration workflow. Do you want to prioritize the existing project rules or adopt the recommended Lite rules?
```

Default recommendation: existing project rules win.

## Casual Coordination Mode

Casual Coordination Mode is the default.

It uses only:

- `AGENTS.md`
- `COLLAB_LOG.md`

Members work from the user's current instruction, check Active Work Locks before editing, and write concise updates afterward. There is no required task table or review queue.

## Optional Task Assignment Mode

Enable this only when the user wants formal task tracking.

When enabled, the Lead creates or updates `TEAM_TASKS.md` and uses simple statuses:

- `BACKLOG`
- `ASSIGNED`
- `IN_PROGRESS`
- `BLOCKED`
- `READY_FOR_REVIEW`
- `CHANGES_REQUESTED`
- `DONE`

Task entries should stay practical: owner, scope, goal, acceptance notes, blocker, and last update.

## Optional Module Ownership Mode

Enable this only when path or module boundaries matter.

When enabled, the Lead creates or updates `MODULE_OWNERSHIP.md` with:

- Module names.
- Owners.
- Allowed paths.
- Avoid or protected paths.
- Interface notes.
- Risks.
- Cross-module notes.

If the user does not want module ownership, do not create the file.

## Active Work Locks

`COLLAB_LOG.md` must keep `# Active Work Locks` near the top.

A lock is a soft coordination note:

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

Before larger read/write work, every agent should check for overlapping locks.

If there is no conflict, add a lock with the actor, role, scope, and expected work. If there is a conflict, do not edit. Tell the user which actor owns the overlapping scope and ask what to do.

If a lock looks stale, mark it as stale and ask before removing it. Suggested stale threshold: 2 hours.

## Markdown Files

| File | Required | Purpose |
| --- | --- | --- |
| `AGENTS.md` | Yes | Shared project rules, startup checklist, Git rules, logging rules, and conflict handling. |
| `COLLAB_LOG.md` | Yes | Active locks, current summary, blockers, decisions, updates, handoffs, and history. |
| `TEAM_TASKS.md` | Optional | Lightweight task table when Task Assignment Mode is enabled. |
| `MODULE_OWNERSHIP.md` | Optional | Module owners and path boundaries when Module Ownership Mode is enabled. |

Templates are available in [`templates/`](templates/).

## Example Tiny Team Flow

See [`examples/tiny-team-project`](examples/tiny-team-project/).

The example shows:

- Lead initializes `AGENTS.md` and `COLLAB_LOG.md`.
- User enables Task Assignment Mode.
- User skips Module Ownership Mode for now.
- Member checks locks, adds a lock, completes work, removes the lock, and writes a short update.
- Lead summarizes the log and updates the plan.

## Limitations

- This is a soft coordination workflow.
- It does not enforce OS-level permissions.
- It does not prevent someone from ignoring the rules.
- It works because agents are instructed to read and follow shared Markdown files.
- It is intentionally not a server, database, CLI, hook system, or enterprise permission model.

## Advanced Branches

Advanced local protocol experiments are preserved on the `standard-local-protocol` branch.

## Chinese

See [README.zh-CN.md](README.zh-CN.md).
