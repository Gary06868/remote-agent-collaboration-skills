# Contributing

This repository's `main` branch is intentionally lightweight.

Keep `main` focused on:

- Markdown Skills.
- Project collaboration templates.
- Small examples that can be understood quickly.
- Clear documentation for soft coordination workflows.

Avoid adding infrastructure to `main` unless the product direction changes.

Before opening a pull request:

1. Check the current branch.
2. Run `git status --short --branch`.
3. Review changed Markdown files for stale links.
4. Confirm the first screen of `README.md` still describes the Lite product.
5. Explicitly stage only files related to your change.

Do not commit secrets, caches, temporary files, dependency folders, virtualenvs, or local runtime data.

Advanced local protocol experiments are preserved on the `standard-local-protocol` branch.
