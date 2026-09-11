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


def test_tracked_patch_paths_include_rename_source_and_target(ledger_sync_script_module):
    paths = ledger_sync_script_module._tracked_patch_paths(
        [
            "R100\tsrc/core/pillar1119_old_name.py\tsrc/core/pillar1119_new_name.py",
            "M\tsrc/core/sm_free_parameters.py",
        ]
    )
    assert paths == [
        "src/core/pillar1119_new_name.py",
        "src/core/pillar1119_old_name.py",
        "src/core/sm_free_parameters.py",
    ]


def test_main_passes_when_sync_not_required(monkeypatch, capsys, ledger_sync_script_module):
    monkeypatch.setattr(
        ledger_sync_script_module,
        "_git_diff_lines",
        lambda *, base_sha, head_sha, name_only: ["src/core/pillar1087_sprint_cm_full_physics_parallel_execution.py"] if name_only else ["M\tsrc/core/pillar1087_sprint_cm_full_physics_parallel_execution.py"],
    )
    monkeypatch.setattr(ledger_sync_script_module, "_git_patch_for_path", lambda **kwargs: "@@ harmless @@\n+value = 1\n")
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
    monkeypatch.setattr(ledger_sync_script_module, "_git_patch_for_path", lambda **kwargs: "")
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
    monkeypatch.setattr(ledger_sync_script_module, "_git_patch_for_path", lambda **kwargs: "")
    monkeypatch.setattr(sys, "argv", ["check_canonical_ledger_sync.py", "--base-sha", "base", "--head-sha", "head"])

    assert ledger_sync_script_module.main() == 0
    out = capsys.readouterr().out
    assert "OK: canonical ledger sync present for status-bearing pillar changes." in out
