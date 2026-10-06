# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "TOOLS"
    / "checks"
    / "run_supervised_pytest_batch.py"
)
SPEC = importlib.util.spec_from_file_location("run_supervised_pytest_batch", MODULE_PATH)
assert SPEC and SPEC.loader
batch_runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch_runner)


def test_run_executes_pytest_without_shell(monkeypatch) -> None:
    observed: dict[str, object] = {}

    class Completed:
        returncode = 0

    def _fake_run(args, check=False, cwd=None):
        observed["args"] = args
        observed["check"] = check
        observed["cwd"] = cwd
        return Completed()

    monkeypatch.setattr(batch_runner.subprocess, "run", _fake_run)

    exit_code = batch_runner._run(["python", "-m", "pytest", "-m", "not slow", "tests/test_example.py", "-q"], dry_run=False)

    assert exit_code == 0
    assert observed["args"] == ["python", "-m", "pytest", "-m", "not slow", "tests/test_example.py", "-q"]
    assert observed["check"] is False
    assert observed["cwd"] == batch_runner.ROOT


def test_main_skips_empty_fast_batch(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "tests-fast", "--batch-count", "2", "--batch-index", "1",
    ])
    monkeypatch.setattr(batch_runner, "fast_batch_argv", lambda batch_index, batch_count: [])

    assert batch_runner.main() == 0
    assert "no tests assigned to batch 1; skipping" in capsys.readouterr().out


def test_supervisor_emit_json_keeps_status_off_stdout(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "supervisor-check", "--batch-count", "4", "--emit-json",
    ])
    monkeypatch.setattr(batch_runner, "build_regression_supervision_plan_with_full_core_count", lambda **kwargs: {
        "supervision": {
            "coverage_matches_discovery": True,
            "all_files_unique": True,
        }
    })

    assert batch_runner.main() == 0
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("{")
    assert "structural file coverage check passed" not in captured.out
    assert "supervised regression structural file coverage check passed (not execution evidence)" in captured.err


def test_full_core_main_executes_full_core_batch(monkeypatch) -> None:
    observed: dict[str, object] = {}

    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "full-core", "--batch-count", "8", "--batch-index", "3",
    ])
    monkeypatch.setattr(batch_runner, "full_core_batch_argv", lambda batch_index, batch_count: ["python", "-m", "pytest", "tests/test_example.py", "-q"])
    def _fake_run(args, dry_run, timeout=None):
        observed["args"] = args
        observed["dry_run"] = dry_run
        observed["timeout"] = timeout
        return 0
    monkeypatch.setattr(batch_runner, "_run", _fake_run)

    assert batch_runner.main() == 0
    assert observed["args"] == ["python", "-m", "pytest", "tests/test_example.py", "-q"]
    assert observed["dry_run"] is False
    assert observed["timeout"] is None


def test_full_core_main_uses_full_core_default_batch_count(monkeypatch) -> None:
    observed: dict[str, object] = {}

    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "full-core", "--batch-index", "3",
    ])
    def _fake_full_core_batch_argv(batch_index, batch_count):
        observed["batch_index"] = batch_index
        observed["batch_count"] = batch_count
        return ["python", "-m", "pytest", "tests/test_example.py", "-q"]
    monkeypatch.setattr(batch_runner, "full_core_batch_argv", _fake_full_core_batch_argv)
    monkeypatch.setattr(batch_runner, "_run", lambda args, dry_run, timeout=None: 0)

    assert batch_runner.main() == 0
    assert observed["batch_index"] == 3
    assert observed["batch_count"] == 8


def test_full_core_supervisor_emit_json_keeps_status_off_stdout(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "full-core-supervisor-check", "--batch-count", "8", "--emit-json",
    ])
    monkeypatch.setattr(batch_runner, "build_regression_supervision_plan_with_full_core_count", lambda **kwargs: {
        "supervision": {
            "full_core_coverage_matches_discovery": True,
            "full_core_all_files_unique": True,
        }
    })

    assert batch_runner.main() == 0
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("{")
    assert "structural file coverage check passed" not in captured.out
    assert "supervised full-core regression structural file coverage check passed (not execution evidence)" in captured.err


def test_full_core_supervisor_uses_full_core_default_batch_count(monkeypatch, capsys) -> None:
    observed: dict[str, object] = {}

    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "full-core-supervisor-check",
    ])
    def _fake_plan(**kwargs):
        observed.update(kwargs)
        return {
            "supervision": {
                "full_core_coverage_matches_discovery": True,
                "full_core_all_files_unique": True,
            }
        }
    monkeypatch.setattr(batch_runner, "build_regression_supervision_plan_with_full_core_count", _fake_plan)

    assert batch_runner.main() == 0
    assert observed["batch_count"] == 4
    assert observed["full_core_batch_count"] == 8
    assert "supervised full-core regression structural file coverage check passed (not execution evidence)" in capsys.readouterr().out


def test_evidence_mode_wraps_existing_command(monkeypatch, tmp_path) -> None:
    import argparse
    import sys

    observed = {}
    command = ["python", "-m", "pytest", "-m", "", "tests/test_example.py", "-q"]

    def fake_run(args, dry_run):
        observed["args"] = args
        observed["dry_run"] = dry_run
        return 7

    monkeypatch.setattr(batch_runner, "_run", fake_run)
    args = argparse.Namespace(evidence_dir=tmp_path, timeout=15, dry_run=True)
    assert batch_runner._execute(command, args) == 7
    assert observed["args"] == [
        sys.executable, "-m", "TOOLS.um_arts", "capture",
        "--repo", str(batch_runner.ROOT), "--output", str(tmp_path.resolve()),
        "--timeout", "15", "--", *command,
    ]
    assert observed["dry_run"] is True


def test_timeout_must_be_positive_finite(monkeypatch) -> None:
    import sys

    import pytest

    for timeout in ("0", "-1", "nan", "inf"):
        monkeypatch.setattr(sys, "argv", [
            str(MODULE_PATH), "--suite", "compactified-preflight", "--timeout", timeout,
        ])
        with pytest.raises(SystemExit) as error:
            batch_runner._parse_args()
        assert error.value.code == 2


def test_receipt_batch_preserves_capture_evidence(monkeypatch, tmp_path) -> None:
    import json

    observed = {}
    monkeypatch.setattr(batch_runner, "ROOT", tmp_path / "project")
    monkeypatch.setattr(batch_runner, "_snapshot", lambda: {"head": "abc", "worktree_digest": "def"})
    monkeypatch.setattr(batch_runner, "_environment_fingerprint", lambda: {"python": "test"})
    monkeypatch.setenv("PYTEST_ADDOPTS", "")
    batches = [{"test_paths": ["tests/test_example.py"]}]
    monkeypatch.setattr(batch_runner, "build_regression_supervision_plan_with_full_core_count",
                        lambda **kwargs: {"supervised_fast_suite": {"batches": batches}})
    monkeypatch.setattr(batch_runner, "fast_batch_argv",
                        lambda **kwargs: ["python", "-m", "pytest", "tests/test_example.py", "-q"])
    results = tmp_path / "results"
    evidence = tmp_path / "evidence"

    def fake_run(command, dry_run):
        observed["command"] = command
        junit = next(item.split("=", 1)[1] for item in command if item.startswith("--junitxml="))
        Path(junit).write_text(
            '<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase name="ok"/></testsuite>')
        return 0

    monkeypatch.setattr(batch_runner, "_run", fake_run)
    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "tests-fast", "--batch-index", "0",
        "--result-dir", str(results), "--evidence-dir", str(evidence), "--timeout", "15",
    ])
    assert batch_runner.main() == 0
    assert observed["command"][:4] == [sys.executable, "-m", "TOOLS.um_arts", "capture"]
    assert str(evidence.resolve()) in observed["command"]
    receipt = json.loads((results / "tests-fast-0.json").read_text())
    assert receipt["status"] == "success"
    assert receipt["counts"]["tests"] == 1
    monkeypatch.setattr(sys, "argv", [
        "runner", "--suite", "tests-fast", "--aggregate", "--result-dir", str(results),
    ])
    assert batch_runner.main() == 0
