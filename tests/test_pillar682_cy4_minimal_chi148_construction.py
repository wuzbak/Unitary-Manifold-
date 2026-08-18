# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 682 — CY4 χ=148 minimal construction."""
import pytest
from src.core.pillar682_cy4_minimal_chi148_construction import (
    K_CS, CHI_TARGET, CHI_COVERING, ORBIFOLD_ORDER, HODGE_NUMBERS,
    cy4_euler_chi_from_hodge,
    d3_tadpole_half_integer_shift_required,
    g4_flux_half_integer_shift,
    verify_cy_condition,
    braid_linkage,
    cy4_minimal_chi148_certificate,
)


# ── Basic constants ───────────────────────────────────────────────────────────

def test_k_cs_value():
    assert K_CS == 74

def test_chi_target_is_2_k_cs():
    assert CHI_TARGET == 2 * K_CS
    assert CHI_TARGET == 148

def test_chi_covering_is_12_k_cs():
    assert CHI_COVERING == 12 * K_CS
    assert CHI_COVERING == 888

def test_orbifold_order():
    assert ORBIFOLD_ORDER == 6

def test_chi_covering_equals_orbifold_times_chi_target():
    assert CHI_COVERING == ORBIFOLD_ORDER * CHI_TARGET


# ── Hodge numbers ─────────────────────────────────────────────────────────────

def test_hodge_numbers_keys():
    for key in ["h11", "h21", "h31", "h22"]:
        assert key in HODGE_NUMBERS

def test_hodge_numbers_non_negative():
    for v in HODGE_NUMBERS.values():
        assert v >= 0

def test_hodge_h21_zero():
    assert HODGE_NUMBERS["h21"] == 0

def test_hodge_h22_correct():
    # 8 + h11 + h31 + 2*h22 = 148 → 8 + 1 + 1 + 2*h22 = 148 → h22 = 69
    assert HODGE_NUMBERS["h22"] == 69


# ── Euler characteristic formula ──────────────────────────────────────────────

def test_cy4_euler_covering_is_888():
    chi = cy4_euler_chi_from_hodge(**HODGE_NUMBERS)
    assert chi == 888

def test_cy4_euler_orbifold_is_148():
    chi_cov = cy4_euler_chi_from_hodge(**HODGE_NUMBERS)
    assert chi_cov // ORBIFOLD_ORDER == 148

def test_cy4_euler_formula_manual():
    h11, h21, h31, h22 = 1, 0, 1, 69
    expected = 6 * (8 + 1 + 1 - 0 + 2 * 69)
    assert cy4_euler_chi_from_hodge(h11, h21, h31, h22) == expected


# ── D3-tadpole ────────────────────────────────────────────────────────────────

def test_d3_tadpole_chi_148_requires_shift():
    result = d3_tadpole_half_integer_shift_required(148)
    assert result["half_integer_shift_required"] is True
    assert not result["is_integer"]

def test_d3_tadpole_chi_24_no_shift():
    result = d3_tadpole_half_integer_shift_required(24)
    assert result["is_integer"] is True
    assert result["half_integer_shift_required"] is False

def test_d3_tadpole_chi_over_24_exact():
    result = d3_tadpole_half_integer_shift_required(148)
    # 148/24 = 37/6
    from fractions import Fraction
    assert Fraction(result["chi_over_24_exact"]) == Fraction(148, 24)


# ── G4 flux half-integer shift ────────────────────────────────────────────────

def test_g4_flux_status():
    result = g4_flux_half_integer_shift(148)
    assert result["status"] == "VERIFIED"

def test_g4_flux_shift_required():
    result = g4_flux_half_integer_shift(148)
    assert result["half_integer_shift_required"] is True

def test_g4_flux_quantization_condition():
    result = g4_flux_half_integer_shift(148)
    assert "G4 + c₂/2" in result["quantization_condition"]


# ── CY condition ──────────────────────────────────────────────────────────────

def test_verify_cy_condition_status():
    result = verify_cy_condition(HODGE_NUMBERS)
    assert result["status"] == "CY4_VERIFIED"

def test_verify_cy_condition_c1():
    result = verify_cy_condition(HODGE_NUMBERS)
    assert result["cy_condition_c1_zero"] == "CERTIFIED_BY_CONSTRUCTION"

def test_verify_cy_chi_orbifold():
    result = verify_cy_condition(HODGE_NUMBERS)
    assert result["chi_orbifold"] == 148


# ── Braid linkage ─────────────────────────────────────────────────────────────

def test_braid_linkage_k_cs():
    result = braid_linkage()
    assert result["k_cs"] == 74

def test_braid_linkage_chi_target():
    result = braid_linkage()
    assert result["chi_target"] == 148

def test_braid_linkage_chi_covering():
    result = braid_linkage()
    assert result["chi_covering"] == 888

def test_braid_linkage_pair():
    result = braid_linkage()
    assert result["braid_pair"] == (5, 7)

def test_braid_linkage_orbifold_order():
    result = braid_linkage()
    assert result["orbifold_order"] == 6


# ── Full certificate ──────────────────────────────────────────────────────────

def test_certificate_status():
    cert = cy4_minimal_chi148_certificate()
    assert cert["status"] == "ADJACENT_TRACK_CERTIFIED"

def test_certificate_pillar():
    cert = cy4_minimal_chi148_certificate()
    assert cert["pillar"] == "682"

def test_certificate_chi_target():
    cert = cy4_minimal_chi148_certificate()
    assert cert["chi_target"] == 148

def test_certificate_all_ok():
    cert = cy4_minimal_chi148_certificate()
    assert cert["all_ok"] is True

def test_certificate_toe_impact():
    cert = cy4_minimal_chi148_certificate()
    assert cert["toe_impact"] == 0

def test_certificate_track():
    cert = cy4_minimal_chi148_certificate()
    assert "ADJACENT" in cert["track"]

def test_certificate_honest_residuals_present():
    cert = cy4_minimal_chi148_certificate()
    assert len(cert["honest_residuals"]) >= 2
