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


def test_handoff_flow_between_members(tmp_path, monkeypatch):
    setup_project(tmp_path, monkeypatch)
    assert run(["member", "add", "--session-id", "lead-thread", "--actor-id", "m1", "--role", "member", "--modules", "docs"], tmp_path, monkeypatch)[0] == 0
    assert run(["member", "add", "--session-id", "lead-thread", "--actor-id", "m2", "--role", "member", "--modules", "docs"], tmp_path, monkeypatch)[0] == 0
    assert run(["module", "add", "--session-id", "lead-thread", "--module-id", "docs", "--members", "m1", "m2", "--allowed-paths", "docs"], tmp_path, monkeypatch)[0] == 0
    assert run(["task", "create", "--session-id", "lead-thread", "--task-id", "t1", "--title", "Docs", "--module-id", "docs", "--owner", "m1"], tmp_path, monkeypatch)[0] == 0
    assert run(["--session-id", "m1-thread", "session", "activate", "--role", "member", "--skill", "team-member-collaboration", "--actor-id", "m1"], tmp_path, monkeypatch)[0] == 0
    assert run(["--session-id", "m2-thread", "session", "activate", "--role", "member", "--skill", "team-member-collaboration", "--actor-id", "m2"], tmp_path, monkeypatch)[0] == 0
    assert run([
        "handoff",
        "create",
        "--session-id",
        "m1-thread",
        "--handoff-id",
        "h1",
        "--task-id",
        "t1",
        "--module-id",
        "docs",
        "--from-actor",
        "m1",
        "--to-actor",
        "m2",
        "--summary",
        "Transfer docs task",
    ], tmp_path, monkeypatch)[0] == 0
    code, payload = run(["handoff", "accept", "--session-id", "m2-thread", "--handoff-id", "h1"], tmp_path, monkeypatch)
    assert code == 0, payload
    assert payload["handoff"]["status"] == "accepted"
    code, payload = run(["handoff", "complete", "--session-id", "m1-thread", "--handoff-id", "h1", "--note", "Context transferred"], tmp_path, monkeypatch)
    assert code == 0, payload
    assert payload["handoff"]["status"] == "completed"


def test_doctor_failed_core_gate(tmp_path, monkeypatch):
    code, payload = run(["doctor"], tmp_path, monkeypatch)
    assert code == 2
    assert payload["role_lock_enforced"] is False
    assert payload["enforcement_mode"] == "failed_core_gate"


def test_phase0_smoke_fallback_session_id_does_not_enforce_role_lock(tmp_path, monkeypatch):
    code, payload = run(["init", "--project-id", "phase0", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload
    code, payload = run(["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload

    code, payload = run(
        [
            "session",
            "activate",
            "--session-id",
            "test-thread",
            "--role",
            "lead",
            "--skill",
            "team-lead-collaboration",
            "--actor-id",
            "lead",
        ],
        tmp_path,
        monkeypatch,
    )
    assert code == 0, payload
    assert payload["lock"]["session_id"] == "test-thread"
    assert payload["lock"]["fallback"] is True

    code, payload = run(["doctor"], tmp_path, monkeypatch)
    assert code == 2
    assert payload["role_lock_enforced"] is False
    assert payload["fallback_mode"] is True
    assert "FALLBACK_SESSION_ONLY" in payload["blocking_reasons"]


def test_phase0_smoke_observed_hook_session_lock_enforces_role_lock(tmp_path, monkeypatch):
    code, payload = run(["init", "--project-id", "phase0", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload
    code, payload = run(["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload
    code, payload = run(
        [
            "session",
            "activate",
            "--session-id",
            "test-thread",
            "--role",
            "lead",
            "--skill",
            "team-lead-collaboration",
            "--actor-id",
            "lead",
        ],
        tmp_path,
        monkeypatch,
    )
    assert code == 0, payload

    lock_dir = tmp_path / ".collaboration-local" / "session-locks"
    lock_dir.mkdir(parents=True)
    (lock_dir / "test-thread.json").write_text(
        json.dumps(
            {
                "session_id": "test-thread",
                "role": "lead",
                "actor_id": "lead",
                "skill_name": "team-lead-collaboration",
                "fallback": False,
                "source_event": "PreToolUse",
                "observed_events": ["UserPromptSubmit", "PreToolUse"],
                "last_seen_at_utc": "2026-06-23T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    code, payload = run(["doctor"], tmp_path, monkeypatch)
    assert code == 0
    assert payload["role_lock_enforced"] is True
    assert payload["enforcement_mode"] == "hook_observed_session_lock"
    assert payload["hooks_trusted_or_observed_running"] is True
    assert payload["session_id_available"] is True
    assert payload["user_prompt_hook_operational"] is True
    assert payload["pre_tool_hook_operational"] is True


def test_session_activate_can_use_collab_session_id_env_as_fallback(tmp_path, monkeypatch):
    code, payload = run(["init", "--project-id", "phase0", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload
    code, payload = run(["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"], tmp_path, monkeypatch)
    assert code == 0, payload
    monkeypatch.setenv("COLLAB_SESSION_ID", "env-thread")

    code, payload = run(
        ["session", "activate", "--role", "lead", "--skill", "team-lead-collaboration", "--actor-id", "lead"],
        tmp_path,
        monkeypatch,
    )

    assert code == 0, payload
    assert payload["lock"]["session_id"] == "env-thread"
    assert payload["lock"]["fallback"] is True
    assert payload["lock"]["session_id_source"] == "COLLAB_SESSION_ID"
