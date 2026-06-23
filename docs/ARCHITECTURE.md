# Architecture

Remote Agent Collaboration uses three layers:

1. Two explicit Codex Skills define role behavior.
2. Hooks observe Codex thread events and pass session context when trusted and supported.
3. `collabctl` performs deterministic validation and writes protocol files.

If hooks are missing, untrusted, or not observed, `collabctl` role-controlled writes fail closed.
