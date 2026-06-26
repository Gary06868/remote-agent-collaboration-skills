# Plugin Install Verification Report

Test date: 2026-06-25
Codex version: `codex-cli 0.130.0-alpha.5`
Operating system: Windows
Plugin name: `remote-agent-collaboration-lite`
Plugin display name: `Remote Agent Collaboration Lite`
Plugin version: `0.5.0`
Marketplace name: `remote-agent-collaboration-lite`

This report is sanitized. It does not include tokens, private local paths, temporary absolute paths, screenshots, or user configuration contents.

## Automated Checks

Post-merge marketplace add command documented for users:

```powershell
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills
```

Remote branch marketplace command actually run after branch push:

```powershell
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills --ref feature/codex-plugin-distribution
codex plugin marketplace remove remote-agent-collaboration-lite
```

Automated local marketplace command actually run:

```powershell
codex plugin marketplace add <PROJECT_ROOT>
codex plugin marketplace remove remote-agent-collaboration-lite
```

Result: Codex accepted marketplace `remote-agent-collaboration-lite` from `<PROJECT_ROOT>`, accepted the pushed GitHub branch marketplace, and each installed marketplace entry was removed after validation. The first remote attempt hit a transient GitHub HTTPS connection timeout; a retry succeeded after `git ls-remote` confirmed the branch commit.

Local CLI capability checks:

- `codex plugin marketplace add`: available.
- `codex plugin marketplace upgrade`: available.
- `codex plugin marketplace remove`: available.
- Non-interactive plugin install: NOT SUPPORTED by local CLI.
- `codex plugin add`: not available in this local CLI.
- `codex plugin list`: not available in this local CLI.
- `codex plugin marketplace list`: not available in this local CLI.

Manifest checks:

- Plugin manifest path: `plugins/remote-agent-collaboration-lite/.codex-plugin/plugin.json`.
- Marketplace metadata path: `.agents/plugins/marketplace.json`.
- Lead Skill bundled: yes.
- Member Skill bundled: yes.
- Lead references bundled: yes.
- Hooks installed: no.
- MCP server installed: no.
- Custom collaboration CLI installed: no.
- Background service installed: no.

## UI Checks

Plugin install via `/plugins`: NOT RUN
Lead Skill visible after UI install: NOT RUN
Member Skill visible after UI install: NOT RUN
Lead explicit invocation result: NOT RUN
Member explicit invocation result: NOT RUN
Plugin upgrade via UI: NOT RUN
Plugin uninstall via UI: NOT RUN
Other Skills unaffected by UI install: NOT RUN

These items are intentionally not marked PASS because this run could not automate the Codex plugin UI.

## Expected Manual Checklist

1. Run `codex plugin marketplace add Gary06868/remote-agent-collaboration-skills`.
2. Open `/plugins`.
3. Select the `Remote Agent Collaboration Lite` marketplace.
4. Install `Remote Agent Collaboration Lite`.
5. Start a fresh thread.
6. Verify both Skill names are separately visible:
   - `team-lead-collaboration`
   - `team-member-collaboration`
7. Start a Lead thread and invoke `$team-lead-collaboration`.
8. Start a Member thread and invoke `$team-member-collaboration`.
9. Confirm no hooks, custom collaboration CLI, background service, or project file mutation was introduced by plugin install.
10. Confirm uninstall or disable does not delete `AGENTS.md`, `COLLAB_LOG.md`, `TEAM_TASKS.md`, `MODULE_OWNERSHIP.md`, or `.collab/` from a test project.

## Notes

The Plugin is a distribution layer for two Markdown Skills. It is not a safety boundary and does not enforce role locks.
