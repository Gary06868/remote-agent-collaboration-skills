# Role Session Lock

A real Codex `session_id` is required for role-controlled writes.

States:

```text
unbound -> lead_active
unbound -> member_active
lead_active -> lead_active
member_active -> member_active
lead_active -> member denied
member_active -> lead denied
closed -> no rebind
```

Missing session context returns `SESSION_CONTEXT_MISSING`.
