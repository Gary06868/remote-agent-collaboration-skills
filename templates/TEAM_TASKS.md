# Team Tasks

Task Assignment Mode is optional. Use this file only when the user wants lightweight task tracking.

## Task Status Legend

- `BACKLOG`: not assigned yet.
- `ASSIGNED`: assigned but not started.
- `IN_PROGRESS`: actively being worked.
- `BLOCKED`: waiting on a decision or dependency.
- `READY_FOR_REVIEW`: ready for target reviewer review.
- `CHANGES_REQUESTED`: needs follow-up changes.
- `DONE`: complete.

## Current Tasks

Use actor IDs for owners. The display name can help humans read the file, but `Owner ID` is the stable identity.

In Remote Git Mode, `.collab/tasks/<task-id>.md` is authoritative state for each task. This root file is a derived snapshot that Lead may rebuild.

## TASK-001

- Status:
- Owner ID:
- Owner Display:
- Scope:
- Goal:
- Completion Policy: Lead review | User review | Member self-completion | Per-task decision
- Selected Completion Policy:
- Handoff Target Type: actor | human-user | none
- Handoff Target Actor ID:
- Handoff Target Human:
- Acceptance Notes:
- Blockers:
- Last Updated:
- Next Action:

## Backlog

- None.

## Review Queue

- None.

## Done

- None.

## Notes

- Keep tasks small enough for one contributor to understand.
- Record owner identity and repository-relative scope clearly.
- Do not use this file when Casual Coordination Mode is enough.
- Default Member completion status is `READY_FOR_REVIEW` unless `AGENTS.md`, the Lead, or the user says direct `DONE` is acceptable.
- Per-task decision requires an explicit selected completion policy; if missing, stop and ask.
- Review loops use `CHANGES_REQUESTED -> IN_PROGRESS -> READY_FOR_REVIEW` or `CHANGES_REQUESTED -> IN_PROGRESS -> DONE`.
- Do not invent commit SHAs; write `Not committed` when there is no commit.
