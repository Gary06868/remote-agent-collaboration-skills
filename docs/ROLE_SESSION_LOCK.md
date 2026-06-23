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

The hook-observed lock is written to `.collaboration-local/session-locks/<session_id>.json` with `session_id`, `role`, `actor_id`, `skill_name`, `fallback`, `source_event`, and `observed_events`. `collabctl doctor --json` treats only non-fallback hook-observed locks as evidence that Phase 0 role lock enforcement is active.

`PreToolUse` is responsible for passing that same `session_id` to controlled `collabctl` invocations. When the hook receives a `tool_input.command` that calls `collabctl` and the command does not already contain `--session-id`, it returns a modified tool input with `--session-id <session_id>` inserted immediately after `collabctl`. It also refreshes the hook-observed lock before the command runs.

`SubagentStart` uses the parent session id, records the inherited role, and returns `COLLAB_SESSION_ID`/`RAC_SESSION_ID` context for the subagent. It is not the only enforcement point; `UserPromptSubmit`, `PreToolUse`, and `collabctl` still enforce role consistency for activation and writes.

If `PreToolUse` is not observed running, or if Codex ignores hook-provided tool input modifications in the current build, `collabctl` remains authoritative: role-controlled writes without a session id fail closed with `SESSION_CONTEXT_MISSING`.

CLI `--session-id`, `COLLAB_SESSION_ID`, and `RAC_SESSION_ID` are local fallback paths for tests and debugging. They are marked `fallback: true` and do not make `doctor` healthy.
