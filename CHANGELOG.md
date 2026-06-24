# Changelog

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
