# Vibe Coding Team Example

This example shows how a small human plus AI team can use Remote Agent Collaboration to keep a shared repository organized.

## Scenario

A two-person startup team is building an internal dashboard with help from multiple Codex threads:

- one human founder acts as project lead
- one Codex thread runs `$team-lead-collaboration`
- one or more Codex threads run `$team-member-collaboration`
- each member thread owns one module such as `docs`, `frontend`, `api`, or `tests`

The goal is not to replace code review or Git discipline. The goal is to make agent work visible: who owns what, what changed, which announcement matters, and when logs were compacted.

## Setup Flow

```bash
collabctl init --project-id startup-dashboard --yes
collabctl actor bootstrap --actor-id lead --role lead --yes
collabctl session activate --session-id thread-lead --role lead --skill team-lead-collaboration --actor-id lead
collabctl member add --session-id thread-lead --actor-id frontend-agent --role member --modules frontend
collabctl module add --session-id thread-lead --module-id frontend --members frontend-agent --allowed-paths src/frontend docs/frontend
```

The lead thread can now assign work:

```bash
collabctl task create --session-id thread-lead --task-id ui-001 --title "Implement dashboard shell" --module-id frontend --owner frontend-agent --allowed-paths src/frontend docs/frontend --tests "npm test"
```

The member thread activates its role and works only inside the assigned module:

```bash
collabctl session activate --session-id thread-frontend --role member --skill team-member-collaboration --actor-id frontend-agent
collabctl task accept --session-id thread-frontend --task-id ui-001
collabctl task start --session-id thread-frontend --task-id ui-001
collabctl log append --session-id thread-frontend --module-id frontend --task-id ui-001 --summary "Implemented shell navigation and empty dashboard state."
```

The member can request lead-only maintenance:

```bash
collabctl request create --session-id thread-frontend --request-id req-compact-frontend --type log_compaction --summary "Frontend log is ready for compaction."
```

The lead performs the privileged operation:

```bash
collabctl log compact --session-id thread-lead --module-id frontend
```

## Expected Guardrails

- If `thread-lead` later tries `$team-member-collaboration`, the session lock returns `ROLE_SESSION_CONFLICT`.
- If `thread-frontend` tries lead-only commands such as `member add` or `log compact`, `collabctl` returns `ROLE_NOT_AUTHORIZED`.
- If a write command lacks a real `session_id`, role-controlled writes fail closed with `SESSION_CONTEXT_MISSING`.
- Until real Codex hooks are observed running, `collabctl doctor --json` reports `role_lock_enforced=false`.
