# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Regression checks for status drift gate tooling."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("status_drift_gate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_status_drift_gate_passes_on_repo():
    module = _load_module(REPO_ROOT / "9-INFRASTRUCTURE" / "check_status_drift.py")
    failures = module.run_checks(REPO_ROOT)
    assert failures == []

