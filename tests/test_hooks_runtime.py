from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path

from remote_agent_collaboration.cli import main as cli_main
from remote_agent_collaboration.hooks_runtime import main


def run_cli(args: list[str], capsys) -> tuple[int, dict]:
    code = cli_main(["--json", *args])
    out = capsys.readouterr().out
    return code, json.loads(out)


def run_hook(event: str, payload: dict, monkeypatch, capsys) -> tuple[int, dict]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    code = main([event])
    out = capsys.readouterr().out
    return code, json.loads(out)


def test_user_prompt_blocks_multiple_roles(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    code, payload = run_hook(
        "UserPromptSubmit",
        {"session_id": "thread-1", "prompt": "$team-lead-collaboration and $team-member-collaboration"},
        monkeypatch,
        capsys,
    )
    assert code == 2
    assert payload["error"] == "MULTIPLE_ROLES_SELECTED"


def test_pre_tool_use_rewrites_collabctl_command_with_session_id(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    code, payload = run_hook(
        "PreToolUse",
        {"session_id": "thread-1", "tool_input": {"command": "collabctl member add --actor-id m1 --role member"}},
        monkeypatch,
        capsys,
    )
    assert code == 0
    assert payload["session_context_mode"] == "command_rewrite"
    assert payload["tool_input"]["command"] == "collabctl --session-id thread-1 member add --actor-id m1 --role member"
    assert payload["modified_tool_input"] == payload["tool_input"]


def test_user_prompt_submit_writes_observed_session_lock(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert run_cli(["init", "--project-id", "hooks", "--yes"], capsys)[0] == 0
    assert run_cli(["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"], capsys)[0] == 0

    code, payload = run_hook(
        "UserPromptSubmit",
        {"session_id": "thread-1", "prompt": "$team-lead-collaboration", "actor_id": "lead"},
        monkeypatch,
        capsys,
    )

    assert code == 0, payload
    assert payload["session_id_available"] is True
    lock = json.loads((tmp_path / ".collaboration-local" / "session-locks" / "thread-1.json").read_text())
    assert lock["session_id"] == "thread-1"
    assert lock["role"] == "lead"
    assert lock["actor_id"] == "lead"
    assert lock["skill_name"] == "team-lead-collaboration"
    assert lock["fallback"] is False
    assert "UserPromptSubmit" in lock["observed_events"]


def test_pre_tool_use_writes_observed_session_lock_for_cli_call(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert run_cli(["init", "--project-id", "hooks", "--yes"], capsys)[0] == 0
    assert run_cli(["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"], capsys)[0] == 0
    assert run_cli(
        [
            "session",
            "activate",
            "--session-id",
            "thread-1",
            "--role",
            "lead",
            "--skill",
            "team-lead-collaboration",
            "--actor-id",
            "lead",
        ],
        capsys,
    )[0] == 0

    code, payload = run_hook(
        "PreToolUse",
        {"session_id": "thread-1", "tool_input": {"command": "collabctl member add --actor-id m1 --role member"}},
        monkeypatch,
        capsys,
    )

    assert code == 0, payload
    lock = json.loads((tmp_path / ".collaboration-local" / "session-locks" / "thread-1.json").read_text())
    assert lock["session_id"] == "thread-1"
    assert lock["role"] == "lead"
    assert lock["actor_id"] == "lead"
    assert lock["skill_name"] == "team-lead-collaboration"
    assert lock["fallback"] is False
    assert "PreToolUse" in lock["observed_events"]


def test_subagent_start_inherits_parent_session_lock(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert run_cli(["init", "--project-id", "hooks", "--yes"], capsys)[0] == 0
    assert run_cli(["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"], capsys)[0] == 0
    assert run_cli(
        [
            "session",
            "activate",
            "--session-id",
            "thread-1",
            "--role",
            "lead",
            "--skill",
            "team-lead-collaboration",
            "--actor-id",
            "lead",
        ],
        capsys,
    )[0] == 0

    code, payload = run_hook(
        "SubagentStart",
        {"session_id": "thread-1", "prompt": "inspect docs"},
        monkeypatch,
        capsys,
    )

    assert code == 0, payload
    assert payload["inherited"] is True
    assert payload["role"] == "lead"
    assert payload["session_context"]["COLLAB_SESSION_ID"] == "thread-1"
    lock = json.loads((tmp_path / ".collaboration-local" / "session-locks" / "thread-1.json").read_text())
    assert lock["subagent"] is True
    assert "SubagentStart" in lock["observed_events"]


def test_pre_tool_use_does_not_duplicate_session_id(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    command = "collabctl --session-id existing member add --actor-id m1 --role member"
    code, payload = run_hook(
        "PreToolUse",
        {"session_id": "thread-1", "tool_input": {"command": command}},
        monkeypatch,
        capsys,
    )
    assert code == 0
    assert payload["session_context_mode"] == "already_has_context_or_unsupported"
    assert "tool_input" not in payload


def test_hook_script_bootstraps_src_without_pythonpath(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(repo / "hooks" / "user_prompt_submit.py")],
        cwd=tmp_path,
        input=json.dumps({"prompt": "hello"}),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["continue"] is True
