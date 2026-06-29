# Remote Agent Collaboration Lite Rules

This project uses Remote Agent Collaboration Lite.

Each Claude thread must use exactly one collaboration role: Lead or Member. Do not switch roles inside the same thread.

Before work, read `AGENTS.md` and `COLLAB_LOG.md`. If they do not exist, ask whether a Lead thread should initialize collaboration first.

Before broad edits, check soft locks. If another actor has an overlapping writing lock, stop and ask for coordination instead of editing through it.

Use `TEAM_TASKS.md` only when Task Assignment Mode is enabled. Use `MODULE_OWNERSHIP.md` only when Module Ownership Mode is enabled. Use `.collab/` when the project chooses Remote Git Mode.

After changing work state, update the shared collaboration files with your actor identity, scope, latest status, and any handoff.

Do not claim hard locks, permission control, or automatic conflict prevention. These files are a collaboration protocol, not a security system.

Follow the user's requested conversation language. If the user requests a separate document language, use that language for the document while keeping replies in the requested conversation language.
