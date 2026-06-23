from __future__ import annotations

from pathlib import Path

from .errors import (
    ACTOR_NOT_REGISTERED,
    CollabError,
    ROLE_NOT_AUTHORIZED,
    ROLE_SESSION_CONFLICT,
    SESSION_ALREADY_CLOSED,
    SESSION_CONTEXT_MISSING,
)
from .storage import SCHEMA_VERSION, atomic_write_json, local_dir, read_json, utc_now

ROLES = {"lead", "member"}


def session_id_from(args_session_id: str | None = None, env: dict | None = None) -> str:
    env = env or {}
    value = args_session_id or env.get("RAC_SESSION_ID") or env.get("CODEX_SESSION_ID") or env.get("CODEX_THREAD_ID")
    if not value:
        raise CollabError(SESSION_CONTEXT_MISSING, "A real Codex session_id is required for this write operation.")
    return value


def session_path(root: Path, session_id: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in session_id)
    return local_dir(root) / "sessions" / f"{safe}.json"


def load_members(root: Path) -> dict:
    return read_json(root / ".collaboration" / "members.json", {"actors": {}})


def actor_role(root: Path, actor_id: str) -> str:
    actor = load_members(root).get("actors", {}).get(actor_id)
    if not actor:
        raise CollabError(ACTOR_NOT_REGISTERED, f"Actor is not registered: {actor_id}")
    return actor.get("role", "")


def activate(root: Path, *, session_id: str, role: str, skill_name: str, actor_id: str, source: str = "skill") -> dict:
    if role not in ROLES:
        raise CollabError(ROLE_NOT_AUTHORIZED, f"Unknown role: {role}")
    registered_role = actor_role(root, actor_id)
    if registered_role != role:
        raise CollabError(ROLE_NOT_AUTHORIZED, f"Actor {actor_id} is registered as {registered_role}, not {role}.")
    path = session_path(root, session_id)
    existing = read_json(path)
    now = utc_now()
    if existing:
        if existing.get("closed_at_utc"):
            raise CollabError(SESSION_ALREADY_CLOSED, "This session was closed and cannot bind a new role.")
        if existing.get("role") != role:
            raise CollabError(ROLE_SESSION_CONFLICT, f"Session is already bound to {existing.get('role')}.")
        existing["last_seen_at_utc"] = now
        existing["lock_version"] = int(existing.get("lock_version", 1)) + 1
        atomic_write_json(path, existing)
        return existing
    lock = {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "project_id": read_json(root / ".collaboration" / "project.json", {}).get("project_id"),
        "project_root": "<PROJECT_ROOT>",
        "worktree_id": root.name,
        "actor_id": actor_id,
        "role": role,
        "skill_name": skill_name,
        "activated_at_utc": now,
        "last_seen_at_utc": now,
        "closed_at_utc": None,
        "source": source,
        "lock_version": 1,
    }
    atomic_write_json(path, lock)
    return lock


def require(root: Path, *, session_id: str, allowed_roles: set[str] | None = None) -> dict:
    lock = read_json(session_path(root, session_id))
    if not lock:
        raise CollabError(SESSION_CONTEXT_MISSING, "No role lock exists for this session_id.")
    if lock.get("closed_at_utc"):
        raise CollabError(SESSION_ALREADY_CLOSED, "This session is closed.")
    if allowed_roles and lock.get("role") not in allowed_roles:
        raise CollabError(ROLE_NOT_AUTHORIZED, f"Role {lock.get('role')} cannot perform this operation.")
    lock["last_seen_at_utc"] = utc_now()
    atomic_write_json(session_path(root, session_id), lock)
    return lock


def close(root: Path, *, session_id: str) -> dict:
    lock = require(root, session_id=session_id)
    lock["closed_at_utc"] = utc_now()
    lock["lock_version"] = int(lock.get("lock_version", 1)) + 1
    atomic_write_json(session_path(root, session_id), lock)
    return lock
