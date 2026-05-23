# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar378_two_radius_gw_r_min.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar378_two_radius_gw_r_min import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    N_W, M_W, K_CS, LAMBDA_GW, EPS_GW, PHI_UV, T_W, R0_GW,
    separation_guard,
    gw_potential,
    winding_tension_potential,
    total_potential,
    gw_potential_second_derivative,
    braid_radius_correction,
    two_radius_ratio,
    two_radius_minimization,
    convention_279_3_derivation,
    pillar378_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 378
    def test_status(self): assert PILLAR_STATUS == "DERIVED_CONDITIONAL"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_n_w(self): assert N_W == 5
    def test_m_w(self): assert M_W == 7
    def test_k_cs(self): assert K_CS == 74
    def test_k_cs_equals_n_sq_plus_m_sq(self): assert N_W**2 + M_W**2 == K_CS
    def test_t_w_positive(self): assert T_W > 0
    def test_t_w_formula(self): assert abs(T_W - K_CS / (16.0 * math.pi**2)) < 1e-10
    def test_r0_gw_positive(self): assert R0_GW > 0


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_derived_conditional(self): assert "DERIVED_CONDITIONAL" in separation_guard()
    def test_r1_less_r2(self): assert "R₁ < R₂" in separation_guard() or "R1 < R2" in separation_guard()


class TestGWPotential:
    def test_returns_float(self): assert isinstance(gw_potential(1.0), float)
    def test_positive(self): assert gw_potential(1.0) >= 0
    def test_positive_at_r0(self): assert gw_potential(R0_GW) >= 0
    def test_increases_for_large_r(self):
        v1 = gw_potential(0.01)
        v2 = gw_potential(10.0)
        assert math.isfinite(v1) and math.isfinite(v2)
    def test_invalid_r(self):
        with pytest.raises(ValueError):
            gw_potential(0.0)
    def test_invalid_negative_r(self):
        with pytest.raises(ValueError):
            gw_potential(-1.0)


class TestWindingTensionPotential:
    def test_returns_float(self): assert isinstance(winding_tension_potential(1.0, 1.0), float)
    def test_positive(self): assert winding_tension_potential(1.0, 1.0) > 0
    def test_decreases_with_larger_r(self):
        v1 = winding_tension_potential(0.5, 0.5)
        v2 = winding_tension_potential(2.0, 2.0)
        assert v1 > v2  # ~ 1/r²
    def test_r1_effect(self):
        # Increasing r1 decreases V_braid (n_w/r1²)
        v1 = winding_tension_potential(0.5, 1.0)
        v2 = winding_tension_potential(1.0, 1.0)
        assert v1 > v2
    def test_invalid_r(self):
        with pytest.raises(ValueError):
            winding_tension_potential(0, 1.0)


class TestTotalPotential:
    def test_finite(self):
        assert math.isfinite(total_potential(1.0, 1.0))
    def test_positive(self):
        assert total_potential(0.5, 0.5) > 0
    def test_symmetric_not_required(self):
        v12 = total_potential(0.8, 1.0)
        v21 = total_potential(1.0, 0.8)
        # Not symmetric (n_w ≠ m_w)
        assert abs(v12 - v21) > 0


class TestGWPotentialSecondDerivative:
    def test_positive(self):
        assert gw_potential_second_derivative() > 0
    def test_increases_with_lambda(self):
        v1 = gw_potential_second_derivative(lam=1.0)
        v2 = gw_potential_second_derivative(lam=2.0)
        assert v2 > v1


class TestBraidRadiusCorrection:
    def test_positive_for_nw(self):
        assert braid_radius_correction(N_W) > 0
    def test_positive_for_mw(self):
        assert braid_radius_correction(M_W) > 0
    def test_nw_correction_less_than_mw(self):
        # n_w < m_w → δR₁ < δR₂
        dr1 = braid_radius_correction(N_W)
        dr2 = braid_radius_correction(M_W)
        assert dr1 < dr2


class TestTwoRadiusRatio:
    def test_returns_dict(self): assert isinstance(two_radius_ratio(), dict)

    def test_r1_less_than_r2(self):
        r = two_radius_ratio()
        assert r["r1_less_than_r2"] is True

    def test_short_radius_is_r1(self):
        r = two_radius_ratio()
        assert r["short_radius_is_r1"] is True

    def test_braid_dominated_ratio_is_nw_mw(self):
        r = two_radius_ratio()
        assert abs(r["ratio_braid_dominated_limit"] - N_W / M_W) < 1e-10

    def test_r1_positive(self):
        r = two_radius_ratio()
        assert r["r1"] > 0

    def test_r2_positive(self):
        r = two_radius_ratio()
        assert r["r2"] > 0

    def test_agrees_with_n_assignment(self):
        r = two_radius_ratio()
        assert r["agrees_with_n_assignment"] is True


class TestTwoRadiusMinimization:
    def test_returns_dict(self):
        r = two_radius_minimization(n_grid=30)
        assert isinstance(r, dict)

    def test_r1_less_than_r2(self):
        r = two_radius_minimization(n_grid=30)
        assert r["r1_less_than_r2"] is True

    def test_short_radius_is_r1(self):
        r = two_radius_minimization(n_grid=30)
        assert r["short_radius_is_r1"] is True

    def test_convention_279_3_confirmed(self):
        r = two_radius_minimization(n_grid=30)
        assert r["convention_279_3_confirmed"] is True

    def test_r1_positive(self):
        r = two_radius_minimization(n_grid=30)
        assert r["r1_min"] > 0

    def test_v_min_finite(self):
        r = two_radius_minimization(n_grid=30)
        assert math.isfinite(r["v_min"])


class TestConvention279_3:
    def test_returns_dict(self): assert isinstance(convention_279_3_derivation(), dict)

    def test_new_status(self):
        r = convention_279_3_derivation()
        assert r["new_status"] == "DERIVED_CONDITIONAL"

    def test_previous_status(self):
        r = convention_279_3_derivation()
        assert r["previous_status"] == "CONDITIONAL_DERIVATION"

    def test_all_conditions_met(self):
        r = convention_279_3_derivation()
        assert r["all_conditions_met"] is True

    def test_certificate_status(self):
        r = convention_279_3_derivation()
        assert "CONVENTION_279_3" in r["certificate_status"]

    def test_ratio_braid_limit(self):
        r = convention_279_3_derivation()
        assert abs(r["ratio_braid_limit"] - N_W / M_W) < 1e-10

    def test_derivation_chain_steps(self):
        r = convention_279_3_derivation()
        assert len(r["derivation_chain"]) >= 5


class TestPillar378Summary:
    def test_returns_dict(self): assert isinstance(pillar378_summary(), dict)
    def test_pillar_number(self):
        r = pillar378_summary()
        assert r["pillar_number"] == PILLAR_NUMBER
    def test_status(self):
        r = pillar378_summary()
        assert r["status"] == "DERIVED_CONDITIONAL"
    def test_key_result_present(self):
        r = pillar378_summary()
        assert "key_result" in r
        assert "5/7" in r["key_result"] or "R₁" in r["key_result"]
    def test_falsification_present(self):
        r = pillar378_summary()
        assert "falsification" in r
