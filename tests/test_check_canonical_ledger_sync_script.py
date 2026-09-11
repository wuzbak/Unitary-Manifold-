# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


@pytest.fixture
def ledger_sync_script_module():
    script_path = Path(__file__).resolve().parents[1] / "TOOLS" / "checks" / "check_canonical_ledger_sync.py"
    spec = importlib.util.spec_from_file_location("check_canonical_ledger_sync", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_split_patch_by_path_includes_rename_source_and_target(ledger_sync_script_module):
    patches = ledger_sync_script_module._split_patch_by_path(
        "\n".join(
            [
                "diff --git a/src/core/pillar1119_old_name.py b/src/core/pillar1119_new_name.py",
                "--- a/src/core/pillar1119_old_name.py",
                "+++ b/src/core/pillar1119_new_name.py",
                "@@ -1 +1 @@",
                "-PILLAR_STATUS = 'OLD'",
                "+PILLAR_STATUS = 'NEW'",
                "diff --git a/src/core/sm_free_parameters.py b/src/core/sm_free_parameters.py",
                "--- a/src/core/sm_free_parameters.py",
                "+++ b/src/core/sm_free_parameters.py",
                "@@ -1 +1 @@",
                "-x = 1",
                "+x = 2",
            ]
        )
    )
    assert set(patches) == {
        "src/core/pillar1119_old_name.py",
        "src/core/pillar1119_new_name.py",
        "src/core/sm_free_parameters.py",
    }


def test_split_patch_by_path_maps_deleted_file_from_markers(ledger_sync_script_module):
    patches = ledger_sync_script_module._split_patch_by_path(
        "\n".join(
            [
                "diff --git a/src/core/pillar1119_old_name.py b/dev/null",
                "deleted file mode 100644",
                "--- a/src/core/pillar1119_old_name.py",
                "+++ /dev/null",
                "@@ -1 +0,0 @@",
                "-PILLAR_STATUS = 'OLD'",
            ]
        )
    )
    assert patches["src/core/pillar1119_old_name.py"].startswith(
        "diff --git a/src/core/pillar1119_old_name.py b/dev/null"
    )
    assert "dev/null" not in patches


def test_split_patch_by_path_ignores_dev_null_header_paths(ledger_sync_script_module):
    patches = ledger_sync_script_module._split_patch_by_path(
        "diff --git a/src/core/pillar1119_old_name.py b/dev/null"
    )
    assert patches == {
        "src/core/pillar1119_old_name.py": "diff --git a/src/core/pillar1119_old_name.py b/dev/null"
    }
    assert "dev/null" not in patches


def test_expanded_changed_files_include_rename_source_and_target(ledger_sync_script_module):
    changed = ledger_sync_script_module._expanded_changed_files(
        ["STATUS.md"],
        ["R100\tSTATUS.md\tSTATUS_OLD.md"],
    )
    assert changed == ["STATUS.md", "STATUS_OLD.md"]


def test_main_passes_when_sync_not_required(monkeypatch, capsys, ledger_sync_script_module):
    monkeypatch.setattr(
        ledger_sync_script_module,
        "_git_diff_lines",
        lambda *, base_sha, head_sha, name_only: ["src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py"] if name_only else ["M\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py"],
    )
    monkeypatch.setattr(ledger_sync_script_module, "_git_full_patch", lambda **kwargs: "@@ harmless @@\n+value = 1\n")
    monkeypatch.setattr(sys, "argv", ["check_canonical_ledger_sync.py", "--base-sha", "base", "--head-sha", "head"])

    assert ledger_sync_script_module.main() == 0
    out = capsys.readouterr().out
    assert "OK: canonical ledger sync not required for this diff." in out


def test_main_fails_when_required_ledgers_missing(monkeypatch, capsys, ledger_sync_script_module):
    monkeypatch.setattr(
        ledger_sync_script_module,
        "_git_diff_lines",
        lambda *, base_sha, head_sha, name_only: ["src/core/pillar1121_new_name.py"] if name_only else ["A\tsrc/core/pillar1121_new_name.py"],
    )
    monkeypatch.setattr(ledger_sync_script_module, "_git_full_patch", lambda **kwargs: "")
    monkeypatch.setattr(sys, "argv", ["check_canonical_ledger_sync.py", "--base-sha", "base", "--head-sha", "head"])

    assert ledger_sync_script_module.main() == 1
    out = capsys.readouterr().out
    assert "::error::Missing required ledger update: STATUS.md" in out
    assert "Wave/pillar changes require canonical ledger + changelog synchronization." in out


def test_main_passes_when_required_ledgers_are_present(monkeypatch, capsys, ledger_sync_script_module):
    changed = [
        "src/core/pillar1121_new_name.py",
        "STATUS.md",
        "FALLIBILITY.md",
        "README.md",
        "1-THEORY/DERIVATION_STATUS.md",
        "docs/WAVE_CHANGELOG.md",
    ]
    monkeypatch.setattr(
        ledger_sync_script_module,
        "_git_diff_lines",
        lambda *, base_sha, head_sha, name_only: changed if name_only else ["A\tsrc/core/pillar1121_new_name.py"],
    )
    monkeypatch.setattr(ledger_sync_script_module, "_git_full_patch", lambda **kwargs: "")
    monkeypatch.setattr(sys, "argv", ["check_canonical_ledger_sync.py", "--base-sha", "base", "--head-sha", "head"])

    assert ledger_sync_script_module.main() == 0
    out = capsys.readouterr().out
    assert "OK: canonical ledger sync present for status-bearing pillar changes." in out


def test_git_full_patch_uses_rename_and_copy_detection(monkeypatch, ledger_sync_script_module):
    calls = {}

    class _Completed:
        stdout = ""

    def _fake_run(args, check, capture_output, text):
        calls["args"] = args
        return _Completed()

    monkeypatch.setattr(ledger_sync_script_module.subprocess, "run", _fake_run)
    ledger_sync_script_module._git_full_patch(base_sha="base", head_sha="head")
    assert "--find-renames" in calls["args"]
    assert "--find-copies" in calls["args"]


def test_git_diff_lines_uses_rename_and_copy_detection(monkeypatch, ledger_sync_script_module):
    calls = {}

    class _Completed:
        stdout = ""

    def _fake_run(args, check, capture_output, text):
        calls["args"] = args
        return _Completed()

    monkeypatch.setattr(ledger_sync_script_module.subprocess, "run", _fake_run)
    ledger_sync_script_module._git_diff_lines(base_sha="base", head_sha="head", name_only=False)
    assert "--find-renames" in calls["args"]
    assert "--find-copies" in calls["args"]


def test_workflow_invokes_ledger_sync_script():
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "staleness-honesty-gate.yml"
    content = workflow_path.read_text(encoding="utf-8")
    assert "Enforce canonical ledger sync for wave/pillar changes" in content
    assert "python3 TOOLS/checks/check_canonical_ledger_sync.py" in content
    assert "--base-sha" in content
    assert "--head-sha" in content
    assert '${{ github.sha }}' in content
