# Promotion Kit

This kit is for launching Remote Agent Collaboration Lite v0.6.0.

## Positioning

Remote Agent Collaboration Lite is a Codex Plugin that installs two independent Markdown Skills, Lead and Member, for coordinating small human and AI coding teams in one repository.

Core message:

```text
Chat history is not coordination. Lite Collab gives Codex and other AI coding agents shared Markdown rules, soft locks, actor identity, and handoffs.
```

Short description:

```text
Codex Plugin with Lead/Member Skills for Markdown-based coordination across human and AI coding agents.
```

Primary call to action:

```powershell
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills
```

Then open `/plugins`, install `Remote Agent Collaboration Lite`, start a fresh thread, and activate exactly one role:

```text
$team-lead-collaboration
```

or:

```text
$team-member-collaboration
```

Support line:

```text
If this helps your AI coding workflow, a GitHub star helps others discover it.
```

## Future Demo Script

No video demo ships with v0.6.0. Use this later if a 60-90 second screen recording is produced.

1. Show the problem: two AI coding threads are about to edit the same repository.
2. Open the README and show that the Plugin installs two visible Skills.
3. Start a Lead thread with `$team-lead-collaboration`.
4. Show `AGENTS.md` and `COLLAB_LOG.md` being used as shared project state.
5. Start Member A and claim a writing lock for `README.md`.
6. Start Member B and attempt the same scope.
7. Show Member B detecting the overlap and stopping before business edits.
8. Show Member A finishing, releasing the lock, and creating a review handoff.
9. End on the key line: no server, no database, no hooks, no custom collaboration CLI.

Recommended title:

```text
Markdown soft locks for AI coding agents
```

## Show HN

Title:

```text
Show HN: Lite Collab - Markdown soft locks for AI coding agents
```

Post body:

```text
I built Remote Agent Collaboration Lite because chat history is a weak coordination layer when several AI coding agents work in the same repository.

It is a Codex Plugin that installs two Markdown Skills:
- team-lead-collaboration
- team-member-collaboration

The Skills coordinate through ordinary Markdown files: AGENTS.md, COLLAB_LOG.md, optional TEAM_TASKS.md, optional MODULE_OWNERSHIP.md, and optional .collab state for Remote Git Mode.

It intentionally does not add a server, database, hooks, custom collaboration CLI, daemon, or permission system. It is soft coordination: actor identity, soft locks, current snapshot, open handoffs, and final reconciliation.

Install:
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills

Then open /plugins and install Remote Agent Collaboration Lite.

I am looking for feedback from people running multiple Codex, Claude, Cursor, or other AI coding threads against the same repo.

If the idea is useful, starring the repo helps more AI coding users find it.
```

## Product Hunt

Name:

```text
Remote Agent Collaboration Lite
```

Tagline:

```text
Markdown soft locks for human and AI coding teams
```

Description:

```text
Remote Agent Collaboration Lite is a Codex Plugin for coordinating small teams of humans and AI coding agents. It installs two independent Markdown Skills, Lead and Member, and uses ordinary repository files for actor identity, soft locks, task status, current snapshots, and handoffs. No server, database, hooks, or custom collaboration CLI.
```

First comment:

```text
I built this after repeatedly seeing AI coding work spread across scattered chats, stale task notes, and duplicate edits.

Lite Collab keeps the protocol deliberately small: one Lead Skill, one Member Skill, Claude Code adapter prompts, and Markdown files that agents can read before editing. The v0.6.0 release improves the homepage, compatibility matrix, quick start, visual assets, and Plugin screenshots while keeping both Skills independently visible.

The main thing I want feedback on: how small can the coordination layer stay before teams really need a server or hard lock service?

If the project is useful, a GitHub star helps more AI coding users discover it.
```

Gallery asset checklist:

- One screenshot of the `/plugins` install entry.
- One diagram showing Plugin -> Lead Skill / Member Skill -> Markdown state.
- Optional future demo clip of overlapping `README.md` work being stopped by a soft lock.

## Social Posts

Short post:

```text
Released Remote Agent Collaboration Lite v0.6.0.

It is a Codex Plugin that installs Lead/Member Skills for coordinating multiple human and AI coding agents through Markdown soft locks, actor identity, and handoffs. Claude Code is supported through an adapter, not a native Claude plugin.

No server. No database. No hooks. No custom collaboration CLI. No video demo in this release.

https://github.com/Gary06868/remote-agent-collaboration-skills

If this helps your AI coding workflow, a GitHub star helps others discover it.
```

Developer-focused post:

```text
When several AI coding agents work in one repo, chat history is not enough.

Remote Agent Collaboration Lite v0.6.0 gives them:
- Lead and Member Skills
- Claude Code adapter prompts
- AGENTS.md and COLLAB_LOG.md
- actor identity
- soft locks
- task and handoff reconciliation
- Remote Git Mode Beta for different clones/worktrees
- refreshed README visuals and Plugin screenshots

Install:
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills

If this helps your AI coding workflow, a GitHub star helps others discover it.
```

## Community Reply Template

Use this when replying to a concrete multi-agent coordination problem.

```text
This is the exact problem Lite Collab tries to keep small: agents need a shared coordination surface before they edit, not another after-the-fact chat summary.

The approach is Markdown-only: Lead/Member Skills, actor identity, soft locks, current snapshot, and handoffs. It will not enforce permissions, but it makes well-instructed agents stop before conflicting edits.

Repo: https://github.com/Gary06868/remote-agent-collaboration-skills

If this helps your AI coding workflow, a GitHub star helps others discover it.
```

## Manual Launch Checklist

- Record or capture the `/plugins` install flow.
- Confirm both Skills are visible after UI install.
- Confirm uninstall or disable does not delete project collaboration files.
- Add a GitHub social preview image in repository settings.
- Post Show HN.
- Launch on Product Hunt.
- If a video is produced later, share the demo clip on X, LinkedIn, and relevant AI coding communities.
- Watch install issues for the first 48 hours.
