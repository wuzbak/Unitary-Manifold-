# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_submm_gravity.py
===========================
Tests for src/core/submm_gravity.py — Pillar 108.
"""

import math
import pytest

from src.core.submm_gravity import (
    K_CS,
    WINDING_NUMBER,
    compactification_length_m,
    current_experiment_reach_m,
    experiment_sensitivity_ratio,
    gravity_deviation_yukawa,
    next_gen_target_m,
    submm_gravity_summary,
)

# ── compactification_length_m ─────────────────────────────────────────────────

class TestCompactificationLength:

    def test_positive(self):
        assert compactification_length_m() > 0.0

    def test_default_in_micron_range(self):
        l_c = compactification_length_m()
        assert 0.5e-6 <= l_c <= 10e-6

    def test_approx_1_79_micron(self):
        l_c = compactification_length_m()
        assert abs(l_c - 1.79e-6) < 0.2e-6

    def test_scales_inversely_with_mass(self):
        l1 = compactification_length_m(m_kk_mev=0.110e-6)
        l2 = compactification_length_m(m_kk_mev=0.220e-6)
        assert abs(l1 / l2 - 2.0) < 1e-10

    def test_larger_mass_shorter_length(self):
        assert compactification_length_m(0.5e-3) < compactification_length_m(0.1e-3)

    def test_raises_for_zero_mass(self):
        with pytest.raises((ValueError, ZeroDivisionError)):
            compactification_length_m(0.0)

    def test_raises_for_negative_mass(self):
        with pytest.raises(ValueError):
            compactification_length_m(-1e-3)

    def test_units_consistency(self):
        # ħc / M_KK in MeV should give metres
        hc = 197.3269804e-15   # MeV·m
        m  = 0.110e-6          # 110 meV = 0.110e-6 MeV
        expected = hc / m
        assert abs(compactification_length_m() - expected) < 1e-20

    def test_double_mass_halves_length(self):
        m0 = 0.110e-6
        l0 = compactification_length_m(m0)
        l1 = compactification_length_m(2 * m0)
        assert abs(l0 - 2 * l1) < 1e-20

    def test_returns_float(self):
        assert isinstance(compactification_length_m(), float)


# ── gravity_deviation_yukawa ──────────────────────────────────────────────────

class TestGravityDeviationYukawa:

    def test_positive_at_zero(self):
        assert gravity_deviation_yukawa(0.0) > 0.0

    def test_unity_at_r_zero_alpha1(self):
        assert abs(gravity_deviation_yukawa(0.0, alpha=1.0) - 1.0) < 1e-12

    def test_decays_with_distance(self):
        assert gravity_deviation_yukawa(1e-6) > gravity_deviation_yukawa(5e-6)

    def test_exponential_form(self):
        l_c = compactification_length_m()
        r = l_c
        expected = math.exp(-1.0)
        assert abs(gravity_deviation_yukawa(r) - expected) < 1e-10

    def test_alpha_scaling(self):
        r = 1e-6
        d1 = gravity_deviation_yukawa(r, alpha=1.0)
        d2 = gravity_deviation_yukawa(r, alpha=2.0)
        assert abs(d2 - 2.0 * d1) < 1e-15

    def test_large_r_small_deviation(self):
        assert gravity_deviation_yukawa(1e-3) < 1e-100

    def test_at_current_reach_small(self):
        # At 50 μm, deviation from ~2 μm KK should be negligible
        dev = gravity_deviation_yukawa(current_experiment_reach_m())
        assert dev < 1e-10

    def test_at_next_gen_target_nonnegligible(self):
        dev = gravity_deviation_yukawa(next_gen_target_m())
        assert dev > 0.0

    def test_raises_for_negative_r(self):
        with pytest.raises(ValueError):
            gravity_deviation_yukawa(-1e-6)

    def test_returns_float(self):
        assert isinstance(gravity_deviation_yukawa(1e-6), float)

    def test_alpha_zero_gives_zero(self):
        assert gravity_deviation_yukawa(1e-6, alpha=0.0) == 0.0

    def test_monotone_decrease(self):
        distances = [1e-7, 1e-6, 5e-6, 1e-5, 5e-5]
        devs = [gravity_deviation_yukawa(r) for r in distances]
        assert devs == sorted(devs, reverse=True)


# ── experiment reach functions ────────────────────────────────────────────────

class TestExperimentReach:

    def test_current_reach_positive(self):
        assert current_experiment_reach_m() > 0.0

    def test_current_reach_order_50_micron(self):
        assert abs(current_experiment_reach_m() - 50e-6) < 1e-9

    def test_next_gen_target_positive(self):
        assert next_gen_target_m() > 0.0

    def test_next_gen_target_order_2_micron(self):
        assert abs(next_gen_target_m() - 2e-6) < 1e-9

    def test_next_gen_smaller_than_current(self):
        assert next_gen_target_m() < current_experiment_reach_m()

    def test_current_reach_in_microns(self):
        assert 1e-6 < current_experiment_reach_m() < 1e-3

    def test_next_gen_below_10_microns(self):
        assert next_gen_target_m() < 10e-6


# ── experiment_sensitivity_ratio ──────────────────────────────────────────────

class TestSensitivityRatio:

    def test_positive(self):
        assert experiment_sensitivity_ratio() > 0.0

    def test_greater_than_one(self):
        # Current experiments cannot reach the prediction
        assert experiment_sensitivity_ratio() > 1.0

    def test_formula(self):
        expected = current_experiment_reach_m() / compactification_length_m()
        assert abs(experiment_sensitivity_ratio() - expected) < 1e-10

    def test_scales_with_mass(self):
        r1 = experiment_sensitivity_ratio(0.110e-6)
        r2 = experiment_sensitivity_ratio(0.220e-6)
        # Higher mass → shorter L_c → larger ratio
        assert r2 > r1

    def test_returns_float(self):
        assert isinstance(experiment_sensitivity_ratio(), float)


# ── submm_gravity_summary ─────────────────────────────────────────────────────

class TestSubmmGravitySummary:

    def test_returns_dict(self):
        assert isinstance(submm_gravity_summary(), dict)

    def test_required_keys(self):
        s = submm_gravity_summary()
        for key in ("L_c_microns", "current_reach_microns",
                    "next_gen_target_microns", "sensitivity_ratio",
                    "detectable_next_gen"):
            assert key in s

    def test_L_c_microns_in_range(self):
        s = submm_gravity_summary()
        assert 0.5 <= s["L_c_microns"] <= 10.0

    def test_current_reach_microns_value(self):
        s = submm_gravity_summary()
        assert abs(s["current_reach_microns"] - 50.0) < 0.1

    def test_next_gen_target_microns_value(self):
        s = submm_gravity_summary()
        assert abs(s["next_gen_target_microns"] - 2.0) < 0.1

    def test_sensitivity_ratio_greater_one(self):
        s = submm_gravity_summary()
        assert s["sensitivity_ratio"] > 1.0

    def test_detectable_next_gen_is_bool(self):
        s = submm_gravity_summary()
        assert isinstance(s["detectable_next_gen"], bool)

    def test_detectable_next_gen_true(self):
        # next_gen_target (2 μm) < L_c × 10 (≈ 18 μm)
        s = submm_gravity_summary()
        assert s["detectable_next_gen"] is True

    def test_consistent_with_functions(self):
        s = submm_gravity_summary()
        assert abs(s["L_c_microns"] - compactification_length_m() * 1e6) < 1e-10

    def test_no_none_values(self):
        s = submm_gravity_summary()
        for v in s.values():
            assert v is not None
