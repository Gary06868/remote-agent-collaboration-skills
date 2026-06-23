# Source Collaboration To Generic Mapping

This document maps mechanisms from a source project into generic public protocol terms. It intentionally omits private names, private URLs, original commit identifiers, local paths, raw source text, original branch names, and internal permission details.

| Source Mechanism | Generic Implementation | Preserved | Expanded | Removed |
| --- | --- | --- | --- | --- |
| Project start checklist | Skill first-step checklist plus `collabctl git preflight` | Read current state before work | Doctor JSON and role lock validation | Source-specific onboarding text |
| Project lead role | Lead Skill and lead actor registry | Governance authority | Explicit command permissions | Private person names |
| Module contributor role | Member Skill and module authorization | Directory boundaries | Deny-by-default requests | Source workstream names |
| Shared collaboration log | Global and module append-only logs | Durable history | Lossless archive plus summary compaction | Raw historical log text |
| Major update notice | Announcements with acknowledgements | Read-before-work behavior | Severity and required actions | Source-specific status updates |
| Integration branch discipline | Configurable Git preflight | No blind overwrite | Machine-readable checks | Original branch names |
