# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Post-MAS Track 3 neural-symbolic drift checks."""

from __future__ import annotations

import pytest

pytest.importorskip("sympy", reason="sympy not installed — skip SymPy-dependent tests")

from src.core.neural_symbolic_drift_check import (
    equation_family_report,
    track3_drift_artifact,
)


def test_equation_family_report_has_families():
    report = equation_family_report()
    assert "families" in report
    assert "inflation_observables" in report["families"]
    assert "dark_energy_sector" in report["families"]


def test_track3_artifact_pass():
    artifact = track3_drift_artifact()
    assert artifact["track"] == "T3"
    assert artifact["status"] == "PASS"


def test_each_family_contains_equations():
    report = equation_family_report()
    for family_data in report["families"].values():
        assert len(family_data["equations"]) >= 1

