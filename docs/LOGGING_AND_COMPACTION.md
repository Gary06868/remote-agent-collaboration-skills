# Logging And Compaction

Logs are append-only JSONL. Corrections use superseding events.

Compaction archives the original ACTIVE log, records source and archive SHA-256 hashes, writes a current summary, and appends a `compaction_completed` event.
