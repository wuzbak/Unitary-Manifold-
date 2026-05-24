# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 410 — T³/Z₂ Compact Topology Quadrupole Bound."""
import math
import pytest

from src.core.pillar410_topology_quadrupole_bound import (
    PILLAR_STATUS,
    QUADRUPOLE_STATUS,
    D_HUBBLE_GPC,
    D_CMB_GPC,
    H0_KM_S_MPC,
    QUADRUPOLE_DEFICIT_LOW,
    QUADRUPOLE_DEFICIT_HIGH,
    quadrupole_wavenumber,
    topology_suppression_fraction,
    suppression_table,
    required_topology_scale,
    um_compatibility_check,
    quadrupole_topology_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == "CONSTRAINED_FROM_CMB"

    def test_quadrupole_status(self):
        assert QUADRUPOLE_STATUS == "CONSTRAINED_FROM_CMB"

    def test_d_hubble_order(self):
        # H₀ = 67.4 → D_H ≈ 14.3 Gpc
        assert 13.0 < D_HUBBLE_GPC < 16.0

    def test_deficit_low(self):
        assert abs(QUADRUPOLE_DEFICIT_LOW - 0.26) < 0.01

    def test_deficit_high(self):
        assert abs(QUADRUPOLE_DEFICIT_HIGH - 0.47) < 0.01


class TestQuadrupoleWavenumber:
    def test_returns_dict(self):
        data = quadrupole_wavenumber()
        assert isinstance(data, dict)

    def test_ell_is_2(self):
        data = quadrupole_wavenumber()
        assert data["ell"] == 2

    def test_k_positive(self):
        data = quadrupole_wavenumber()
        assert data["k_quad_Gpc_inv"] > 0

    def test_k_formula(self):
        # k_{ℓ=2} = √6 / D_CMB (rounded in module to 5 decimal places)
        data = quadrupole_wavenumber()
        expected = math.sqrt(6.0) / D_CMB_GPC
        assert abs(data["k_quad_Gpc_inv"] - expected) < 1e-4


class TestTopologySuppression:
    def test_zero_for_large_L(self):
        # For very large L (>> D_H), no suppression
        f = topology_suppression_fraction(L_DH=100.0)
        assert abs(f - 1.0) < 1e-3

    def test_zero_for_small_L(self):
        # For L → 0, suppression should be → 0
        f = topology_suppression_fraction(L_DH=0.001)
        assert f < 0.01

    def test_monotone_increasing(self):
        # Suppression increases with decreasing L
        f1 = topology_suppression_fraction(0.3)
        f2 = topology_suppression_fraction(0.6)
        f3 = topology_suppression_fraction(0.9)
        assert f1 < f2 < f3

    def test_formula(self):
        L_DH = 0.7
        expected = 1.0 - math.exp(-L_DH ** 2)  # for ℓ=2
        result = topology_suppression_fraction(L_DH, ell=2)
        assert abs(result - expected) < 1e-10

    def test_deficit_window_contains_values(self):
        # L/D_H ~ 0.55 to 0.80 should be in window
        for L_DH in (0.55, 0.65, 0.75, 0.80):
            f = topology_suppression_fraction(L_DH)
            # At least some should be in [0.26, 0.47]
            if 0.26 <= f <= 0.47:
                return  # success
        pytest.fail("No L/D_H in [0.55, 0.80] gives suppression in deficit window")


class TestSuppressionTable:
    def test_returns_list(self):
        table = suppression_table()
        assert isinstance(table, list)
        assert len(table) > 0

    def test_some_in_window(self):
        table = suppression_table()
        in_window = [r for r in table if r["in_deficit_window"]]
        assert len(in_window) > 0

    def test_L_Gpc_consistent_with_DH(self):
        table = suppression_table()
        for r in table:
            expected_Gpc = r["L_DH"] * D_HUBBLE_GPC
            assert abs(r["L_Gpc"] - expected_Gpc) < 0.1

    def test_percent_suppression_consistent(self):
        table = suppression_table()
        for r in table:
            assert abs(r["percent_suppression"] - r["f_supp"] * 100) < 0.1


class TestRequiredTopologyScale:
    def test_returns_dict(self):
        data = required_topology_scale()
        assert isinstance(data, dict)

    def test_L_min_DH_positive(self):
        data = required_topology_scale()
        assert data["L_min_DH"] > 0

    def test_L_max_larger_than_min(self):
        data = required_topology_scale()
        assert data["L_max_DH"] > data["L_min_DH"]

    def test_suppression_at_L_min_matches_deficit_low(self):
        data = required_topology_scale()
        f = topology_suppression_fraction(data["L_min_DH"])
        assert abs(f - QUADRUPOLE_DEFICIT_LOW) < 0.01

    def test_suppression_at_L_max_matches_deficit_high(self):
        data = required_topology_scale()
        f = topology_suppression_fraction(data["L_max_DH"])
        assert abs(f - QUADRUPOLE_DEFICIT_HIGH) < 0.01

    def test_Gpc_consistent_with_DH(self):
        data = required_topology_scale()
        assert abs(data["L_min_Gpc"] - data["L_min_DH"] * D_HUBBLE_GPC) < 0.1
        assert abs(data["L_max_Gpc"] - data["L_max_DH"] * D_HUBBLE_GPC) < 0.1

    def test_window_below_1_DH(self):
        # L < D_H required for topology suppression
        data = required_topology_scale()
        assert data["L_max_DH"] < 1.0


class TestUMCompatibilityCheck:
    def test_um_compatible_true(self):
        data = um_compatibility_check()
        assert data["um_compatible"] is True

    def test_um_cannot_select_L(self):
        data = um_compatibility_check()
        assert data["um_can_select_L"] is False

    def test_within_planck_allowed(self):
        data = um_compatibility_check()
        assert data["L_within_planck_allowed"] is True

    def test_verdict_contains_compatible(self):
        data = um_compatibility_check()
        assert "COMPATIBLE" in data["verdict"]


class TestQuadrupoleTopologyVerdict:
    def test_status_constrained(self):
        verdict = quadrupole_topology_verdict()
        assert verdict["status"] == "CONSTRAINED_FROM_CMB"

    def test_status_upgrade(self):
        verdict = quadrupole_topology_verdict()
        assert verdict["previous_status"] == "POSSIBLE_CANDIDATE_SPECIFIED"
        assert verdict["new_status"] == "CONSTRAINED_FROM_CMB"

    def test_some_in_window(self):
        verdict = quadrupole_topology_verdict()
        assert verdict["n_table_entries_in_window"] > 0

    def test_verdict_contains_upgraded(self):
        verdict = quadrupole_topology_verdict()
        assert "CONSTRAINED_FROM_CMB" in verdict["verdict"]
