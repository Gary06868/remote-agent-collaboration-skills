# README Reference Audit

Audit date: 2026-06-23.

This project reviewed current public README structures from established developer-tool, CLI, and agent-adjacent repositories. The review used only information architecture patterns. It did not copy external wording, screenshots, brand assets, diagrams, examples, or repository-specific claims.

## Reviewed Repositories

| Repository | Why reviewed | Observed README pattern adopted here |
| --- | --- | --- |
| [openai/codex](https://github.com/openai/codex) | Terminal coding agent with plugin and local-environment expectations | Put agent-facing install and trust steps before deep protocol detail. |
| [astral-sh/uv](https://github.com/astral-sh/uv) | High-signal developer CLI README | Keep installation, verification, and command examples close together. |
| [cli/cli](https://github.com/cli/cli) | Mature CLI with clear user journeys | Use short command blocks and separate setup from reference material. |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Agent/tooling ecosystem repository | Name trust, security, and capability boundaries explicitly. |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | AI coding assistant with terminal-first workflow | Show real command-line flows instead of marketing screenshots. |
| [vercel/ai](https://github.com/vercel/ai) | SDK documentation with quick-start emphasis | Put the minimum viable path above conceptual architecture. |
| [supabase/cli](https://github.com/supabase/cli) | CLI for local and remote workflows | Include machine-readable verification commands. |
| [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) | Agent-adjacent recipe documentation | Keep examples task-focused and avoid overexplaining obvious UI controls. |

## Patterns Used

- First screen states the install requirement and one-role-per-thread rule.
- Agent installation has its own top-level section, so an AI worker can complete setup without reading the entire README.
- Commands are copyable and paired with verification output expectations.
- The demo asset is generated from a local fixture instead of using a fake product screenshot.
- Architecture is shown with original SVG diagrams committed to this repository.
- Limitations are visible near the top, including the failed real-hook gate in this environment.
- Trust and hook review are treated as required setup, not optional hardening.

## Patterns Rejected

- No copied badges, brand marks, screenshots, or prose from reviewed projects.
- No custom slash-command syntax that current Codex does not support.
- No claim that role-lock enforcement is healthy when real hooks were not observed.
- No install command remains documented unless it was tested against the local Codex CLI shape.
