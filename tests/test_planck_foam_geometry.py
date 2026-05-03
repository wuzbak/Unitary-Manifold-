# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_planck_foam_geometry.py
====================================
Tests for Pillar 128 — Planck-Scale Discrete Geometry (Quantum Foam).

~55 tests covering: area spectrum quantization, area gap ratio,
foam-to-smooth transition, Immirzi analogue, and summary completeness.
"""

from __future__ import annotations

import math

import pytest

from src.core.planck_foam_geometry import (
    K_CS,
    N_W,
    L_PL_M,
    L_PL_M2,
    LQG_IMMIRZI,
    BRAID_N1,
    BRAID_N2,
    area_spectrum,
    minimum_area_quantum,
    foam_to_smooth_transition,
    immirzi_from_kcs,
    planck_foam_summary,
)


# ---------------------------------------------------------------------------
# TestConstants — 6 tests
# ---------------------------------------------------------------------------

class TestConstants:
    def test_k_cs_equals_74(self):
        assert K_CS == 74

    def test_n_w_equals_5(self):
        assert N_W == 5

    def test_k_cs_from_braid(self):
        assert BRAID_N1 ** 2 + BRAID_N2 ** 2 == K_CS

    def test_l_pl_positive(self):
        assert L_PL_M > 0

    def test_l_pl_order_of_magnitude(self):
        assert 1e-36 < L_PL_M < 1e-34

    def test_lqg_immirzi_positive(self):
        assert LQG_IMMIRZI > 0


# ---------------------------------------------------------------------------
# TestAreaSpectrum — 14 tests
# ---------------------------------------------------------------------------

class TestAreaSpectrum:
    def test_n1_returns_float(self):
        assert isinstance(area_spectrum(1), float)

    def test_n1_positive(self):
        assert area_spectrum(1) > 0

    def test_spectrum_linear_in_n(self):
        a1 = area_spectrum(1)
        a3 = area_spectrum(3)
        assert abs(a3 - 3 * a1) < 1e-80

    def test_spectrum_n1_formula(self):
        expected = 4 * math.pi * K_CS * L_PL_M2
        assert abs(area_spectrum(1) - expected) < 1e-80

    def test_spectrum_n5(self):
        assert abs(area_spectrum(5) - 5 * area_spectrum(1)) < 1e-80

    def test_spectrum_n10(self):
        assert abs(area_spectrum(10) - 10 * area_spectrum(1)) < 1e-80

    def test_spacing_uniform(self):
        for n in range(1, 10):
            delta = area_spectrum(n + 1) - area_spectrum(n)
            assert abs(delta - area_spectrum(1)) < 1e-80

    def test_n0_raises(self):
        with pytest.raises(ValueError):
            area_spectrum(0)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            area_spectrum(-1)

    def test_n100_scales_correctly(self):
        assert abs(area_spectrum(100) / area_spectrum(1) - 100) < 1e-10

    def test_area_units_order_m2(self):
        # A_1 ≈ 2.43e-68 m²
        a1 = area_spectrum(1)
        assert 1e-70 < a1 < 1e-65

    def test_area_increases_with_n(self):
        for n in range(1, 20):
            assert area_spectrum(n + 1) > area_spectrum(n)

    def test_ratio_consecutive(self):
        # A_{n+1} / A_n = (n+1)/n
        for n in range(1, 10):
            ratio = area_spectrum(n + 1) / area_spectrum(n)
            assert abs(ratio - (n + 1) / n) < 1e-12

    def test_n2_equals_twice_n1(self):
        assert abs(area_spectrum(2) - 2 * area_spectrum(1)) < 1e-80


# ---------------------------------------------------------------------------
# TestMinimumAreaQuantum — 8 tests
# ---------------------------------------------------------------------------

class TestMinimumAreaQuantum:
    def test_returns_float(self):
        assert isinstance(minimum_area_quantum(), float)

    def test_equals_area_spectrum_1(self):
        assert abs(minimum_area_quantum() - area_spectrum(1)) < 1e-80

    def test_positive(self):
        assert minimum_area_quantum() > 0

    def test_formula(self):
        expected = 4 * math.pi * K_CS * L_PL_M ** 2
        assert abs(minimum_area_quantum() - expected) < 1e-80

    def test_k_cs_factor(self):
        # Ratio A_min / (4π L_Pl²) = k_cs
        ratio = minimum_area_quantum() / (4 * math.pi * L_PL_M2)
        assert abs(ratio - K_CS) < 1e-6

    def test_larger_than_planck_area(self):
        assert minimum_area_quantum() > L_PL_M2

    def test_order_of_magnitude(self):
        a = minimum_area_quantum()
        assert 1e-70 < a < 1e-65

    def test_zero_free_parameters(self):
        s = planck_foam_summary()
        assert s["free_parameters"] == 0


# ---------------------------------------------------------------------------
# TestFoamToSmoothTransition — 12 tests
# ---------------------------------------------------------------------------

class TestFoamToSmoothTransition:
    def test_returns_dict(self):
        assert isinstance(foam_to_smooth_transition(), dict)

    def test_transition_scale_positive(self):
        t = foam_to_smooth_transition()
        assert t["transition_scale_m"] > 0

    def test_transition_scale_formula(self):
        t = foam_to_smooth_transition()
        expected = L_PL_M * math.sqrt(K_CS)
        assert abs(t["transition_scale_m"] - expected) < 1e-40

    def test_transition_above_planck_length(self):
        t = foam_to_smooth_transition()
        assert t["transition_scale_m"] > L_PL_M

    def test_transition_in_planck_lengths(self):
        t = foam_to_smooth_transition()
        assert abs(t["transition_scale_in_planck_lengths"] - math.sqrt(K_CS)) < 1e-10

    def test_self_consistent_true(self):
        assert foam_to_smooth_transition()["self_consistent"] is True

    def test_n_grains_positive(self):
        assert foam_to_smooth_transition()["n_grains_per_transition_area"] > 0

    def test_n_grains_equals_kcs(self):
        assert foam_to_smooth_transition()["n_grains_per_transition_area"] == K_CS

    def test_smoothness_ratio_less_than_1(self):
        t = foam_to_smooth_transition()
        assert t["smoothness_ratio_at_transition"] < 1.0

    def test_smoothness_ratio_formula(self):
        t = foam_to_smooth_transition()
        assert abs(t["smoothness_ratio_at_transition"] - 1 / math.sqrt(K_CS)) < 1e-12

    def test_minimum_area_consistent(self):
        t = foam_to_smooth_transition()
        assert abs(t["minimum_area_m2"] - minimum_area_quantum()) < 1e-80

    def test_has_description(self):
        t = foam_to_smooth_transition()
        assert isinstance(t["description"], str)
        assert len(t["description"]) > 0


# ---------------------------------------------------------------------------
# TestImmirziFromKcs — 10 tests
# ---------------------------------------------------------------------------

class TestImmirziFromKcs:
    def test_returns_dict(self):
        assert isinstance(immirzi_from_kcs(), dict)

    def test_gamma_eff_positive(self):
        assert immirzi_from_kcs()["gamma_eff"] > 0

    def test_gamma_eff_formula(self):
        d = immirzi_from_kcs()
        expected = K_CS / (2 * math.pi)
        assert abs(d["gamma_eff"] - expected) < 1e-10

    def test_gamma_eff_approx_value(self):
        # k_cs / (2π) ≈ 74 / 6.283 ≈ 11.78
        d = immirzi_from_kcs()
        assert 11.0 < d["gamma_eff"] < 13.0

    def test_distinguishable_from_lqg(self):
        d = immirzi_from_kcs()
        assert d["distinguishable_from_lqg"] is True

    def test_ratio_to_lqg_large(self):
        d = immirzi_from_kcs()
        assert d["ratio_um_to_lqg"] > 10.0

    def test_braid_pair_correct(self):
        d = immirzi_from_kcs()
        assert d["braid_pair"] == (5, 7)

    def test_kcs_identity_string(self):
        d = immirzi_from_kcs()
        assert "74" in d["k_cs_identity"]

    def test_free_parameters_zero(self):
        d = immirzi_from_kcs()
        assert d["free_parameters"] == 0

    def test_area_gap_um_larger_than_lqg(self):
        d = immirzi_from_kcs()
        assert d["area_gap_um_m2"] > d["area_gap_lqg_m2"]


# ---------------------------------------------------------------------------
# TestPlanckFoamSummary — 5 tests
# ---------------------------------------------------------------------------

class TestPlanckFoamSummary:
    def test_returns_dict(self):
        assert isinstance(planck_foam_summary(), dict)

    def test_pillar_number(self):
        assert planck_foam_summary()["pillar"] == 128

    def test_epistemic_status(self):
        assert planck_foam_summary()["epistemic_status"] == "PREDICTIVE"

    def test_spacing_equals_a_min(self):
        s = planck_foam_summary()
        assert s["spacing_equals_a_min"] is True

    def test_area_spectrum_5_entries(self):
        s = planck_foam_summary()
        assert len(s["area_spectrum_n1_to_5"]) == 5
