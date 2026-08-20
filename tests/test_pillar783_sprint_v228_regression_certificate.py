# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 783 — Sprint v22.5–v22.8 Regression Certificate."""
from __future__ import annotations
import pytest
from src.core.pillar783_sprint_v228_regression_certificate import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_SPRINT_NEW_TOTAL, LEAN4_SPRINT_PREV_TOTAL, LEAN4_SPRINT_NEW_THEOREMS,
    PILLARS_IN_SPRINT, SPRINT_EPISTEMIC_DELTAS,
    sprint_summary, pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 783

def test_pillar_status():
    assert PILLAR_STATUS == "SPRINT_V225_V228_REGRESSION_PASSED"

def test_version():
    assert VERSION == "v22.8"

def test_lean4_prev_total():
    assert LEAN4_SPRINT_PREV_TOTAL == 872

def test_lean4_new_theorems():
    assert LEAN4_SPRINT_NEW_THEOREMS == 86

def test_lean4_new_total():
    assert LEAN4_SPRINT_NEW_TOTAL == 958

def test_lean4_formula():
    assert LEAN4_SPRINT_NEW_TOTAL == LEAN4_SPRINT_PREV_TOTAL + LEAN4_SPRINT_NEW_THEOREMS

def test_pillars_in_sprint_range():
    assert PILLARS_IN_SPRINT == list(range(774, 784))

def test_pillars_count():
    assert len(PILLARS_IN_SPRINT) == 10

def test_epistemic_deltas_count():
    assert len(SPRINT_EPISTEMIC_DELTAS) == 9

def test_sprint_lean4_check():
    summary = sprint_summary()
    assert summary["lean4_check"] is True

def test_sprint_lean4_new():
    summary = sprint_summary()
    assert summary["lean4_new"] == 86

def test_sprint_lean4_total():
    summary = sprint_summary()
    assert summary["lean4_total"] == 958

def test_sprint_np_bc_chains():
    summary = sprint_summary()
    chains = summary["np_bc_chains_resolved"]
    assert len(chains) == 4
    assert any("NP-BC-1" in c for c in chains)
    assert any("NP-BC-4" in c for c in chains)

def test_sprint_gap_statuses():
    summary = sprint_summary()
    assert "PROVED_LEAN4_FORMAL" in summary["gap_3_status"]
    assert "PARTIALLY_CONSTRAINED" in summary["gap_4_status"]
    assert "DECOMPOSED" in summary["gap_5_status"]

def test_sprint_dm21_status():
    summary = sprint_summary()
    assert "ARCHITECTURE_LIMIT" in summary["dm21_status"]
    assert "NNLO" in summary["dm21_status"]

def test_sprint_alpha_s_status():
    summary = sprint_summary()
    assert "ALL_ROUTES" in summary["alpha_s_status"]

def test_sprint_open_gaps():
    summary = sprint_summary()
    assert len(summary["open_gaps_remaining"]) >= 2

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4", "sprint"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 872
    assert lean4["new_theorems"] == 86
    assert lean4["new_total"] == 958
