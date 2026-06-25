# Test Plan: Remote Agent Collaboration Lite

## Project Understanding

Remote Agent Collaboration Lite is a Markdown-only collaboration workflow for a small project lead and multiple contributors. It ships two Skills, `team-lead-collaboration` and `team-member-collaboration`, plus reusable templates and one tiny example.

The pain point is coordination drift: scattered chat history, duplicate edits, unclear scope ownership, and agents guessing through conflicts. The project intentionally avoids infrastructure: no server, database, custom collaboration CLI, hooks, or hard permission model.

The implementation method is a document protocol:

- `AGENTS.md` records shared rules, Actor Registry, startup checks, Git rules, logging rules, and when to ask.
- `COLLAB_LOG.md` records Active Work Locks, Current Snapshot, blockers, Open Handoffs, decisions, updates, and history.
- `TEAM_TASKS.md` is optional and only appears when Task Assignment Mode is enabled.
- `MODULE_OWNERSHIP.md` is optional and only appears when Module Ownership Mode is enabled.
- Lead and Member Skills keep context separated: Lead initializes/coordinates, Member executes assigned work without taking over project-wide decisions.

## Test Strategy

Because there is no runtime code, tests focus on static protocol contracts and example consistency.

| ID | Area | Goal | Method |
| --- | --- | --- | --- |
| TP-001 | Product boundary | Verify docs still describe the Lite product and do not imply enforcement infrastructure. | README and CONTRIBUTING contract tests. |
| TP-002 | Lead/Member isolation | Verify each Skill is explicit-only and prevents role bleed. | Skill text contract tests. |
| TP-003 | Mode selection | Verify task and module files remain opt-in and user-confirmed. | Lead Skill and template checks. |
| TP-004 | Actor identity | Verify stable actor fields and Actor Registry appear in Skills, templates, and examples. | Identity contract tests. |
| TP-005 | Soft locks | Verify lock fields and reading/writing/paused semantics are consistent across Lead, Member, README, and templates. | Shared field and conflict semantic tests. |
| TP-006 | Template completeness | Verify templates contain the operational sections needed by agents and Lead carries self-contained copies. | Template heading, content, and copy-install checks. |
| TP-007 | Example flow | Verify the tiny-team example matches the advertised Lead/Member lifecycle and reconciled READY_FOR_REVIEW state. | Semantic consistency tests. |
| TP-008 | Link/privacy integrity | Verify local Markdown links resolve and tracked public files do not expose local/private source terms. | Local link and privacy tests. |
| TP-009 | Remote Git Mode | Verify a bare remote with two independent clones handles same-scope competition, different-scope parallel locks, and non-fast-forward rechecks. | Real Git integration tests in temporary directories. |
| TP-010 | Completion policies | Verify Lead review, User review, Member self-completion, Per-task decision, and review loops are represented without fake Actor IDs. | `.collab/tasks` and `.collab/events` fixture tests. |
| TP-011 | Install idempotency | Verify repeated copy installs remove stale files, avoid nested Skill dirs, preserve unrelated Skills, and keep Lead references. | Temporary install directory tests. |
| TP-012 | CI | Verify GitHub Actions runs tests on push and pull_request for Ubuntu and Windows. | Workflow contract test. |
| TP-013 | Plugin distribution | Verify one Codex Plugin bundles both Skills, the marketplace metadata is parseable, README uses plugin-first install, no hooks/custom collaboration CLI/server are reintroduced, and manual fallback paths use `.agents/skills`. | Plugin manifest, marketplace, install-report, archive, privacy, BOM, and docs contract tests. |

## Automated Test Command

Run from the repository root:

```powershell
python -m unittest discover -s tests -v
```

If `python` is not on PATH on Windows, use:

```powershell
py -m unittest discover -s tests -v
```

## Manual Review Checklist

- Confirm README first screen still positions the repository as a lightweight Markdown Skill workflow.
- Confirm neither Skill claims hard locking, permissions, hooks, a custom collaboration CLI, or a server.
- Confirm Member behavior stops and asks on conflicting locks or unclear actor/scope.
- Confirm Lead behavior asks before enabling optional task or module ownership modes.
- Confirm Actor Registry uses stable actor IDs rather than task names.
- Confirm Current Snapshot, TEAM_TASKS.md, and Open Handoffs describe the same current state.
- Confirm Remote Git Mode uses `.collab/locks`, `.collab/tasks`, `.collab/events`, and `.collab/snapshots` instead of requiring every agent to rewrite root aggregate files.
- Confirm completion policy does not use `review target` as an Actor ID.
- Confirm example files remain small enough for a new contributor to understand quickly.
- Confirm README says "No server, no database, no hooks, and no custom collaboration CLI" instead of implying Codex itself has no CLI.
- Confirm README separates Workspace Topology from Workflow Options and labels Remote Git Mode as Beta.
- Confirm Codex/Claude compatibility is documented without turning the product into an environment-specific CLI workflow.
- Confirm Plugin installation is first, `$skill-installer` is not claimed as verified, and manual copy remains a development/fallback path.

## Review Findings

Resolved in the current Lite protocol:

- `Active Work Locks` wording is now heading-level neutral in README, Skills, and templates. Templates and examples can use `## Active Work Locks` under the document title.
- `COLLAB_LOG.md` ordering is consistent: Active Work Locks appear before Current Snapshot because conflict avoidance depends on early lock visibility.
- Open Handoffs only keeps unresolved handoffs; resolved or cancelled handoffs move to History / Archived Notes.
- Actor identity fields now include human owner, agent platform, collaboration role, functional role, instance, actor ID, and display name.
- Remote Git Mode adds low-conflict authoritative state and append-only events under `.collab/`.
- Completion Policy is parameterized across Lead review, User review, Member self-completion, and Per-task decision.
- Handoff targets distinguish actor targets from human-user targets.
- `TEAM_TASKS.md` is now clearly tied to Task Assignment Mode. If the file exists while `AGENTS.md` says task mode is disabled, members treat it as legacy/reference material and ask before using or updating it.
- Stale-lock handling is strict: mark or report stale status, but do not remove another actor's lock without user confirmation.
- Default member completion in task mode is `READY_FOR_REVIEW` unless `AGENTS.md`, the Lead, or the user says direct `DONE` is acceptable.
- Scope-overlap guidance now names common overlap cases: same path, same folder/module, broad module locks, and shared interfaces.
- QA reject follow-up fixes are covered: the privacy scanner no longer treats diagnostic labels as Windows drive paths, public tests do not embed reconstructible private source terms, Actor Registry status semantics are defined, and multi-path scope canonicalization is canonical.
- 0.5.0 Plugin distribution keeps Lite Markdown-only: one Plugin bundles the Lead and Member Skills, the Plugin has no hooks/MCP/custom CLI/service surface, README distinguishes marketplace add from Plugin install, and manual copy uses `.agents/skills`.

## Execution Log

- Status: executed on the Codex Plugin distribution branch.
- Commands:
  - `python -m unittest discover -s tests -v`
  - `.venv\Scripts\python.exe -m pytest -q`
- Result:
  - `python -m unittest discover -s tests -v`: PASS, 68 tests.
  - `.venv\Scripts\python.exe -m pytest -q`: PASS, 68 tests and 484 subtests.
- Notes: Current suite covers actor identity, Actor Registry status semantics, scope canonicalization, log/task/handoff semantic consistency, Remote Git Mode, real two-clone lock races, install docs, install idempotency, self-contained Lead templates, E2E report, plugin packaging, repository marketplace metadata, archive contents, link checks, CI workflow, privacy scan, and BOM scan.
