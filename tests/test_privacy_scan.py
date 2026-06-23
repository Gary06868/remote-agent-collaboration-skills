from __future__ import annotations

from pathlib import Path

from remote_agent_collaboration.cli import main


def test_privacy_scan_passes_clean_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "README.md").write_text("source project and project lead\n", encoding="utf-8")
    assert main(["privacy-scan"]) == 0
