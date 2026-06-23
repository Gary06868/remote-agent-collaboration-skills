# Contributing

Use explicit Git staging and keep role protocol changes covered by tests.

Before opening a pull request:

```bash
python -m pytest
python scripts/generate_demo.py
python scripts/verify_readme_assets.py
collabctl privacy-scan --json
```

Do not commit local `.collaboration-local/`, `.phase0/`, secrets, private paths, or raw source-project documents.
