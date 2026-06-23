# Plan Compliance Audit

Audit date: 2026-06-23.

This document records plan-execution gaps found after the initial implementation and the corrective action taken. It exists so the repository does not rely on chat-only claims.

## Corrected Gaps

| Gap | Risk | Correction |
| --- | --- | --- |
| Hook entry scripts imported `remote_agent_collaboration` directly. | Plugin-bundled hooks could fail when the Python package was not installed in the active environment. | Added `hooks/_bootstrap.py` and imported it from every hook entrypoint so the repository `src/` directory is added to `sys.path` before runtime imports. |
| `PreToolUse` only set an environment variable inside the hook process. | That environment change would not reliably reach the later `collabctl` command. | `PreToolUse` now returns modified tool input for `collabctl` commands by injecting `--session-id <session_id>` when absent. |
| The plan completion checkbox was marked in `IMPLEMENTATION_PLAN.md`, but the repository had no durable compliance-audit artifact. | The final-report requirement was only visible in chat and could not be reviewed from the repo. | Added this audit file and kept Phase 0 failure details in `docs/audits/phase0-hook-feasibility.md`. |
| The primary marketplace command can fail on networks where HTTPS Git clone is blocked. | AI agents following only the primary path may stop during install. | Documented the tested SSH-over-443 fallback in `README.md`, `README.zh-CN.md`, `AGENT_INSTALL.md`, and `agent-install.json`. |

## Still Not Claimable

These items remain blocked by the real Codex hook gate and must not be described as fully implemented:

- `role_lock_enforced=true`
- real-thread prompt activation blocking via trusted plugin hooks
- real-thread `PreToolUse` command modification acceptance by Codex
- subagent prompt activation blocking
- full subagent role-lock enforcement

The deterministic `collabctl` layer still enforces role checks and fail-closed behavior for role-controlled writes.

## Verification Added

- Hook script bootstrap test without `PYTHONPATH`.
- `PreToolUse` command rewrite test.
- Duplicate `--session-id` prevention test.
- Multiple-role `UserPromptSubmit` rejection test.
