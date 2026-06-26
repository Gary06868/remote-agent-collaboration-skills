# Remote Git Mode

Remote Git Mode (Beta) is for different machines, clones, or worktrees coordinating through a Git remote. It is a topology, not a task workflow. A team can use Casual Coordination Mode or Task Assignment Mode inside either Shared Workspace Mode or Remote Git Mode.

Do not mix assumptions between these modes. Shared Workspace Mode can rely on the same working directory and immediate local reads. Remote Git Mode must assume another participant can publish changes from a different clone between any two local commands.

Git is only the synchronization transport. It is not a permission service, a lock server, or a runtime daemon.

## Low-Conflict State Layout

| Path | Type | Rule |
| --- | --- | --- |
| `.collab/locks/<actor-id>.md` | authoritative state | One actor owns one lock file. It records current lock state for that actor. |
| `.collab/tasks/<task-id>.md` | authoritative state | One task owns one task file. It records status, owner, scope, completion policy, and review target. |
| `.collab/events/<timestamp>-<actor-id>.md` | append-only event | One event per file. Do not rewrite old event files except to correct private data before sharing. |
| `.collab/snapshots/COLLAB_LOG.md` | derived snapshot | Lead may rebuild this from locks, tasks, and events. |
| `COLLAB_LOG.md` | derived snapshot | In Remote Git Mode, this is a human-readable aggregate that Lead may rebuild. |

Use `.collab/*` as the Remote Git Mode source of truth. Root files stay useful for humans, but the low-conflict files reduce repeated rewrites of `COLLAB_LOG.md` and `TEAM_TASKS.md`.

## Remote Git Mode Lock Protocol

Before modifying business files in Remote Git Mode:

1. fetch the latest remote state.
2. Re-read `.collab/locks/*.md` and `.collab/tasks/*.md`.
3. Check existing locks for scope overlap.
4. create a candidate lock record in `.collab/locks/<actor-id>.md`.
5. commit only the candidate lock.
6. push the candidate lock to the collaboration branch.
7. If push reports non-fast-forward, fetch, rebase or reapply the candidate lock, re-read all locks, and re-evaluate scope overlap.
8. Do not blindly repeat push.
9. Do not force push.
10. Only edit business files after the candidate lock is published and rechecked on the latest remote state.

If two actors compete for the same scope, only one may continue. The losing actor must withdraw the candidate lock and stop before business edits.

## Lock Lifecycle

- acquire: publish a candidate lock, re-check latest remote state, then treat it as acquired.
- refresh: update `Last Updated` before continuing long work.
- pause: keep the scope reserved while temporarily stopped.
- resume: the same actor returns and refreshes the lock before editing.
- release: remove or mark the actor's lock released after work and reconciliation.
- stale: a lock is older than the stale threshold; ordinary Members report it but do not delete it.
- abandoned: Lead or explicit user decision marks a stale/crashed lock abandoned so others can proceed.

## Non-Fast-Forward Recovery

A non-fast-forward push means the local clone is behind the remote. The actor must fetch, rebase or reapply the candidate lock, re-read all locks, and re-evaluate scope overlap before trying again.

The actor must not blindly repeat push. The actor must not force push. If the new remote state reveals an overlapping active lock, the actor stops and withdraws its candidate lock before editing business files.

## Stale and Abandoned Locks

A stale lock is not automatically abandoned. Ordinary Members may report stale locks, but they do not delete another actor's state. Lead or the human user decides whether the stale/crashed work is abandoned.

When a lock is marked abandoned, the event log should record who made the decision, why it was safe, and which scope became available.

## Relationship To Plugin Distribution

The Codex Plugin packages the two Markdown Skills. It does not add a Git helper, lock service, custom collaboration CLI, hook, or background process. Remote Git Mode remains a documented collaboration protocol executed by the participating humans and agents.
