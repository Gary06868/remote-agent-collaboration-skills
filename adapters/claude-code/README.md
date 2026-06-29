# Claude Code Adapter

This is a Claude Code adapter for Remote Agent Collaboration Lite. It is not a native Claude plugin.

Use this adapter when a project wants the same Lead / Member collaboration behavior in Claude Code that Codex gets through the Plugin. Claude Code reads project instructions and prompts; the collaboration state remains ordinary project files.

## Files Used

- `AGENTS.md`: shared collaboration rules, actor identity, mode choices, and lock rules.
- `COLLAB_LOG.md`: active soft locks, current snapshot, blockers, handoffs, decisions, and updates.
- `TEAM_TASKS.md` optional: task owner, task status, completion policy, and review handoff.
- `MODULE_OWNERSHIP.md` optional: module owners, path boundaries, interfaces, and risks.
- `.collab/`: Remote Git Mode low-conflict locks, tasks, events, and snapshots.

## Start Claude Code

1. Copy [`CLAUDE.md`](CLAUDE.md) into the project root, or merge its rules into the existing project `CLAUDE.md`.
2. Start one Claude Code conversation as the Lead thread and paste [`lead-prompt.md`](lead-prompt.md).
3. Start one or more separate Claude Code conversations as Member threads and paste [`member-prompt.md`](member-prompt.md).
4. Keep one role per Claude thread. Do not switch a Lead thread into Member work or a Member thread into Lead coordination.

## Lead Thread

The Lead thread initializes or updates collaboration files, confirms the team model, chooses Shared Workspace Mode or Remote Git Mode, asks whether to enable Task Assignment Mode, asks whether to enable Module Ownership Mode, and produces Member startup prompts.

## Member Thread

The Member thread reads the collaboration files, confirms actor identity, checks soft locks before editing, declares scope, performs the assigned work, writes back an update or handoff, and releases or updates its lock.

## Boundaries

- Claude Code support is adapter-based support, not a native Claude plugin.
- Soft locks are coordination notes, not hard locks.
- The adapter does not add a server, database, custom collaboration CLI, hook, MCP server, daemon, or permission system.
- Follow the user's requested conversation language. If the user asks for documents in another language, write those documents in that requested language.
