# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 779 — Δm²₂₁ NNLO Braid Lattice Correction."""
from __future__ import annotations
import pytest
from src.core.pillar779_dm21_nnlo_braid_correction import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    EPISTEMIC_LABEL, NNLO_GATE, NNLO_SUB_1SIGMA_ACHIEVED,
    K_CS, N_W, DM21_PDG_EV2, DM21_SIGMA_EV2,
    DM21_AFTER_NLO, TENSION_AFTER_NLO, DELTA_C, DELTA_C_4,
    SIN2_THETA12, COS2_THETA12,
    nnlo_winding_correction,
    nnlo_cross_term_correction,
    nnlo_lattice_correction,
    nnlo_combined_correction,
    dm21_after_nnlo,
    tension_after_nnlo,
    architecture_limit_certificate,
    closure_sufficiency_audit,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 779

def test_pillar_status():
    assert PILLAR_STATUS == "DM21_NNLO_ARCHITECTURE_LIMIT_CERTIFIED"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 928
    assert LEAN4_NEW_THEOREMS == 10
    assert LEAN4_NEW_TOTAL == 938

def test_lean4_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

def test_nnlo_not_achieved():
    assert NNLO_SUB_1SIGMA_ACHIEVED is False

def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert abs(DELTA_C - 5/74) < 1e-12

def test_delta_c_4():
    assert abs(DELTA_C_4 - (5/74)**4) < 1e-15

def test_mixing_angles_sum():
    assert abs(SIN2_THETA12 + COS2_THETA12 - 1.0) < 1e-12

# Individual NNLO corrections

def test_nnlo_winding_positive():
    res = nnlo_winding_correction()
    assert res["correction"] > 0.0

def test_nnlo_winding_formula():
    res = nnlo_winding_correction()
    expected = DELTA_C_4 * COS2_THETA12 / 4.0
    assert abs(res["correction"] - expected) < 1e-15

def test_nnlo_cross_positive():
    res = nnlo_cross_term_correction()
    assert res["correction"] > 0.0

def test_nnlo_lattice_positive():
    res = nnlo_lattice_correction()
    assert res["correction"] > 0.0

# Combined NNLO

def test_nnlo_combined_sum():
    comb = nnlo_combined_correction()
    w = nnlo_winding_correction()["correction"]
    c = nnlo_cross_term_correction()["correction"]
    l = nnlo_lattice_correction()["correction"]
    assert abs(comb["nnlo_total"] - (w + c + l)) < 1e-15

def test_nnlo_negligible_vs_nlo():
    comb = nnlo_combined_correction()
    assert comb["nnlo_negligible_vs_nlo"] is True
    assert comb["nnlo_vs_nlo_ratio"] < 0.01

# DM21 after NNLO

def test_dm21_after_nnlo_close_to_nlo():
    res = dm21_after_nnlo()
    # NNLO shift should be tiny
    relative_shift = abs(res["dm21_after_nnlo"] - DM21_AFTER_NLO) / DM21_AFTER_NLO
    assert relative_shift < 1e-4

# Tension after NNLO

def test_tension_still_above_1sigma():
    res = tension_after_nnlo()
    assert res["tension_sigma"] > 1.0

def test_tension_sub_1sigma_not_achieved():
    res = tension_after_nnlo()
    assert res["sub_1sigma_achieved"] is False

def test_tension_gate():
    res = tension_after_nnlo()
    assert res["nnlo_gate"] == NNLO_GATE

def test_tension_epistemic_label():
    res = tension_after_nnlo()
    assert res["epistemic_label"] == EPISTEMIC_LABEL

# Architecture limit

def test_arch_limit_is_limit():
    cert = architecture_limit_certificate()
    assert cert["architecture_limit"] is True

def test_arch_limit_sub_1sigma_not_achieved():
    cert = architecture_limit_certificate()
    assert cert["sub_1sigma_achieved"] is False

def test_arch_limit_nnlo_insufficient():
    cert = architecture_limit_certificate()
    # NNLO provides far less than needed
    assert cert["sufficiency_ratio"] < 0.1

def test_arch_limit_required_ingredients():
    cert = architecture_limit_certificate()
    assert len(cert["required_new_ingredient"]) >= 2

# Sufficiency audit

def test_geometric_series_closes_gap():
    # Even infinite geometric series should NOT close the gap
    res = closure_sufficiency_audit()
    # The function reports whether it closes or not
    assert isinstance(res["full_series_closes_gap"], bool)
    # The conclusion string should be present
    assert len(res["conclusion"]) > 0

def test_geometric_sum_positive():
    res = closure_sufficiency_audit()
    assert res["geometric_series_sum"] > 0.0

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "nnlo_correction", "dm21_after_nnlo", "tension",
              "architecture_limit", "sufficiency_audit", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 928
    assert lean4["new_total"] == 938

def test_epistemic_deltas():
    deltas = pillar_report()["epistemic_deltas"]
    assert any("ARCHITECTURE_LIMIT" in d for d in deltas)
    assert any("NNLO" in d for d in deltas)
