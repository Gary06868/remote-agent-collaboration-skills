from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def remove(path: Path) -> bool:
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Uninstall Remote Agent Collaboration plugin and skills.")
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--target", help="Project root for project scope. Defaults to cwd.")
    args = parser.parse_args()
    if args.scope == "user":
        base = Path.home() / ".codex"
        paths = [
            base / "skills" / "team-lead-collaboration",
            base / "skills" / "team-member-collaboration",
            base / "plugins" / "remote-agent-collaboration",
            base / "hooks" / "remote-agent-collaboration",
        ]
    else:
        project = Path(args.target or Path.cwd()).resolve()
        paths = [
            project / ".agents" / "skills" / "team-lead-collaboration",
            project / ".agents" / "skills" / "team-member-collaboration",
            project / ".agents" / "plugins" / "remote-agent-collaboration",
            project / ".codex" / "hooks" / "remote-agent-collaboration",
        ]
    removed = [str(p) for p in paths if remove(p)]
    print(json.dumps({"removed": removed, "collaboration_data_preserved": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
