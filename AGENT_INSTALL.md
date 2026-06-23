# Agent Install

Remote Agent Collaboration is for small teams using Codex as more than a single assistant. Install it when a project needs one lead thread to coordinate announcements, tasks, reviews, and log compaction while member threads work inside assigned modules.

Preferred tested marketplace command shape:

```bash
codex plugin marketplace add Gary06868/remote-agent-collaboration-skills
```

If HTTPS clone is blocked on the current network, this SSH-over-443 fallback is also tested:

```bash
codex plugin marketplace add ssh://git@ssh.github.com:443/Gary06868/remote-agent-collaboration-skills.git
```

Then use `/plugins` to install **Remote Agent Collaboration**.

This Codex CLI build does not provide tested `codex plugin add --json` or `codex plugin list --json`; do not document those as working for this release.

After installation:

1. Open `/hooks`.
2. Review and trust hooks.
3. Start a new thread.
4. Invoke exactly one role with `$team-lead-collaboration` or `$team-member-collaboration`.
5. Run `collabctl doctor --json`.
6. Report `role_lock_enforced`, `enforcement_mode`, and `blocking_reasons`.

Phase 0 passes only when trusted hooks observe a real Codex `session_id` and write `.collaboration-local/session-locks/<session_id>.json`. If hooks are not trusted, or if the thread was not restarted after trust, `doctor` must report `role_lock_enforced: false` and must not report healthy.

Local debugging fallback:

```bash
collabctl session activate --session-id local-thread --role lead --skill team-lead-collaboration --actor-id lead
collabctl doctor --json
```

or:

```bash
COLLAB_SESSION_ID=local-thread collabctl session status
```

Fallback locks are marked `fallback: true`; they are useful for tests and CLI development but do not prove real Codex thread mutual exclusion.
