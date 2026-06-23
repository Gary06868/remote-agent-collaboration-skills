from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        backup = dst.with_name(dst.name + ".backup")
        if backup.exists():
            shutil.rmtree(backup)
        shutil.copytree(dst, backup)
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install both Remote Agent Collaboration skills.")
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--target", help="Project root for project scope. Defaults to cwd.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    if args.scope == "user":
        base = Path.home() / ".codex"
        skills_base = base / "skills"
        plugins_base = base / "plugins" / "remote-agent-collaboration"
        hooks_base = base / "hooks" / "remote-agent-collaboration"
    else:
        project = Path(args.target or Path.cwd()).resolve()
        skills_base = project / ".agents" / "skills"
        plugins_base = project / ".agents" / "plugins" / "remote-agent-collaboration"
        hooks_base = project / ".codex" / "hooks" / "remote-agent-collaboration"

    skills_base.mkdir(parents=True, exist_ok=True)
    copytree(repo / "skills" / "team-lead-collaboration", skills_base / "team-lead-collaboration")
    copytree(repo / "skills" / "team-member-collaboration", skills_base / "team-member-collaboration")
    copytree(repo / ".codex-plugin", plugins_base)
    copytree(repo / "hooks", hooks_base)

    result = {
        "installed": True,
        "scope": args.scope,
        "installed_skills": [
            str(skills_base / "team-lead-collaboration"),
            str(skills_base / "team-member-collaboration"),
        ],
        "plugin_path": str(plugins_base),
        "hooks_path": str(hooks_base),
        "next_steps": [
            "Open /hooks and review/trust Remote Agent Collaboration hooks.",
            "Start a new Codex thread.",
            "Invoke exactly one skill with $team-lead-collaboration or $team-member-collaboration.",
            "Run collabctl doctor --json.",
        ],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
