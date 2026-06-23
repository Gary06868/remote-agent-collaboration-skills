# Security

Remote Agent Collaboration is a repository protocol and Codex workflow guardrail. It is not an operating-system sandbox, a permissions system enforced by the kernel, or a cryptographic access-control boundary.

Important limits:

- Hooks must be reviewed and trusted before they run.
- If hooks do not run, `role_lock_enforced` must be false.
- Role-controlled `collabctl` writes fail closed without a real session context.
- Claims and leases are advisory coordination tools, not distributed locks.
- Original logs are preserved during compaction; AI summaries never replace archives.

Do not store tokens, private keys, cookies, passwords, `.env` files, or local session locks in Git.
