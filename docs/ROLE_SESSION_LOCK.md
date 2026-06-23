# Role Session Lock

A real Codex `session_id` is required for role-controlled writes.

States:

```text
unbound -> lead_active
unbound -> member_active
lead_active -> lead_active
member_active -> member_active
lead_active -> member denied
member_active -> lead denied
closed -> no rebind
```

Missing session context returns `SESSION_CONTEXT_MISSING`.

## Session Context Handoff

`UserPromptSubmit` is responsible for binding the real Codex `session_id` to a selected role when the prompt explicitly contains `$team-lead-collaboration` or `$team-member-collaboration`.

`PreToolUse` is responsible for passing that same `session_id` to controlled `collabctl` invocations. When the hook receives a `tool_input.command` that calls `collabctl` and the command does not already contain `--session-id`, it returns a modified tool input with `--session-id <session_id>` inserted immediately after `collabctl`.

If `PreToolUse` is not observed running, or if Codex ignores hook-provided tool input modifications in the current build, `collabctl` remains authoritative: role-controlled writes without a session id fail closed with `SESSION_CONTEXT_MISSING`.
