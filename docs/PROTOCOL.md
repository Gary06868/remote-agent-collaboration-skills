# Protocol

Initialized projects store durable collaboration state under `.collaboration/`.

- `project.json`, `policy.json`, `members.json`, `modules.json`
- `announcements/`
- `logs/global/` and `logs/modules/<module-id>/`
- `tasks/`
- `requests/`
- `handoffs/`

Local runtime data such as session locks belongs under `.collaboration-local/` and must not be committed.
