# Tiny Team Project Example

This example shows how Remote Agent Collaboration Lite works in a small project with one Lead thread and one Member thread.

The team chooses:

- Casual Coordination Mode as the base mode.
- Task Assignment Mode enabled.
- Module Ownership Mode not enabled yet.

Files:

- `AGENTS.md`: project rules and Git collaboration rules.
- `COLLAB_LOG.md`: Active Work Locks and short updates.
- `TEAM_TASKS.md`: optional task tracking.

## Flow

1. The Lead starts with `$team-lead-collaboration`.
2. The Lead checks that this is an existing tiny web project.
3. The Lead creates `AGENTS.md` and `COLLAB_LOG.md`.
4. The Lead asks: "Do you want to enable Task Assignment Mode?"
5. The user says yes.
6. The Lead creates `TEAM_TASKS.md`.
7. The Lead asks: "Do you want to define module boundaries and owners now?"
8. The user says not yet.
9. The Member starts with `$team-member-collaboration`.
10. The Member reads `AGENTS.md`, `COLLAB_LOG.md`, and `TEAM_TASKS.md`.
11. The Member checks Active Work Locks.
12. The Member adds a lock for `README.md`.
13. The Member finishes, removes the lock, and writes a Latest Update.
14. The Lead summarizes the log and updates the next plan.

This example is intentionally small. It is a workflow pattern, not an enterprise process.
