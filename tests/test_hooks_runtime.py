from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path

from remote_agent_collaboration.hooks_runtime import main


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
