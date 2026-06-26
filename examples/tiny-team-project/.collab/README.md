# Remote Git Mode State

This folder demonstrates the low-conflict Markdown structure for Remote Git Mode.

- `locks/`: authoritative lock state, one file per actor.
- `tasks/`: authoritative task state, one file per task.
- `events/`: append-only event files.
- `snapshots/`: derived snapshot files that Lead may rebuild.
