# Agent Install

Preferred tested marketplace command shape:

```bash
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills
```

Then use `/plugins` to install **Remote Agent Collaboration**.

This Codex CLI build does not provide tested `codex plugin add --json` or `codex plugin list --json`; do not document those as working for this release.

After installation:

1. Open `/hooks`.
2. Review and trust hooks.
3. Start a new thread.
4. Invoke exactly one role with `$team-lead-collaboration` or `$team-member-collaboration`.
5. Run `collabctl doctor --json`.
6. Report `role_lock_enforced`, `enforcement_mode`, and `blocking_reasons`.
