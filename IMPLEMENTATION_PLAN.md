# Remote Agent Collaboration Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` or `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone public Codex Plugin repository that installs two collaboration Skills while enforcing one immutable role per real Codex thread.

**Architecture:** A plugin-first distribution packages two explicit-invocation Skills, trusted hooks, and a deterministic `collabctl` CLI. Hooks provide real Codex session context and early blocking; `collabctl` remains authoritative and fails closed for role-controlled writes without a verified `session_id`.

**Tech Stack:** Python 3.11+ standard library, pytest, Codex Skills/Plugins/Hooks, Git/GitHub CLI, SVG assets, generated terminal demo fixtures.

---

## Hard Rules

- First write is this file.
- Work only under `<PROJECT_ROOT>`.
- Do not initialize Git in the parent directory.
- Do not publish local absolute paths, private source names, private URLs, original commit SHAs, original branch names, internal permission details, or raw source documents.
- README Skill invocation syntax is only `$team-lead-collaboration` and `$team-member-collaboration`.
- `/plugins` is for plugin management; `/hooks` is for hook review/trust.
- If real Codex-thread role-lock validation fails, mark `FAILED CORE GATE`, set `role_lock_enforced=false`, and do not describe the version as fully enforcing thread-level mutual exclusion.

## Phase 0: Real Codex Hook Feasibility Gate

- [x] Create a minimal smoke fixture for Codex hooks.
- [x] Verify real Codex thread execution, and record that hooks were not observed in this environment.
- [x] Verify project-level hooks did not expose `session_id`, raw `prompt`, or `tool_input`.
- [x] Verify user-level fallback hooks did not expose `session_id`, raw `prompt`, or `tool_input`.
- [x] Verify current CLI rejects `--dangerously-bypass-hook-trust`.
- [x] Record that resumed-thread, concurrent-thread, and subagent hook enforcement cannot be honestly claimed without observed hook execution.
- [x] Record `enforcement_mode`: `failed_core_gate`.

## Phase 1: Repository Skeleton

- [x] Create package, docs, plugin, skills, hooks, tools, templates, demo, examples, tests, and CI directories.
- [x] Add MIT license, `.gitignore`, `pyproject.toml`, `README.md`, `README.zh-CN.md`, `AGENT_INSTALL.md`, `agent-install.json`, `SECURITY.md`, `CONTRIBUTING.md`, and `CHANGELOG.md`.
- [x] Add `.codex-plugin/plugin.json` and marketplace metadata.
- [x] Add two separate Skills with distinct `SKILL.md`, `agents/openai.yaml`, assets, examples, and tests.

## Phase 2: Deterministic Protocol Engine

- [x] Implement `collabctl` CLI.
- [x] Implement immutable session locks keyed by real `session_id`.
- [x] Implement hook context intake and fail-closed behavior for missing session context.
- [x] Implement actor, member, module, task, request, announcement, log, compaction, and Git preflight commands.
- [x] Implement append-only JSONL event storage, atomic writes, SHA-256 verification, and path confinement.

## Phase 3: Hooks, Installers, And Doctor

- [x] Implement `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `SubagentStart`, `SubagentStop`, and `Stop` hooks.
- [x] Implement install, uninstall, doctor, and plugin validation tools.
- [x] `doctor --json` reports `hooks_installed`, `hooks_trusted_or_observed_running`, `session_id_available`, `user_prompt_hook_operational`, `pre_tool_hook_operational`, `subagent_hook_operational`, `role_lock_enforced`, `enforcement_mode`, and `blocking_reasons`.
- [x] If hooks are untrusted or not observed running, doctor must not report healthy.

## Phase 4: Docs, Visuals, Demo, And Privacy

- [x] Write bilingual README with fixed AI Agent install sections.
- [x] Document tested install commands; current CLI lacks non-interactive plugin add/list JSON commands.
- [x] Create generic source-mechanism mapping without private source identifiers.
- [x] Generate original SVG hero, architecture, role-lock flow, icons, demo poster, and reproducible GIF from `collabctl` fixture output.
- [x] Add privacy scan across Markdown, JSON, YAML, Python, PowerShell, Bash, SVG, and demo scripts.

## Phase 5: Verification, GitHub, And Release

- [x] Run unit, smoke, docs, asset, demo, privacy, and packaging checks.
- [x] Run install-chain tests using actual local Codex CLI capabilities.
- [ ] Initialize independent Git repository under `<PROJECT_ROOT>`.
- [ ] Explicitly stage files; do not use blind `git add .`.
- [ ] Commit.
- [ ] Create public GitHub repository `remote-agent-collaboration-skills`.
- [ ] Configure `origin`, push `main`, and verify local and remote SHAs.
- [ ] Final report lists Phase 0 result, `role_lock_enforced`, `enforcement_mode`, role-conflict tests, concurrent-thread test, resume test, subagent prompt/write blocking, hook trust status, install commands, marketplace/plugin/Skill names, doctor JSON, compaction hash result, privacy scan result, README/demo paths, local commit SHA, GitHub URL, remote SHA, failures, and known limitations.
