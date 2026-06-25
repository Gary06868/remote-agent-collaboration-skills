# Codex Plugin Distribution Audit

Test date: 2026-06-25
Codex version: `codex-cli 0.130.0-alpha.5`
Product version: `0.5.0`

This audit records the distribution decisions for Remote Agent Collaboration Lite. The product remains Markdown Skills plus Markdown templates. Plugin is packaging only.

## Sources Checked

- Current OpenAI Codex Plugin documentation.
- Current OpenAI Codex Skills documentation.
- Local Codex CLI help output.
- Installed Superpowers plugin structure under the local Codex plugin cache.
- Local system `plugin-creator` Skill reference and validator.

## Verified Plugin Structure

The required plugin manifest path is `.codex-plugin/plugin.json`.

Superpowers uses this shape:

- `.codex-plugin/plugin.json`
- `assets/`
- `skills/`

Its manifest declares `"skills": "./skills/"` and does not need one manifest entry per Skill. Remote Agent Collaboration Lite reuses this distribution model with its own name, icon, metadata, and two Skill folders.

Remote Agent Collaboration Lite differs from Superpowers:

- It is a two-role collaboration workflow, not a general software methodology.
- It uses explicit Skill activation instead of implicit role detection.
- It does not copy Superpowers branding, icon, screenshots, or text.
- It does not install hooks, MCP servers, apps, a custom collaboration CLI, a daemon, or a permission system.

## Marketplace Structure

The repo marketplace file is `.agents/plugins/marketplace.json`.

The marketplace name is `remote-agent-collaboration-lite`.

The plugin entry points to:

```json
{
  "source": "local",
  "path": "./plugins/remote-agent-collaboration-lite"
}
```

The plugin manifest is at:

```text
plugins/remote-agent-collaboration-lite/.codex-plugin/plugin.json
```

## CLI Behavior Observed

`codex plugin marketplace add` is available.

These commands were present in local help:

- `codex plugin marketplace add <SOURCE>`
- `codex plugin marketplace upgrade [MARKETPLACE_NAME]`
- `codex plugin marketplace remove <MARKETPLACE_NAME>`

These commands were not available in this local CLI even though current web documentation references some of them:

- `codex plugin add`
- `codex plugin list`
- `codex plugin remove`
- `codex plugin marketplace list`

Because `codex plugin add` is not available in this local CLI, the README does not document it as an install command. Installation uses `/plugins` after adding the marketplace.

## Skill Paths

Current Codex Skills documentation says Codex reads Skills from repository, user, admin, and system locations. For repository and user-authored Skills, the documented paths include:

- `$CWD/.agents/skills`
- `$REPO_ROOT/.agents/skills`
- `$HOME/.agents/skills`

This machine also has older user Skill folders under a Codex-specific home directory, but this release does not make that older location the documented default.

## Verified Commands

Verified locally:

```powershell
codex --version
codex plugin --help
codex plugin marketplace --help
codex plugin marketplace add --help
codex plugin marketplace upgrade --help
codex plugin marketplace remove --help
```

Marketplace add against this repository is recorded in [tests/plugin-install/README.md](../tests/plugin-install/README.md). UI plugin installation through `/plugins` was not automated in this run.

Automated marketplace add/remove was verified with the local repository root:

```powershell
codex plugin marketplace add <PROJECT_ROOT>
codex plugin marketplace remove remote-agent-collaboration-lite
```

Codex accepted the marketplace name `remote-agent-collaboration-lite` and resolved the installed marketplace root to `<PROJECT_ROOT>`.

After the development branch was pushed, marketplace add/remove was also verified against the GitHub repository branch:

```powershell
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills --ref feature/codex-plugin-distribution
codex plugin marketplace remove remote-agent-collaboration-lite
```

The first remote add attempt hit a transient GitHub HTTPS connection timeout. `git ls-remote` confirmed the pushed branch was visible on GitHub, and the next `codex plugin marketplace add` attempt succeeded.

## Unverified Capabilities

- Non-interactive Plugin install: not supported by local CLI.
- Non-interactive Plugin list: not supported by local CLI.
- `/plugins` UI install: requires manual UI validation.
- `$skill-installer` install of both repository Skill folders in one reliable flow: not verified.
- macOS Plugin install: not run.

## Product Boundary

Plugin is packaging only. It does not change the Lite protocol or turn soft locks into security locks.

Remote Agent Collaboration Lite still consists of:

- two Markdown Skills;
- Markdown templates;
- ordinary project Markdown state files;
- optional Git as synchronization transport for Remote Git Mode.

No hooks, custom collaboration CLI, session lock, Phase 0 gate, doctor command, server, database, or runtime permission system is part of this Lite release.
