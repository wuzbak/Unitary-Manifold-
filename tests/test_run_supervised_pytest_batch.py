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

    exit_code = batch_runner._run('python -m pytest -m "not slow" tests/test_example.py -q', dry_run=False)

    assert exit_code == 0
    assert observed["args"] == ["python", "-m", "pytest", "-m", "not slow", "tests/test_example.py", "-q"]
    assert observed["check"] is False
