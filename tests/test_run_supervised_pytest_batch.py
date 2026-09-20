# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
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

    def _fake_run(args, check=False):
        observed["args"] = args
        observed["check"] = check
        return Completed()

    monkeypatch.setattr(batch_runner.subprocess, "run", _fake_run)

    exit_code = batch_runner._run(["python", "-m", "pytest", "-m", "not slow", "tests/test_example.py", "-q"], dry_run=False)

    assert exit_code == 0
    assert observed["args"] == ["python", "-m", "pytest", "-m", "not slow", "tests/test_example.py", "-q"]
    assert observed["check"] is False


def test_main_skips_empty_fast_batch(monkeypatch, capsys) -> None:
    monkeypatch.setattr(batch_runner, "_parse_args", lambda: type("Args", (), {
        "suite": "tests-fast",
        "batch_count": 2,
        "batch_index": 1,
        "dry_run": False,
        "emit_json": False,
    })())
    monkeypatch.setattr(batch_runner, "fast_batch_argv", lambda batch_index, batch_count: [])

    assert batch_runner.main() == 0
    assert "no non-slow tests assigned to batch 1; skipping" in capsys.readouterr().out


def test_supervisor_emit_json_keeps_status_off_stdout(monkeypatch, capsys) -> None:
    monkeypatch.setattr(batch_runner, "_parse_args", lambda: type("Args", (), {
        "suite": "supervisor-check",
        "batch_count": 4,
        "batch_index": None,
        "dry_run": False,
        "emit_json": True,
    })())
    monkeypatch.setattr(batch_runner, "build_regression_supervision_plan", lambda batch_count: {
        "supervision": {
            "coverage_matches_discovery": True,
            "all_files_unique": True,
        }
    })

    assert batch_runner.main() == 0
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("{")
    assert "supervised regression coverage check passed" not in captured.out
    assert "supervised regression coverage check passed" in captured.err


def test_full_core_main_executes_full_core_batch(monkeypatch) -> None:
    observed: dict[str, object] = {}

    monkeypatch.setattr(batch_runner, "_parse_args", lambda: type("Args", (), {
        "suite": "full-core",
        "batch_count": 8,
        "batch_index": 3,
        "dry_run": False,
        "emit_json": False,
    })())
    monkeypatch.setattr(batch_runner, "full_core_batch_argv", lambda batch_index, batch_count: ["python", "-m", "pytest", "tests/test_example.py", "-q"])
    def _fake_run(args, dry_run):
        observed["args"] = args
        observed["dry_run"] = dry_run
        return 0
    monkeypatch.setattr(batch_runner, "_run", _fake_run)

    assert batch_runner.main() == 0
    assert observed["args"] == ["python", "-m", "pytest", "tests/test_example.py", "-q"]
    assert observed["dry_run"] is False


def test_full_core_supervisor_emit_json_keeps_status_off_stdout(monkeypatch, capsys) -> None:
    monkeypatch.setattr(batch_runner, "_parse_args", lambda: type("Args", (), {
        "suite": "full-core-supervisor-check",
        "batch_count": 8,
        "batch_index": None,
        "dry_run": False,
        "emit_json": True,
    })())
    monkeypatch.setattr(batch_runner, "build_regression_supervision_plan", lambda batch_count: {
        "supervision": {
            "full_core_coverage_matches_discovery": True,
            "full_core_all_files_unique": True,
        }
    })

    assert batch_runner.main() == 0
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("{")
    assert "supervised full-core regression coverage check passed" not in captured.out
    assert "supervised full-core regression coverage check passed" in captured.err
