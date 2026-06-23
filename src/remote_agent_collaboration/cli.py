from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .errors import CollabError, ROLE_NOT_AUTHORIZED, STATE_TRANSITION_DENIED
from .sessions import activate as activate_session
from .sessions import close as close_session
from .sessions import require as require_session
from .sessions import session_id_from
from .storage import (
    SCHEMA_VERSION,
    append_jsonl,
    atomic_write_json,
    collab_dir,
    event_record,
    find_project_root,
    jsonl_events,
    local_dir,
    read_json,
    safe_rel_path,
    sha256_file,
    utc_now,
)


def emit(data: dict, json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        if data.get("ok", True):
            print(data.get("message", "OK"))
        else:
            print(f"{data.get('error')}: {data.get('message')}", file=sys.stderr)
    return 0 if data.get("ok", True) else 2


def audit(root: Path, actor_id: str, actor_role: str, event_type: str, summary: str, **extra: Any) -> None:
    append_jsonl(collab_dir(root) / "logs" / "global" / "ACTIVE.jsonl", event_record(event_type, actor_id, actor_role, summary, **extra))


def init_project(args: argparse.Namespace) -> dict:
    root = Path.cwd().resolve()
    cdir = collab_dir(root)
    if cdir.exists() and not args.yes:
        raise CollabError("PROJECT_EXISTS", "Project already initialized. Pass --yes to re-run idempotently.")
    for rel in [
        "announcements/active",
        "announcements/archive",
        "announcements/acknowledgements",
        "logs/global",
        "logs/modules",
        "logs/archive/global",
        "logs/archive/modules",
        "tasks/active",
        "tasks/review",
        "tasks/completed",
        "tasks/cancelled",
        "handoffs/pending",
        "handoffs/accepted",
        "handoffs/rejected",
        "handoffs/completed",
        "requests/pending",
        "requests/resolved",
        "requests/rejected",
        "claims",
        "reports",
        "schemas",
    ]:
        (cdir / rel).mkdir(parents=True, exist_ok=True)
    atomic_write_json(cdir / "project.json", {"schema_version": SCHEMA_VERSION, "project_id": args.project_id, "created_at_utc": utc_now()})
    atomic_write_json(cdir / "policy.json", {"schema_version": SCHEMA_VERSION, "branch_policy": "configurable", "force_push": "deny_by_default"})
    if not (cdir / "members.json").exists():
        atomic_write_json(cdir / "members.json", {"schema_version": SCHEMA_VERSION, "actors": {}})
    if not (cdir / "modules.json").exists():
        atomic_write_json(cdir / "modules.json", {"schema_version": SCHEMA_VERSION, "modules": {}})
    if not (cdir / "announcements" / "CURRENT.md").exists():
        (cdir / "announcements" / "CURRENT.md").write_text("# Current Announcements\n\nNo active announcements.\n", encoding="utf-8")
    if not (cdir / "logs" / "global" / "CURRENT_SUMMARY.md").exists():
        (cdir / "logs" / "global" / "CURRENT_SUMMARY.md").write_text("# Global Summary\n\nInitialized.\n", encoding="utf-8")
    git_dir = root / ".git"
    if git_dir.exists():
        (git_dir / "info").mkdir(parents=True, exist_ok=True)
        exclude = git_dir / "info" / "exclude"
        text = exclude.read_text(encoding="utf-8", errors="ignore") if exclude.exists() else ""
        if ".collaboration-local/" not in text:
            exclude.write_text(text + "\n.collaboration-local/\n.phase0/\n", encoding="utf-8")
    return {"ok": True, "message": "Collaboration project initialized.", "project_root": "<PROJECT_ROOT>"}


def actor_bootstrap(args: argparse.Namespace) -> dict:
    root = find_project_root()
    members_path = collab_dir(root) / "members.json"
    members = read_json(members_path, {"schema_version": SCHEMA_VERSION, "actors": {}})
    if members["actors"] and not args.yes:
        raise CollabError("BOOTSTRAP_DENIED", "Bootstrap is only for an empty actor registry.")
    members["actors"][args.actor_id] = {
        "actor_id": args.actor_id,
        "role": args.role,
        "status": "active",
        "modules": args.modules or [],
        "created_at_utc": utc_now(),
    }
    atomic_write_json(members_path, members)
    audit(root, args.actor_id, args.role, "actor_bootstrap", f"Bootstrapped {args.role} actor.")
    return {"ok": True, "message": f"Bootstrapped {args.role} actor {args.actor_id}."}


def session_activate(args: argparse.Namespace) -> dict:
    root = find_project_root()
    sid = session_id_from(args.session_id, os.environ)
    lock = activate_session(root, session_id=sid, role=args.role, skill_name=args.skill, actor_id=args.actor_id, source=args.source)
    return {"ok": True, "message": f"Session active as {args.role}.", "lock": lock}


def session_status(args: argparse.Namespace) -> dict:
    root = find_project_root()
    sid = session_id_from(args.session_id, os.environ)
    lock = require_session(root, session_id=sid)
    return {"ok": True, "message": f"Session role: {lock['role']}", "lock": lock}


def session_close_cmd(args: argparse.Namespace) -> dict:
    root = find_project_root()
    sid = session_id_from(args.session_id, os.environ)
    lock = close_session(root, session_id=sid)
    return {"ok": True, "message": "Session closed.", "lock": lock}


def command_lock(args: argparse.Namespace, roles: set[str]) -> tuple[Path, dict]:
    root = find_project_root()
    sid = session_id_from(args.session_id, os.environ)
    return root, require_session(root, session_id=sid, allowed_roles=roles)


def member_add(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead"})
    path = collab_dir(root) / "members.json"
    members = read_json(path, {"schema_version": SCHEMA_VERSION, "actors": {}})
    members["actors"][args.actor_id] = {"actor_id": args.actor_id, "role": args.role, "status": "active", "modules": args.modules or []}
    atomic_write_json(path, members)
    audit(root, lock["actor_id"], lock["role"], "member_add", f"Added actor {args.actor_id}.")
    return {"ok": True, "message": f"Added {args.actor_id}."}


def module_add(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead"})
    path = collab_dir(root) / "modules.json"
    modules = read_json(path, {"schema_version": SCHEMA_VERSION, "modules": {}})
    for rel in args.allowed_paths or []:
        safe_rel_path(root, rel)
    modules["modules"][args.module_id] = {
        "module_id": args.module_id,
        "name": args.name or args.module_id,
        "owners": args.owners or [],
        "members": args.members or [],
        "allowed_paths": args.allowed_paths or [],
        "protected_paths": args.protected_paths or [],
        "status": "active",
    }
    atomic_write_json(path, modules)
    (collab_dir(root) / "logs" / "modules" / args.module_id).mkdir(parents=True, exist_ok=True)
    audit(root, lock["actor_id"], lock["role"], "module_add", f"Added module {args.module_id}.", module_id=args.module_id)
    return {"ok": True, "message": f"Added module {args.module_id}."}


def task_path(root: Path, bucket: str, task_id: str) -> Path:
    return collab_dir(root) / "tasks" / bucket / f"{task_id}.json"


def task_create(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead"})
    task = {
        "schema_version": SCHEMA_VERSION,
        "task_id": args.task_id,
        "title": args.title,
        "description": args.description or "",
        "module_id": args.module_id,
        "owner": args.owner,
        "assigner": lock["actor_id"],
        "status": "assigned" if args.owner else "proposed",
        "priority": args.priority,
        "allowed_paths": args.allowed_paths or [],
        "forbidden_paths": args.forbidden_paths or [],
        "acceptance_criteria": args.acceptance or [],
        "required_tests": args.tests or [],
        "branch": args.branch,
        "timestamps": {"created_at_utc": utc_now()},
        "commits": [],
        "handoffs": [],
        "blockers": [],
    }
    atomic_write_json(task_path(root, "active", args.task_id), task)
    audit(root, lock["actor_id"], lock["role"], "task_create", f"Created task {args.task_id}.", module_id=args.module_id, task_id=args.task_id)
    return {"ok": True, "message": f"Created task {args.task_id}.", "task": task}


TASK_MEMBER_TRANSITIONS = {
    "accept": {"assigned": "accepted"},
    "start": {"accepted": "in_progress", "paused": "in_progress"},
    "pause": {"in_progress": "paused"},
    "resume": {"paused": "in_progress"},
    "block": {"in_progress": "blocked", "accepted": "blocked"},
    "submit": {"in_progress": "submitted_for_review", "blocked": "submitted_for_review"},
}


def task_transition(args: argparse.Namespace) -> dict:
    role = {"approve", "reject", "cancel"}
    root, lock = command_lock(args, {"lead"} if args.action in role else {"member", "lead"})
    path = task_path(root, "active", args.task_id)
    task = read_json(path)
    if not task:
        review_path = task_path(root, "review", args.task_id)
        task = read_json(review_path)
        path = review_path
    if not task:
        raise CollabError("TASK_NOT_FOUND", f"Task not found: {args.task_id}")
    old = task["status"]
    if args.action in TASK_MEMBER_TRANSITIONS:
        mapping = TASK_MEMBER_TRANSITIONS[args.action]
        if old not in mapping:
            raise CollabError(STATE_TRANSITION_DENIED, f"Cannot {args.action} from {old}.")
        if lock["role"] == "member" and task.get("owner") != lock["actor_id"]:
            raise CollabError(ROLE_NOT_AUTHORIZED, "Members can only update their own tasks.")
        task["status"] = mapping[old]
    elif args.action == "approve":
        if old != "submitted_for_review":
            raise CollabError(STATE_TRANSITION_DENIED, "Only submitted tasks can be approved.")
        task["status"] = "completed"
    elif args.action == "reject":
        if old != "submitted_for_review":
            raise CollabError(STATE_TRANSITION_DENIED, "Only submitted tasks can be rejected.")
        task["status"] = "rejected"
    elif args.action == "cancel":
        task["status"] = "cancelled"
    task.setdefault("timestamps", {})[f"{args.action}_at_utc"] = utc_now()
    if args.commit:
        task.setdefault("commits", []).append(args.commit)
    dest = path
    if task["status"] == "submitted_for_review":
        dest = task_path(root, "review", args.task_id)
    elif task["status"] == "completed":
        dest = task_path(root, "completed", args.task_id)
    elif task["status"] == "cancelled":
        dest = task_path(root, "cancelled", args.task_id)
    atomic_write_json(dest, task)
    if dest != path and path.exists():
        path.unlink()
    audit(root, lock["actor_id"], lock["role"], f"task_{args.action}", f"{args.action} task {args.task_id}.", module_id=task.get("module_id"), task_id=args.task_id)
    return {"ok": True, "message": f"Task {args.task_id} -> {task['status']}.", "task": task}


def log_append(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead", "member"})
    scope = "global" if not args.module_id else "module"
    if lock["role"] == "member" and scope == "global":
        raise CollabError(ROLE_NOT_AUTHORIZED, "Members cannot append global logs.")
    if lock["role"] == "member" and args.module_id:
        modules = read_json(collab_dir(root) / "modules.json", {"modules": {}})["modules"]
        mod = modules.get(args.module_id, {})
        if lock["actor_id"] not in mod.get("members", []) and lock["actor_id"] not in mod.get("owners", []):
            raise CollabError(ROLE_NOT_AUTHORIZED, "Member is not authorized for this module.")
    path = collab_dir(root) / "logs" / "global" / "ACTIVE.jsonl" if scope == "global" else collab_dir(root) / "logs" / "modules" / args.module_id / "ACTIVE.jsonl"
    event = event_record(args.event_type, lock["actor_id"], lock["role"], args.summary, scope=scope, module_id=args.module_id, task_id=args.task_id, commit_sha=args.commit)
    append_jsonl(path, event)
    return {"ok": True, "message": "Log appended.", "event": event}


def log_compact(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead"})
    if args.module_id:
        active = collab_dir(root) / "logs" / "modules" / args.module_id / "ACTIVE.jsonl"
        archive_dir = collab_dir(root) / "logs" / "archive" / "modules" / args.module_id
        summary = collab_dir(root) / "logs" / "modules" / args.module_id / "CURRENT_SUMMARY.md"
        scope = "module"
    else:
        active = collab_dir(root) / "logs" / "global" / "ACTIVE.jsonl"
        archive_dir = collab_dir(root) / "logs" / "archive" / "global"
        summary = collab_dir(root) / "logs" / "global" / "CURRENT_SUMMARY.md"
        scope = "global"
    active.parent.mkdir(parents=True, exist_ok=True)
    if not active.exists():
        active.write_text("", encoding="utf-8")
    source_count = len(jsonl_events(active))
    source_hash = sha256_file(active)
    compaction_id = f"compact-{utc_now().replace(':', '').replace('.', '-')}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive = archive_dir / f"{compaction_id}.jsonl"
    shutil.copyfile(active, archive)
    archive_hash = sha256_file(archive)
    summary.write_text(f"# {scope.title()} Summary\n\nCompacted {source_count} events at {utc_now()}.\n\nArchive SHA-256: `{archive_hash}`.\n", encoding="utf-8")
    completed = event_record("compaction_completed", lock["actor_id"], lock["role"], f"Compacted {scope} log.", scope=scope, module_id=args.module_id)
    active.write_text(json.dumps(completed, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "compaction_id": compaction_id,
        "scope": scope,
        "module_id": args.module_id,
        "executed_by": lock["actor_id"],
        "executed_at_utc": utc_now(),
        "source_event_count": source_count,
        "source_sha256": source_hash,
        "archive_path": str(archive.relative_to(root)),
        "archive_sha256": archive_hash,
        "retained_event_ids": [completed["event_id"]],
        "summary_path": str(summary.relative_to(root)),
        "status": "completed",
    }
    atomic_write_json(archive_dir / f"{compaction_id}.manifest.json", manifest)
    return {"ok": True, "message": "Log compacted.", "manifest": manifest}


def announce_publish(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead"})
    ann = {
        "announcement_id": args.announcement_id,
        "title": args.title,
        "severity": args.severity,
        "issued_by": lock["actor_id"],
        "issued_at_utc": utc_now(),
        "effective_at_utc": args.effective_at or utc_now(),
        "affected_modules": args.affected_modules or [],
        "summary": args.summary,
        "required_actions": args.required_actions or [],
        "supersedes": args.supersedes,
        "expires_at": args.expires_at,
        "acknowledgement_required": args.acknowledgement_required,
    }
    path = collab_dir(root) / "announcements" / "active" / f"{args.announcement_id}.json"
    atomic_write_json(path, ann)
    (collab_dir(root) / "announcements" / "CURRENT.md").write_text(f"# Current Announcement\n\n## {args.title}\n\n{args.summary}\n", encoding="utf-8")
    audit(root, lock["actor_id"], lock["role"], "announcement_publish", f"Published announcement {args.announcement_id}.")
    return {"ok": True, "message": f"Published announcement {args.announcement_id}.", "announcement": ann}


def announce_ack(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead", "member"})
    ack = {"announcement_id": args.announcement_id, "actor_id": lock["actor_id"], "acknowledged_at_utc": utc_now()}
    atomic_write_json(collab_dir(root) / "announcements" / "acknowledgements" / f"{args.announcement_id}.{lock['actor_id']}.json", ack)
    return {"ok": True, "message": f"Acknowledged {args.announcement_id}.", "acknowledgement": ack}


def request_create(args: argparse.Namespace) -> dict:
    root, lock = command_lock(args, {"lead", "member"})
    req = {"request_id": args.request_id, "type": args.type, "created_by": lock["actor_id"], "status": "pending", "summary": args.summary, "created_at_utc": utc_now()}
    atomic_write_json(collab_dir(root) / "requests" / "pending" / f"{args.request_id}.json", req)
    audit(root, lock["actor_id"], lock["role"], "request_create", f"Created request {args.request_id}.")
    return {"ok": True, "message": f"Created request {args.request_id}.", "request": req}


def git_preflight(args: argparse.Namespace) -> dict:
    root = find_project_root(require=False)
    checks: dict[str, Any] = {"is_git_repo": (root / ".git").exists()}
    commands = [
        ["git", "status", "--short", "--branch"],
        ["git", "branch", "-vv"],
    ]
    for cmd in commands:
        try:
            result = subprocess.run(cmd, cwd=root, check=False, text=True, capture_output=True)
            checks[" ".join(cmd)] = {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        except FileNotFoundError:
            checks["git_available"] = False
    return {"ok": True, "message": "Git preflight completed.", "checks": checks}


def doctor(args: argparse.Namespace) -> dict:
    root = find_project_root(require=False)
    phase0 = read_json(local_dir(root) / "phase0_result.json", {})
    hooks_installed = (root / "hooks" / "hooks.json").exists() or (root / ".codex" / "hooks.json").exists()
    role_lock = bool(phase0.get("role_lock_enforced"))
    blocking = []
    if not role_lock:
        blocking.append("FAILED_CORE_GATE: real Codex thread hooks were not observed running in this environment.")
    result = {
        "ok": role_lock,
        "healthy": role_lock,
        "version": __version__,
        "hooks_installed": hooks_installed,
        "hooks_trusted_or_observed_running": bool(phase0.get("hooks_trusted_or_observed_running")),
        "session_id_available": bool(phase0.get("session_id_available")),
        "user_prompt_hook_operational": bool(phase0.get("user_prompt_hook_operational")),
        "pre_tool_hook_operational": bool(phase0.get("pre_tool_hook_operational")),
        "subagent_hook_operational": bool(phase0.get("subagent_hook_operational")),
        "role_lock_enforced": role_lock,
        "enforcement_mode": phase0.get("enforcement_mode", "failed_core_gate"),
        "blocking_reasons": blocking,
        "message": "Doctor completed." if role_lock else "Doctor failed: role lock is not enforced.",
    }
    return result


PRIVATE_SUBSTRINGS = [
    "D:" + "\\\\" + "System" + "File",
    "C:" + "\\\\" + "Users" + "\\\\" + "Liangyu" + " " + "Gong",
    "Meta" + "Agent",
    "Meta" + "Planner",
    "version" + "/" + "v1",
    "workstream" + "/" + "skills",
    "workstream" + "/" + "frontend",
]
PRIVATE_NAME_REGEXES = [re.compile(r"\b" + name + r"\b") for name in ["Ga" + "ry", "Et" + "han", "Ben" + "nie", "Har" + "ry"]]


def privacy_scan(args: argparse.Namespace) -> dict:
    root = Path.cwd().resolve()
    include = {".md", ".json", ".yaml", ".yml", ".py", ".ps1", ".sh", ".svg", ".tape", ".toml"}
    findings = []
    for path in root.rglob("*"):
        if any(part in {".git", ".venv", "__pycache__", ".pytest_cache", ".collaboration-local", ".phase0"} for part in path.parts):
            continue
        if path.is_dir() or path.suffix.lower() not in include:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pat in PRIVATE_SUBSTRINGS:
            if pat in text:
                findings.append({"path": str(path.relative_to(root)), "pattern": pat})
        for regex in PRIVATE_NAME_REGEXES:
            if regex.search(text):
                findings.append({"path": str(path.relative_to(root)), "pattern": regex.pattern})
    return {"ok": not findings, "message": "Privacy scan passed." if not findings else "Privacy scan failed.", "findings": findings}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="collabctl")
    p.add_argument("--json", action="store_true")
    p.add_argument("--session-id")
    sub = p.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init")
    init.add_argument("--project-id", default="remote-agent-collaboration-demo")
    init.add_argument("--yes", action="store_true")
    init.set_defaults(func=init_project)

    actor = sub.add_parser("actor")
    actor_sub = actor.add_subparsers(dest="actor_cmd", required=True)
    boot = actor_sub.add_parser("bootstrap")
    boot.add_argument("--actor-id", required=True)
    boot.add_argument("--role", choices=["lead", "member"], required=True)
    boot.add_argument("--modules", nargs="*")
    boot.add_argument("--yes", action="store_true")
    boot.set_defaults(func=actor_bootstrap)

    session = sub.add_parser("session")
    ss = session.add_subparsers(dest="session_cmd", required=True)
    act = ss.add_parser("activate")
    act.add_argument("--role", choices=["lead", "member"], required=True)
    act.add_argument("--skill", required=True)
    act.add_argument("--actor-id", required=True)
    act.add_argument("--source", default="cli")
    act.set_defaults(func=session_activate)
    ss.add_parser("status").set_defaults(func=session_status)
    ss.add_parser("close").set_defaults(func=session_close_cmd)

    member = sub.add_parser("member")
    ms = member.add_subparsers(dest="member_cmd", required=True)
    ma = ms.add_parser("add")
    ma.add_argument("--actor-id", required=True)
    ma.add_argument("--role", choices=["lead", "member"], default="member")
    ma.add_argument("--modules", nargs="*")
    ma.set_defaults(func=member_add)

    module = sub.add_parser("module")
    mods = module.add_subparsers(dest="module_cmd", required=True)
    madd = mods.add_parser("add")
    madd.add_argument("--module-id", required=True)
    madd.add_argument("--name")
    madd.add_argument("--owners", nargs="*")
    madd.add_argument("--members", nargs="*")
    madd.add_argument("--allowed-paths", nargs="*")
    madd.add_argument("--protected-paths", nargs="*")
    madd.set_defaults(func=module_add)

    task = sub.add_parser("task")
    ts = task.add_subparsers(dest="task_cmd", required=True)
    tc = ts.add_parser("create")
    tc.add_argument("--task-id", required=True)
    tc.add_argument("--title", required=True)
    tc.add_argument("--description")
    tc.add_argument("--module-id", required=True)
    tc.add_argument("--owner")
    tc.add_argument("--priority", default="normal")
    tc.add_argument("--allowed-paths", nargs="*")
    tc.add_argument("--forbidden-paths", nargs="*")
    tc.add_argument("--acceptance", nargs="*")
    tc.add_argument("--tests", nargs="*")
    tc.add_argument("--branch")
    tc.set_defaults(func=task_create)
    for action in ["accept", "start", "pause", "resume", "block", "submit", "approve", "reject", "cancel"]:
        tp = ts.add_parser(action)
        tp.add_argument("--task-id", required=True)
        tp.add_argument("--commit")
        tp.set_defaults(func=task_transition, action=action)

    log = sub.add_parser("log")
    ls = log.add_subparsers(dest="log_cmd", required=True)
    la = ls.add_parser("append")
    la.add_argument("--module-id")
    la.add_argument("--task-id")
    la.add_argument("--event-type", default="progress")
    la.add_argument("--summary", required=True)
    la.add_argument("--commit")
    la.set_defaults(func=log_append)
    lc = ls.add_parser("compact")
    lc.add_argument("--module-id")
    lc.set_defaults(func=log_compact)

    ann = sub.add_parser("announce")
    ans = ann.add_subparsers(dest="announce_cmd", required=True)
    ap = ans.add_parser("publish")
    ap.add_argument("--announcement-id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--severity", choices=["info", "important", "critical"], default="important")
    ap.add_argument("--summary", required=True)
    ap.add_argument("--effective-at")
    ap.add_argument("--affected-modules", nargs="*")
    ap.add_argument("--required-actions", nargs="*")
    ap.add_argument("--supersedes")
    ap.add_argument("--expires-at")
    ap.add_argument("--acknowledgement-required", action="store_true")
    ap.set_defaults(func=announce_publish)
    aa = ans.add_parser("acknowledge")
    aa.add_argument("--announcement-id", required=True)
    aa.set_defaults(func=announce_ack)

    req = sub.add_parser("request")
    rs = req.add_subparsers(dest="request_cmd", required=True)
    rc = rs.add_parser("create")
    rc.add_argument("--request-id", required=True)
    rc.add_argument("--type", required=True)
    rc.add_argument("--summary", required=True)
    rc.set_defaults(func=request_create)

    gp = sub.add_parser("git")
    gs = gp.add_subparsers(dest="git_cmd", required=True)
    gs.add_parser("preflight").set_defaults(func=git_preflight)

    sub.add_parser("doctor").set_defaults(func=doctor)
    sub.add_parser("privacy-scan").set_defaults(func=privacy_scan)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argv = list(argv or sys.argv[1:])
    lifted: list[str] = []
    rest: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == "--session-id" and i + 1 < len(argv):
            lifted.extend([argv[i], argv[i + 1]])
            i += 2
        elif argv[i] == "--json":
            lifted.append(argv[i])
            i += 1
        else:
            rest.append(argv[i])
            i += 1
    args = parser.parse_args([*lifted, *rest])
    try:
        return emit(args.func(args), args.json)
    except CollabError as exc:
        return emit(exc.to_dict(), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
