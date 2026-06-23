from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from .errors import MULTIPLE_ROLES_SELECTED, ROLE_SESSION_CONFLICT, CollabError
from .sessions import activate, require, session_id_from
from .storage import find_project_root, local_dir, read_json, atomic_write_json, utc_now

LEAD_TOKEN = "$team-lead-collaboration"
MEMBER_TOKEN = "$team-member-collaboration"


def _payload() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"prompt": raw}


def _session_id(data: dict) -> str | None:
    for key in ("session_id", "sessionId", "thread_id", "threadId"):
        if data.get(key):
            return str(data[key])
    return os.environ.get("CODEX_SESSION_ID") or os.environ.get("CODEX_THREAD_ID")


def _prompt(data: dict) -> str:
    return str(data.get("prompt") or data.get("user_prompt") or data.get("message") or "")


def _tool_input(data: dict) -> dict:
    value = data.get("tool_input") or data.get("toolInput") or {}
    return value if isinstance(value, dict) else {}


def _inject_session_id(command: str, session_id: str) -> tuple[str, bool]:
    if "--session-id" in command or "RAC_SESSION_ID" in command:
        return command, False
    if not re.fullmatch(r"[A-Za-z0-9_.:-]+", session_id):
        return command, False
    patterns = [
        (r"(?<![\w.-])collabctl(?![\w.-])", f"collabctl --session-id {session_id}"),
        (
            r"(?<![\w.-])python\s+-m\s+remote_agent_collaboration\.cli(?![\w.-])",
            f"python -m remote_agent_collaboration.cli --session-id {session_id}",
        ),
    ]
    for pattern, replacement in patterns:
        updated, count = re.subn(pattern, replacement, command, count=1)
        if count:
            return updated, True
    return command, False


def _rewrite_tool_input_for_session(data: dict, session_id: str) -> tuple[dict | None, str]:
    tool_input = _tool_input(data)
    command = tool_input.get("command") or tool_input.get("cmd")
    if not isinstance(command, str) or "collabctl" not in command and "remote_agent_collaboration.cli" not in command:
        return None, "not_collabctl"
    updated, changed = _inject_session_id(command, session_id)
    if not changed:
        return None, "already_has_context_or_unsupported"
    rewritten = dict(tool_input)
    if "command" in rewritten:
        rewritten["command"] = updated
    else:
        rewritten["cmd"] = updated
    return rewritten, "command_rewrite"


def _record(root: Path, event: str, data: dict, result: dict) -> None:
    path = local_dir(root) / "hook-events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": utc_now(), "event": event, "data_keys": sorted(data), "result": result}, sort_keys=True) + "\n")


def user_prompt_submit() -> int:
    data = _payload()
    root = find_project_root(require=False)
    prompt = _prompt(data)
    sid = _session_id(data)
    result: dict = {"continue": True}
    try:
        has_lead = LEAD_TOKEN in prompt
        has_member = MEMBER_TOKEN in prompt
        if has_lead and has_member:
            raise CollabError(MULTIPLE_ROLES_SELECTED, "Choose exactly one collaboration role per prompt.")
        if sid and (has_lead or has_member) and (root / ".collaboration").exists():
            role = "lead" if has_lead else "member"
            skill = "team-lead-collaboration" if has_lead else "team-member-collaboration"
            actor_id = data.get("actor_id") or os.environ.get("RAC_ACTOR_ID") or "default-lead"
            activate(root, session_id=sid, role=role, skill_name=skill, actor_id=str(actor_id), source="UserPromptSubmit")
        result = {"continue": True, "session_id_available": bool(sid)}
    except CollabError as exc:
        result = {"continue": False, "error": exc.code, "message": exc.message}
    _record(root, "UserPromptSubmit", data, result)
    print(json.dumps(result))
    return 0 if result.get("continue") else 2


def pre_tool_use() -> int:
    data = _payload()
    root = find_project_root(require=False)
    sid = _session_id(data)
    result: dict
    if sid:
        rewritten, mode = _rewrite_tool_input_for_session(data, sid)
        result = {"continue": True, "session_id_available": True, "session_context_mode": mode}
        if rewritten is not None:
            result["tool_input"] = rewritten
            result["modified_tool_input"] = rewritten
    else:
        result = {"continue": True, "session_id_available": False, "warning": "SESSION_CONTEXT_MISSING"}
    _record(root, "PreToolUse", data, result)
    print(json.dumps(result))
    return 0


def subagent_start() -> int:
    data = _payload()
    root = find_project_root(require=False)
    sid = _session_id(data)
    result = {"continue": True, "session_id_available": bool(sid), "inherited": False}
    if sid and (root / ".collaboration").exists():
        try:
            lock = require(root, session_id=sid)
            result.update({"inherited": True, "role": lock.get("role")})
        except CollabError as exc:
            result.update({"warning": exc.code, "message": exc.message})
    _record(root, "SubagentStart", data, result)
    print(json.dumps(result))
    return 0


def generic(event: str) -> int:
    data = _payload()
    root = find_project_root(require=False)
    result = {"continue": True, "session_id_available": bool(_session_id(data))}
    _record(root, event, data, result)
    print(json.dumps(result))
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    event = argv[0] if argv else "unknown"
    if event == "UserPromptSubmit":
        return user_prompt_submit()
    if event == "PreToolUse":
        return pre_tool_use()
    if event == "SubagentStart":
        return subagent_start()
    return generic(event)


if __name__ == "__main__":
    raise SystemExit(main())
