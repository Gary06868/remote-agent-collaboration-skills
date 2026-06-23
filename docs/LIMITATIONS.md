# Limitations

- Current local Phase 0 validation failed to observe Codex hooks in `codex exec`.
- This release must not claim full thread-level role-lock enforcement until hooks are trusted and observed in real Codex threads.
- Subagent prompt blocking depends on `UserPromptSubmit` being available inside subagent turns.
- Subagent write blocking remains enforced by `PreToolUse` and `collabctl` when session context is available; without session context writes fail closed.
