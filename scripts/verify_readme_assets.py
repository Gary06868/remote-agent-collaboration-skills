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
    gif = root / "docs/assets/demo.gif"
    poster = root / "docs/assets/demo-poster.png"
    if gif.stat().st_size < 100_000:
        print(f"demo.gif is too small to be the generated terminal demo: {gif.stat().st_size} bytes")
        return 1
    if not gif.read_bytes().startswith(b"GIF89a"):
        print("demo.gif is not a GIF89a file")
        return 1
    if not poster.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        print("demo-poster.png is not a PNG file")
        return 1
    print("README assets verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
