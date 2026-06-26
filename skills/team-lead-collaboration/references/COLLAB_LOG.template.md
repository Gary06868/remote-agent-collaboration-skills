# Collaboration Log

> Read `AGENTS.md` before working.
> Project timezone:

Remote Git Mode note: `.collab/locks/<actor-id>.md` and `.collab/tasks/<task-id>.md` are authoritative state, `.collab/events/<timestamp>-<actor-id>.md` is an append-only event, and `.collab/snapshots/COLLAB_LOG.md` plus this root log are derived snapshot files. Lead may rebuild derived snapshots from authoritative state and events.

## Active Work Locks

Soft locks are coordination notes, not security locks.

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

Current locks:

- None.

## Current Snapshot

- Stage:
- Current focus:
- Active work:
- Next action:
- Last updated:
- Updated by:

## Active Blockers

- None.

## Open Handoffs

Only handoffs with `Status: open` or `Status: accepted` stay here. Move resolved or cancelled handoffs to History / Archived Notes.

Handoff targets must distinguish actor targets from human-user targets. Do not write `review target` into an Actor ID field.

```markdown
- Handoff ID:
  From Actor:
  Target Type: actor | human-user
  Target Actor ID:
  Target Human:
  Task:
  Scope:
  Required Next Action:
  Status: open | accepted | resolved | cancelled
  Created:
  Last Updated:
```

- None.

## Recent Decisions

- None.

## Latest Updates

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

- None.

## History / Archived Notes

- None.
