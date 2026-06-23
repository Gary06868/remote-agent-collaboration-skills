from __future__ import annotations

import base64
from pathlib import Path


TRANSCRIPT = """$ collabctl init --project-id demo --yes
Collaboration project initialized.
$ collabctl actor bootstrap --actor-id lead --role lead --yes
Bootstrapped lead actor lead.
$ collabctl session activate --session-id thread-lead --role lead --skill team-lead-collaboration --actor-id lead
Session active as lead.
$ collabctl session activate --session-id thread-lead --role member --skill team-member-collaboration --actor-id member
ROLE_SESSION_CONFLICT: Session is already bound to lead.
$ collabctl member add --session-id thread-lead --actor-id member --role member --modules docs
Added member.
$ collabctl session activate --session-id thread-member --role member --skill team-member-collaboration --actor-id member
Session active as member.
$ collabctl announce publish --session-id thread-lead --announcement-id ann-1 --title "Release plan" --summary "Read before work" --acknowledgement-required
Published announcement ann-1.
$ collabctl announce acknowledge --session-id thread-member --announcement-id ann-1
Acknowledged ann-1.
$ collabctl task start --session-id thread-member --task-id task-1
Task task-1 -> in_progress.
$ collabctl request create --session-id thread-member --request-id req-compact --type log_compaction --summary "Please compact logs"
Created request req-compact.
$ collabctl log compact --session-id thread-lead
Archive and SHA-256 verified.
"""


def svg(content: str) -> str:
    lines = content.splitlines()
    height = 40 + len(lines) * 22
    text = "\n".join(
        f'<text x="24" y="{38 + i * 22}" fill="#d1fae5" font-size="14" font-family="Consolas, monospace">{line.replace("&", "&amp;").replace("<", "&lt;")}</text>'
        for i, line in enumerate(lines)
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}"><rect width="960" height="{height}" fill="#0f172a"/>{text}</svg>\n'


def main() -> int:
    root = Path.cwd()
    assets = root / "docs" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (root / "demo").mkdir(exist_ok=True)
    (root / "demo" / "demo-transcript.txt").write_text(TRANSCRIPT, encoding="utf-8")
    poster = svg(TRANSCRIPT)
    (assets / "demo-poster.svg").write_text(poster, encoding="utf-8")
    # Tiny valid 1x1 transparent GIF fallback. The transcript source is the reproducible artifact.
    gif = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==")
    (assets / "demo.gif").write_bytes(gif)
    (assets / "demo-poster.png").write_bytes(gif)
    print("Generated demo transcript, poster fallback, and compact GIF.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
