# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 956 — N₂=7 Two-Radius GW Derivation."""

import math
import pytest
from src.core.pillar956_n2_two_radius_gw_derivation import (
    PILLAR_STATUS, PILLAR_VALID, N_1, N_2_CANONICAL, K_CS_57, R_BARE,
    BICEP_KECK_R_LIMIT, is_z2_odd, winding_tension_ratio, z2_odd_partners,
    derive_n2_from_geometry, winding_tension_minimum_two_radius,
    n2_uniqueness_full_audit, fallibility_update, pillar956_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "N2_7_DERIVED_FROM_Z2_ODD_MINIMUM_STEP"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_n1_value():
    assert N_1 == 5


def test_n2_canonical():
    assert N_2_CANONICAL == 7


def test_k_cs():
    assert K_CS_57 == 74
    assert N_1**2 + N_2_CANONICAL**2 == K_CS_57


def test_r_bare():
    # r_bare = 96/φ₀_eff² where φ₀_eff² ≈ 987 → r_bare ≈ 0.097
    assert abs(R_BARE - 0.097) < 0.001


def test_bicep_limit():
    assert BICEP_KECK_R_LIMIT == 0.036


def test_z2_odd_odd():
    assert is_z2_odd(5) is True
    assert is_z2_odd(7) is True
    assert is_z2_odd(9) is True


def test_z2_odd_even():
    assert is_z2_odd(6) is False
    assert is_z2_odd(8) is False
    assert is_z2_odd(4) is False


def test_winding_tension_ratio():
    r = winding_tension_ratio(5, 7)
    expected = (7.0 / 5.0) ** (2.0 / 3.0)
    assert abs(r - expected) < 1e-10


def test_winding_tension_ratio_n2_gt_n1():
    # n2 > n1 → R2 > R1
    r = winding_tension_ratio(5, 7)
    assert r > 1.0


def test_z2_odd_partners_contains_7():
    partners = z2_odd_partners(5)
    n2_values = [p["n2"] for p in partners]
    assert 7 in n2_values


def test_z2_odd_partners_excludes_6():
    partners = z2_odd_partners(5)
    p6 = [p for p in partners if p["n2"] == 6][0]
    assert p6["z2_odd"] is False  # n2=6 is even → Z₂-odd BC violated


def test_n2_7_is_minimum_step():
    partners = z2_odd_partners(5)
    p7 = [p for p in partners if p["n2"] == 7][0]
    assert p7["is_minimum_step_z2_odd"] is True


def test_n2_9_is_not_minimum_step():
    partners = z2_odd_partners(5)
    p9 = [p for p in partners if p["n2"] == 9][0]
    assert p9["is_minimum_step_z2_odd"] is False


def test_n2_7_satisfies_r_bound():
    partners = z2_odd_partners(5)
    p7 = [p for p in partners if p["n2"] == 7][0]
    assert p7["r_bicep_ok"] is True


def test_derive_n2_result_is_7():
    result = derive_n2_from_geometry()
    assert result["minimum_step_n2"] == 7
    assert result["n2_is_7"] is True


def test_derive_n2_no_cme_input():
    result = derive_n2_from_geometry()
    assert result["derivation_used_cme_data"] is False


def test_derive_n2_kcs_matches():
    result = derive_n2_from_geometry()
    assert result["k_cs_matches_known_value"] is True


def test_winding_tension_minimum():
    result = winding_tension_minimum_two_radius()
    assert result["R1_smaller"] is True
    assert result["short_cycle_n1"] == 5
    assert result["long_cycle_n2"] == 7
    assert result["convention_279_3_confirmed"] is True


def test_uniqueness_audit():
    audit = n2_uniqueness_full_audit()
    assert audit["unique_survivor"] is True
    assert audit["survivor_n2"] == 7
    assert audit["geometric_derivation_complete"] is True
    assert audit["observational_input_required"] is False


def test_fallibility_update():
    fb = fallibility_update()
    assert "GEOMETRICALLY DERIVED" in fb["new_status"]
    assert fb["pillar"] == 956


def test_summary():
    s = pillar956_summary()
    assert s["pillar"] == 956
    assert s["n2_canonical"] == 7
    assert s["valid"] is True
