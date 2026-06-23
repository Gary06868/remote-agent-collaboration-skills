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


def session_context_from(args_session_id: str | None = None, env: dict | None = None) -> dict:
    env = env or {}
    candidates = [
        ("--session-id", args_session_id),
        ("COLLAB_SESSION_ID", env.get("COLLAB_SESSION_ID")),
        ("RAC_SESSION_ID", env.get("RAC_SESSION_ID")),
        ("CODEX_SESSION_ID", env.get("CODEX_SESSION_ID")),
        ("CODEX_THREAD_ID", env.get("CODEX_THREAD_ID")),
    ]
    source = None
    value = None
    for candidate_source, candidate_value in candidates:
        if candidate_value:
            source = candidate_source
            value = str(candidate_value)
            break
    if not value:
        raise CollabError(SESSION_CONTEXT_MISSING, "A real Codex session_id is required for this write operation.")
    return {"session_id": value, "source": source, "fallback": True}


def session_id_from(args_session_id: str | None = None, env: dict | None = None) -> str:
    return str(session_context_from(args_session_id, env)["session_id"])


def safe_session_name(session_id: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in session_id)


def session_path(root: Path, session_id: str) -> Path:
    return local_dir(root) / "sessions" / f"{safe_session_name(session_id)}.json"


def observed_session_lock_path(root: Path, session_id: str) -> Path:
    return local_dir(root) / "session-locks" / f"{safe_session_name(session_id)}.json"


def read_observed_session_lock(root: Path, session_id: str) -> dict:
    return read_json(observed_session_lock_path(root, session_id), {})


def list_observed_session_locks(root: Path) -> list[dict]:
    directory = local_dir(root) / "session-locks"
    if not directory.exists():
        return []
    locks = []
    for path in sorted(directory.glob("*.json")):
        data = read_json(path, {})
        if isinstance(data, dict) and data:
            locks.append(data)
    return locks


def write_observed_session_lock(
    root: Path,
    *,
    session_id: str,
    role: str,
    actor_id: str,
    skill_name: str,
    source_event: str,
    fallback: bool = False,
    parent_session_id: str | None = None,
    subagent: bool = False,
) -> dict:
    path = observed_session_lock_path(root, session_id)
    existing = read_json(path, {})
    now = utc_now()
    observed_events = set(existing.get("observed_events", []))
    observed_events.add(source_event)
    lock = {
        **existing,
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "project_id": read_json(root / ".collaboration" / "project.json", {}).get("project_id"),
        "project_root": "<PROJECT_ROOT>",
        "worktree_id": root.name,
        "actor_id": actor_id,
        "role": role,
        "skill_name": skill_name,
        "fallback": bool(fallback),
        "source_event": source_event,
        "observed_events": sorted(observed_events),
        "last_seen_at_utc": now,
    }
    lock.setdefault("created_at_utc", now)
    if parent_session_id:
        lock["parent_session_id"] = parent_session_id
    if subagent:
        lock["subagent"] = True
    atomic_write_json(path, lock)
    return lock


def load_members(root: Path) -> dict:
    return read_json(root / ".collaboration" / "members.json", {"actors": {}})


def actor_role(root: Path, actor_id: str) -> str:
    actor = load_members(root).get("actors", {}).get(actor_id)
    if not actor:
        raise CollabError(ACTOR_NOT_REGISTERED, f"Actor is not registered: {actor_id}")
    return actor.get("role", "")


def activate(
    root: Path,
    *,
    session_id: str,
    role: str,
    skill_name: str,
    actor_id: str,
    source: str = "skill",
    fallback: bool = False,
    session_id_source: str | None = None,
) -> dict:
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
        if "fallback" not in existing or not fallback:
            existing["fallback"] = bool(fallback)
        existing["session_id_source"] = session_id_source or existing.get("session_id_source") or source
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
        "fallback": bool(fallback),
        "session_id_source": session_id_source or source,
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
