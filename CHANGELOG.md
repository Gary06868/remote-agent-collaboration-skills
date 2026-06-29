# Changelog

## 0.6.0

- Added the Claude Code adapter with project rules plus Lead and Member startup prompts.
- Reworked the README homepage around a stronger hero, compatibility matrix, 30-second quick start, mode selection table, and soft-lock conflict example.
- Added visual assets for the README and Plugin screenshots while keeping the original Plugin cover and icon.
- Switched the README build status from a static badge to the GitHub Actions workflow badge.
- Kept the release intentionally lightweight: no video demo, no server, no database, no hooks, no custom collaboration CLI, no MCP server, no daemon, and no runtime permission system.
- Documented Claude Code as adapter-based support and avoided claiming a native Claude plugin.

## 0.5.0

- Added Codex Plugin packaging for the Lite product.
- Added repository marketplace distribution for `remote-agent-collaboration-lite`.
- One Plugin now installs both Lead and Member Skills while keeping them independently visible.
- Added Plugin-first installation docs and an AI Agent verification section.
- Recorded the current Codex Plugin and Skills audit in `docs/CODEX_PLUGIN_DISTRIBUTION_AUDIT.md`.
- Corrected manual Skill installation paths to the current `.agents/skills` locations.
- Added plugin manifest, marketplace, install-report, idempotency, archive, privacy, and BOM tests.
- Added a Skill language policy so replies follow the user's prompt language and documents can use a separately requested language.
- No hooks, custom collaboration CLI, server, database, session lock, doctor flow, or runtime permission system were added.

## 0.4.0

- Added explicit Shared Workspace Mode and Remote Git Mode so agents do not mix same-directory assumptions with different-clone collaboration.
- Added the Remote Git Mode lock protocol: candidate lock commit, push, non-fast-forward recovery, re-read/recheck, no force push, and lifecycle states for acquire, refresh, pause, resume, release, stale, and abandoned.
- Added low-conflict Remote Git Mode Markdown state under `.collab/locks`, `.collab/tasks`, `.collab/events`, and `.collab/snapshots`.
- Parameterized Completion Policy across Lead review, User review, Member self-completion, and Per-task decision.
- Split handoff targets into actor targets and human-user targets; `review target` is no longer valid as an Actor ID.
- Added real temporary bare-remote/two-clone tests for same-scope competition, different-scope parallel locks, and non-fast-forward recheck behavior.
- Added repeated install idempotency tests and GitHub Actions for Ubuntu and Windows.

## 0.3.0

- Added the Lite Actor Identity Protocol with stable `actor_id`, human owner, agent platform, collaboration role, functional role, and instance fields.
- Added Actor Registry guidance to `AGENTS.md` and aligned task, lock, update, decision, and handoff identity rules.
- Replaced stale summary language with Current Snapshot and Open Handoffs semantics.
- Added Final Reconciliation rules so tasks, locks, snapshots, and handoffs stay consistent after major work.
- Made the Lead Skill self-contained by carrying synchronized templates in `skills/team-lead-collaboration/references/`.
- Reworked the tiny-team example to demonstrate three unique actors, overlapping-lock conflict stop, READY_FOR_REVIEW, and resolved handoff archival.
- Reworked README install instructions around verified file-copy installation and removed unverified marketplace claims.

## 0.2.0

- Repositioned `main` as Remote Agent Collaboration Lite.
- Kept only the Markdown Skill workflow on `main`.
- Added reusable templates for `AGENTS.md`, `COLLAB_LOG.md`, optional `TEAM_TASKS.md`, and optional `MODULE_OWNERSHIP.md`.
- Added a tiny-team example that demonstrates Lead/Member coordination with soft locks.
- Preserved advanced local protocol experiments on the `standard-local-protocol` branch.

## 0.1.0

- Initial dual-Skill collaboration protocol experiment.
