# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_module():
    script_path = Path(__file__).resolve().parents[1] / "TOOLS" / "checks" / "check_large_files.py"
    spec = importlib.util.spec_from_file_location("check_large_files", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_fails_when_file_exceeds_limit(monkeypatch, capsys):
    module = _load_module()

    monkeypatch.setattr(module, "tracked_paths", lambda: [Path("oversized.bin")])
    monkeypatch.setattr(module.Path, "exists", lambda _: True)
    monkeypatch.setattr(module.os.path, "getsize", lambda _: 11)
    monkeypatch.setattr(sys, "argv", ["check_large_files.py", "--max-bytes", "10"])

    assert module.main() == 1
    out = capsys.readouterr().out
    assert "::error::oversized.bin is 11 bytes" in out


def test_main_passes_with_allowlist(monkeypatch, capsys):
    module = _load_module()

    monkeypatch.setattr(module, "tracked_paths", lambda: [Path("allowed-large.pdf")])
    monkeypatch.setattr(module.Path, "exists", lambda _: True)
    monkeypatch.setattr(module.os.path, "getsize", lambda _: 9999999)
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_large_files.py", "--max-bytes", "10", "--allow", "allowed-large.pdf"],
    )

    assert module.main() == 0
    out = capsys.readouterr().out
    assert "OK: tracked files are <= 10 bytes" in out


def test_main_uses_changed_paths_when_shas_provided(monkeypatch, capsys):
    module = _load_module()

    monkeypatch.setattr(module, "changed_paths", lambda base_sha, head_sha: [Path("delta.bin")])
    monkeypatch.setattr(module.Path, "exists", lambda _: True)
    monkeypatch.setattr(module.os.path, "getsize", lambda _: 11)
    monkeypatch.setattr(module, "tracked_paths", lambda: [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_large_files.py",
            "--max-bytes",
            "10",
            "--base-sha",
            "base",
            "--head-sha",
            "head",
        ],
    )

    assert module.main() == 1
    out = capsys.readouterr().out
    assert "::error::delta.bin is 11 bytes" in out


def test_main_fails_when_only_one_sha_is_provided(monkeypatch, capsys):
    module = _load_module()
    monkeypatch.setattr(sys, "argv", ["check_large_files.py", "--base-sha", "base"])
    assert module.main() == 1
    out = capsys.readouterr().out
    assert "--base-sha and --head-sha must be provided together" in out


def test_main_fails_on_symlink_candidate(monkeypatch, capsys):
    module = _load_module()

    monkeypatch.setattr(module, "tracked_paths", lambda: [Path("linked.bin")])
    monkeypatch.setattr(module.Path, "exists", lambda _: True)
    monkeypatch.setattr(module.Path, "is_symlink", lambda _: True)
    monkeypatch.setattr(sys, "argv", ["check_large_files.py", "--max-bytes", "10"])

    assert module.main() == 1
    out = capsys.readouterr().out
    assert "::error::linked.bin is a symlink" in out


def test_changed_paths_includes_type_changes(monkeypatch):
    module = _load_module()
    calls = {}

    class _Completed:
        stdout = b"file.bin\x00"

    def _fake_run(args, check, capture_output, text):
        calls["args"] = args
        return _Completed()

    monkeypatch.setattr(module.subprocess, "run", _fake_run)
    paths = module.changed_paths(base_sha="base", head_sha="head")
    assert "-z" in calls["args"]
    assert "--diff-filter=AMRT" in calls["args"]
    assert paths == [Path("file.bin")]


def test_workflow_invokes_large_file_guard():
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "tests.yml"
    content = workflow_path.read_text(encoding="utf-8")
    assert "Enforce tracked-file size limit" in content
    assert "python TOOLS/checks/check_large_files.py" in content
    assert "--base-sha" in content
    assert "--head-sha" in content
    assert "github.event.pull_request.head.sha" in content


def test_bazel_pilot_workflow_tracks_guard_files():
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "bazel-pilot.yml"
    content = workflow_path.read_text(encoding="utf-8")
    assert "tests/test_check_large_files.py" in content
    assert "TOOLS/checks/check_large_files.py" in content
