from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import CollabError, PROJECT_NOT_INITIALIZED, PATH_NOT_AUTHORIZED

SCHEMA_VERSION = "0.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def cwd_root(start: Path | None = None) -> Path:
    return (start or Path.cwd()).resolve()


def find_project_root(start: Path | None = None, *, require: bool = True) -> Path:
    cur = cwd_root(start)
    for path in (cur, *cur.parents):
        if (path / ".collaboration" / "project.json").exists():
            return path
    if require:
        raise CollabError(PROJECT_NOT_INITIALIZED, "No .collaboration/project.json found.")
    return cur


def collab_dir(root: Path) -> Path:
    return root / ".collaboration"


def local_dir(root: Path) -> Path:
    path = root / ".collaboration-local"
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_rel_path(root: Path, value: str | Path) -> Path:
    candidate = (root / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise CollabError(PATH_NOT_AUTHORIZED, f"Path escapes project root: {value}") from exc
    return candidate


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_json(path: Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jsonl_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def event_record(event_type: str, actor_id: str, actor_role: str, summary: str, **extra: Any) -> dict:
    base = {
        "schema_version": SCHEMA_VERSION,
        "event_id": extra.pop("event_id", hashlib.sha256(f"{event_type}:{actor_id}:{utc_now()}".encode()).hexdigest()[:16]),
        "timestamp_utc": utc_now(),
        "actor_id": actor_id,
        "actor_type": "agent",
        "actor_role": actor_role,
        "event_type": event_type,
        "scope": extra.pop("scope", "global"),
        "module_id": extra.pop("module_id", None),
        "task_id": extra.pop("task_id", None),
        "summary": summary,
        "details": extra.pop("details", {}),
        "references": extra.pop("references", []),
        "commit_sha": extra.pop("commit_sha", None),
        "supersedes_event_id": extra.pop("supersedes_event_id", None),
    }
    base.update(extra)
    return base
