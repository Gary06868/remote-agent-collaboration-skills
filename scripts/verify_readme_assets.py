from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    readme = (root / "README.md").read_text(encoding="utf-8")
    refs = re.findall(r"docs/assets/[^\s)\"']+", readme)
    missing = [ref for ref in refs if not (root / ref).exists()]
    required = [
        "docs/assets/hero.svg",
        "docs/assets/architecture.svg",
        "docs/assets/role-lock-flow.svg",
        "docs/assets/demo.gif",
        "docs/assets/demo-poster.png",
    ]
    missing.extend(ref for ref in required if not (root / ref).exists())
    if missing:
        print("Missing assets:")
        for item in sorted(set(missing)):
            print(f"- {item}")
        return 1
    print("README assets verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
