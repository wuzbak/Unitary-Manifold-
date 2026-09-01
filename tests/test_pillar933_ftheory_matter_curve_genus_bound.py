# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 933 — Matter-Curve CY₄ Genus Correction Bound."""
from __future__ import annotations
from src.core.pillar933_ftheory_matter_curve_genus_bound import (
    N_W, K_CS, CHI_CY4, CHI_FIBRE, GENUS_MATTER_CURVE,
    DELTA_NGEN_FRAC, GENUS_CORRECTION_SUPPRESSED,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    genus_correction_bound, genus_bound_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 933
def test_gate(): assert PILLAR_GATE == "FTHEORY_MATTER_CURVE_GENUS_BOUND"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74

def test_chi_cy4_positive(): assert CHI_CY4 > 0
def test_chi_cy4_value(): assert CHI_CY4 == 23328
def test_chi_fibre_zero(): assert CHI_FIBRE == 0   # torus T²
def test_genus_order(): assert GENUS_MATTER_CURVE >= 100

def test_delta_ngen_frac_zero(): assert DELTA_NGEN_FRAC == 0.0
def test_genus_correction_suppressed(): assert GENUS_CORRECTION_SUPPRESSED is True

def test_status_suppressed(): assert PILLAR_STATUS == "MATTER_CURVE_GENUS_SUPPRESSED"

def test_bound_dict_keys():
    res = genus_correction_bound()
    assert "status" in res
    assert "delta_ngen_frac" in res
    assert "genus_correction_suppressed" in res

def test_bound_status_matches():
    res = genus_correction_bound()
    assert res["status"] == PILLAR_STATUS

def test_summary_pillar():
    s = genus_bound_summary()
    assert s["pillar"] == 933

def test_summary_suppressed():
    s = genus_bound_summary()
    assert s["genus_correction_suppressed"] is True
