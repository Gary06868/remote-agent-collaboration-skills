# Installation

Remote Agent Collaboration Lite is distributed as one Codex Plugin that bundles two independent Skills:

- `team-lead-collaboration`
- `team-member-collaboration`

The product remains Markdown-only. Installing the Plugin does not install hooks, a custom collaboration CLI, a background service, a database, or a runtime permission system.

## Option 1 - Codex Plugin

Plugin name: `remote-agent-collaboration-lite`
Marketplace name: `remote-agent-collaboration-lite`
Version: `0.6.0`

Add the repository marketplace:

```powershell
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills
```

Adding the marketplace does not install the Plugin. It only lets Codex discover the marketplace.

Install through Codex:

1. Open `/plugins`.
2. Select `Remote Agent Collaboration Lite`.
3. Install the Plugin.
4. Start a fresh thread.
5. Verify that both Skills are separately visible.
6. Activate exactly one role:
   - `$team-lead-collaboration`
   - `$team-member-collaboration`

This repository does not document `codex plugin add` as the install path because local `codex-cli 0.130.0-alpha.5` did not expose that command during verification.

Update the marketplace later:

```powershell
codex plugin marketplace upgrade remote-agent-collaboration-lite
```

Remove the marketplace entry:

```powershell
codex plugin marketplace remove remote-agent-collaboration-lite
```

## Option 2 - Built-in Skill Installer

`$skill-installer` may be useful for local experiments, but it is not documented here as a supported installation path for this repository because this release did not verify that it installs both Skill directories and the Lead `references/` folder in one reliable flow.

## Option 3 - Manual Copy

Use manual copy only for development or fallback. Current Codex Skills documentation describes `.agents/skills` as the user and repository Skill discovery path.

### User-Level Install

Windows PowerShell:

```powershell
$skills = Join-Path $env:USERPROFILE ".agents\skills"
New-Item -ItemType Directory -Force $skills | Out-Null
Remove-Item -Recurse -Force (Join-Path $skills "team-lead-collaboration") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $skills "team-member-collaboration") -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force .\skills\team-lead-collaboration (Join-Path $skills "team-lead-collaboration")
Copy-Item -Recurse -Force .\skills\team-member-collaboration (Join-Path $skills "team-member-collaboration")
Get-ChildItem $skills | Where-Object Name -in @("team-lead-collaboration", "team-member-collaboration")
```

macOS/Linux:

```bash
mkdir -p "$HOME/.agents/skills"
rm -rf "$HOME/.agents/skills/team-lead-collaboration"
rm -rf "$HOME/.agents/skills/team-member-collaboration"
cp -R skills/team-lead-collaboration "$HOME/.agents/skills/team-lead-collaboration"
cp -R skills/team-member-collaboration "$HOME/.agents/skills/team-member-collaboration"
find "$HOME/.agents/skills" -maxdepth 1 -type d \( -name team-lead-collaboration -o -name team-member-collaboration \)
```

### Project-Level Install

Use this when a repository wants to carry its own Skill copies:

Windows PowerShell:

```powershell
$skills = Join-Path (Get-Location) ".agents\skills"
New-Item -ItemType Directory -Force $skills | Out-Null
Remove-Item -Recurse -Force (Join-Path $skills "team-lead-collaboration") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $skills "team-member-collaboration") -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force .\skills\team-lead-collaboration (Join-Path $skills "team-lead-collaboration")
Copy-Item -Recurse -Force .\skills\team-member-collaboration (Join-Path $skills "team-member-collaboration")
Get-ChildItem $skills
```

macOS/Linux:

```bash
mkdir -p .agents/skills
rm -rf .agents/skills/team-lead-collaboration
rm -rf .agents/skills/team-member-collaboration
cp -R skills/team-lead-collaboration .agents/skills/team-lead-collaboration
cp -R skills/team-member-collaboration .agents/skills/team-member-collaboration
find .agents/skills -maxdepth 1 -type d
```

The manual copy commands are safe to run repeatedly. They remove only the two target Skill directories and preserve unrelated Skills.

## Verification

After any install path:

1. Start a fresh thread.
2. Confirm both Skill names are visible:
   - `team-lead-collaboration`
   - `team-member-collaboration`
3. In a Lead thread, explicitly call `$team-lead-collaboration`.
4. In a separate Member thread, explicitly call `$team-member-collaboration`.
5. Do not activate both roles in one thread.

Plugin uninstall or marketplace removal must not delete collaboration files from a project: `AGENTS.md`, `COLLAB_LOG.md`, `TEAM_TASKS.md`, `MODULE_OWNERSHIP.md`, or `.collab/`.

If the Plugin helps your AI coding workflow, please star the repository so more users can discover it:

```text
https://github.com/Gary06868/remote-agent-collaboration-skills
```

See the live verification notes in [tests/plugin-install/README.md](../tests/plugin-install/README.md).
