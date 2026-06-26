# Tiny Team Website Example

This tiny fixture shows a Lite collaboration state after one Lead and two Members coordinate on a small website README.

Scenario:

- Task Assignment Mode enabled.
- Module Ownership Mode not enabled yet.
- The Lead creates `TEAM_TASKS.md`.
- The Member reads `AGENTS.md`, `COLLAB_LOG.md`, and `TEAM_TASKS.md`.
- Alex's Codex #01 is the Lead and project coordinator.
- Morgan's Claude #01 is a Member and content developer.
- Alex's Codex #02 is a second Member and test engineer.

What the example demonstrates:

- Actor IDs are stable and unique.
- The same human owner can run multiple Codex instances with different instance numbers.
- A Member adds a writing lock for `README.md`.
- A second Member detects the overlapping lock and stops before editing business files.
- The first Member finishes TASK-001, removes the lock, and marks the task READY_FOR_REVIEW.
- Current Snapshot names the concrete review target.
- Open Handoffs contains only the unresolved review handoff.
- The old Lead-to-Member assignment handoff is archived as resolved.

This example intentionally stays small. It is a semantic fixture for the Markdown protocol, not a full project management demo.
