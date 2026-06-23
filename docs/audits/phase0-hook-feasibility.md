# Phase 0 Hook Feasibility

Status: `HOOK_GATE_IMPLEMENTED`

Earlier observation in this development environment:

- A real `codex exec` thread was created and returned a thread id.
- The thread executed a shell command, proving tool execution occurred.
- Project-level hooks did not produce observations.
- User-level fallback hooks did not produce observations.
- `codex exec --dangerously-bypass-hook-trust` is rejected by this local CLI build.

Current implementation result:

- `UserPromptSubmit` binds the real hook-provided `session_id` to exactly one role.
- `PreToolUse` records the observed session lock in `.collaboration-local/session-locks/<session_id>.json` and injects `--session-id` into controlled `collabctl` commands.
- `SubagentStart` inherits the parent session context and records the inherited role.
- `collabctl doctor --json` reports `role_lock_enforced=true` when a non-fallback hook-observed session lock exists.
- Local `--session-id` and `COLLAB_SESSION_ID` remain fallback-only and keep `role_lock_enforced=false`.

Untrusted-hook result:

- `role_lock_enforced=false`
- `enforcement_mode=failed_core_gate`
- Role-controlled `collabctl` writes fail closed when `session_id` is missing.
- This release must not be described as enforcing thread-level mutual exclusion until hooks are trusted in `/hooks`, a new Codex thread is started, and hook observations are present.

Subagent notes:

- `SubagentStart` cannot be relied on to block startup.
- It is implemented only to inherit/record parent context.
- Opposite role prompt blocking depends on `UserPromptSubmit`.
- Write operation blocking remains enforced by `PreToolUse` and `collabctl` when session context is available; without session context, writes fail closed.
