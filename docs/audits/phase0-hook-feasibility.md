# Phase 0 Hook Feasibility

Status: `FAILED CORE GATE`

Observed in this development environment:

- A real `codex exec` thread was created and returned a thread id.
- The thread executed a shell command, proving tool execution occurred.
- Project-level hooks did not produce observations.
- User-level fallback hooks did not produce observations.
- `codex exec --dangerously-bypass-hook-trust` is rejected by this local CLI build.

Result:

- `role_lock_enforced=false`
- `enforcement_mode=failed_core_gate`
- Role-controlled `collabctl` writes fail closed when `session_id` is missing.
- This release must not be described as fully enforcing thread-level mutual exclusion until hooks are trusted and observed running in real Codex threads.

Subagent notes:

- `SubagentStart` cannot be relied on to block startup.
- It is implemented only to inherit/record parent context.
- Opposite role prompt blocking depends on `UserPromptSubmit`.
- Write operation blocking remains enforced by `PreToolUse` and `collabctl` when session context is available; without session context, writes fail closed.
