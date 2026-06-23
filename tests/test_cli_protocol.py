from __future__ import annotations

import json
from pathlib import Path

from remote_agent_collaboration.cli import main


def run(args: list[str], cwd: Path, monkeypatch) -> tuple[int, dict | None]:
    monkeypatch.chdir(cwd)
    out = []
    import builtins

    real_print = builtins.print

    def capture(*values, **kwargs):
        if kwargs.get("file") is None:
            out.append(" ".join(str(v) for v in values))
        else:
            real_print(*values, **kwargs)

    monkeypatch.setattr(builtins, "print", capture)
    code = main(["--json", *args])
    payload = json.loads("\n".join(out)) if out else None
    return code, payload


def setup_project(tmp_path: Path, monkeypatch):
    code, payload = run(["init", "--project-id", "test", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload
    code, payload = run(["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload
    code, payload = run(["--session-id", "lead-thread", "session", "activate", "--role", "lead", "--skill", "team-lead-collaboration", "--actor-id", "lead"], tmp_path, monkeypatch)
    assert code == 0, payload


def test_missing_session_fails_closed(tmp_path, monkeypatch):
    setup_project(tmp_path, monkeypatch)
    code, payload = run(["member", "add", "--actor-id", "m1"], tmp_path, monkeypatch)
    assert code == 2
    assert payload["error"] == "SESSION_CONTEXT_MISSING"


def test_same_session_role_conflict(tmp_path, monkeypatch):
    setup_project(tmp_path, monkeypatch)
    code, payload = run(["member", "add", "--session-id", "lead-thread", "--actor-id", "m1", "--role", "member"], tmp_path, monkeypatch)
    assert code == 0, payload
    code, payload = run(["--session-id", "lead-thread", "session", "activate", "--role", "member", "--skill", "team-member-collaboration", "--actor-id", "m1"], tmp_path, monkeypatch)
    assert code == 2
    assert payload["error"] == "ROLE_SESSION_CONFLICT"


def test_two_threads_are_isolated(tmp_path, monkeypatch):
    setup_project(tmp_path, monkeypatch)
    assert run(["member", "add", "--session-id", "lead-thread", "--actor-id", "m1", "--role", "member", "--modules", "docs"], tmp_path, monkeypatch)[0] == 0
    assert run(["module", "add", "--session-id", "lead-thread", "--module-id", "docs", "--members", "m1", "--allowed-paths", "docs"], tmp_path, monkeypatch)[0] == 0
    code, payload = run(["--session-id", "member-thread", "session", "activate", "--role", "member", "--skill", "team-member-collaboration", "--actor-id", "m1"], tmp_path, monkeypatch)
    assert code == 0, payload
    lead_lock = json.loads((tmp_path / ".collaboration-local" / "sessions" / "lead-thread.json").read_text())
    member_lock = json.loads((tmp_path / ".collaboration-local" / "sessions" / "member-thread.json").read_text())
    assert lead_lock["role"] == "lead"
    assert member_lock["role"] == "member"


def test_member_task_and_compaction_flow(tmp_path, monkeypatch):
    setup_project(tmp_path, monkeypatch)
    assert run(["member", "add", "--session-id", "lead-thread", "--actor-id", "m1", "--role", "member", "--modules", "docs"], tmp_path, monkeypatch)[0] == 0
    assert run(["module", "add", "--session-id", "lead-thread", "--module-id", "docs", "--members", "m1", "--allowed-paths", "docs"], tmp_path, monkeypatch)[0] == 0
    assert run(["task", "create", "--session-id", "lead-thread", "--task-id", "t1", "--title", "Docs", "--module-id", "docs", "--owner", "m1"], tmp_path, monkeypatch)[0] == 0
    assert run(["--session-id", "member-thread", "session", "activate", "--role", "member", "--skill", "team-member-collaboration", "--actor-id", "m1"], tmp_path, monkeypatch)[0] == 0
    assert run(["task", "accept", "--session-id", "member-thread", "--task-id", "t1"], tmp_path, monkeypatch)[0] == 0
    assert run(["task", "start", "--session-id", "member-thread", "--task-id", "t1"], tmp_path, monkeypatch)[0] == 0
    assert run(["log", "append", "--session-id", "member-thread", "--module-id", "docs", "--summary", "Worked on docs"], tmp_path, monkeypatch)[0] == 0
    code, payload = run(["log", "compact", "--session-id", "member-thread", "--module-id", "docs"], tmp_path, monkeypatch)
    assert code == 2
    assert payload["error"] == "ROLE_NOT_AUTHORIZED"
    code, payload = run(["log", "compact", "--session-id", "lead-thread", "--module-id", "docs"], tmp_path, monkeypatch)
    assert code == 0, payload
    assert payload["manifest"]["archive_sha256"]


def test_doctor_failed_core_gate(tmp_path, monkeypatch):
    code, payload = run(["doctor"], tmp_path, monkeypatch)
    assert code == 2
    assert payload["role_lock_enforced"] is False
    assert payload["enforcement_mode"] == "failed_core_gate"
