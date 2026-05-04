# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_inflation_as_5d.py
================================
Pillar 156 — Tests for inflation_as_5d.py.

Tests cover:
  - Constants: A_S_PLANCK, N_S_UM, R_UM, PI_KR, K_RS_GEV
  - rs_correction_function(): RS1 Brax-Bruck-Davis correction factor
  - slow_roll_from_um_predictions(): ε, η from UM r and n_s
  - rs_inflation_correction(): full RS correction to A_s
  - inflation_energy_scale_um(): H_inf from RS1 geometry with α
  - as_from_5d_geometry(): partial A_s derivation from 5D
  - cmb_suppression_diagnosis(): full CMB suppression diagnosis
  - pillar156_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.inflation_as_5d import (
    A_S_PLANCK,
    N_S_PLANCK,
    N_S_UM,
    R_UM,
    PI_KR,
    M_PLANCK_GEV,
    K_RS_GEV,
    WARP_FACTOR,
    LAMBDA_BRANE_NATURAL,
    CMB_SUPPRESSION_MIN,
    CMB_SUPPRESSION_MAX,
    RS_CORRECTION_REF,
    R_BICEP_KECK_BOUND,
    rs_correction_function,
    slow_roll_from_um_predictions,
    rs_inflation_correction,
    inflation_energy_scale_um,
    as_from_5d_geometry,
    cmb_suppression_diagnosis,
    pillar156_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_a_s_planck_order(self):
        """A_s ≈ 2.1×10⁻⁹"""
        assert 1e-9 < A_S_PLANCK < 1e-8

    def test_a_s_planck_value(self):
        assert abs(A_S_PLANCK - 2.1e-9) < 1e-11

    def test_n_s_planck_near_0_965(self):
        assert abs(N_S_PLANCK - 0.9649) < 1e-10

    def test_n_s_um_near_planck(self):
        """UM n_s = 0.9635 is within 1σ of Planck."""
        assert abs(N_S_UM - 0.9635) < 1e-10

    def test_r_um_positive(self):
        assert R_UM > 0

    def test_r_um_below_bicep(self):
        assert R_UM < R_BICEP_KECK_BOUND

    def test_pi_kr_is_37(self):
        assert abs(PI_KR - 37.0) < 1e-10

    def test_k_rs_gev_is_m_planck(self):
        assert abs(K_RS_GEV - M_PLANCK_GEV) < 1.0

    def test_warp_factor_is_exp_minus_37(self):
        assert abs(WARP_FACTOR - math.exp(-37.0)) < 1e-20

    def test_lambda_brane_natural_is_6(self):
        assert abs(LAMBDA_BRANE_NATURAL - 6.0) < 1e-10

    def test_suppression_min_positive(self):
        assert CMB_SUPPRESSION_MIN > 1.0

    def test_suppression_range_valid(self):
        assert CMB_SUPPRESSION_MIN < CMB_SUPPRESSION_MAX

    def test_rs_ref_nonempty(self):
        assert len(RS_CORRECTION_REF) > 10

    def test_r_bicep_keck_bound_positive(self):
        assert R_BICEP_KECK_BOUND > 0


# ---------------------------------------------------------------------------
# rs_correction_function
# ---------------------------------------------------------------------------

class TestRSCorrectionFunction:
    def test_x_zero_gives_unity(self):
        """F_RS(0) = 1 (no correction)."""
        assert abs(rs_correction_function(0.0) - 1.0) < 1e-15

    def test_x_positive_gives_f_rs_above_1(self):
        """F_RS(x) > 1 for x > 0 (RS correction enhances A_s)."""
        assert rs_correction_function(0.1) > 1.0

    def test_x_small_near_unity(self):
        """F_RS(x) ≈ 1 + x/2 for small x."""
        x = 1e-4
        expected = 1.0 + x / 2.0
        assert abs(rs_correction_function(x) - expected) < 1e-6

    def test_f_rs_increases_with_x(self):
        """F_RS is monotonically increasing."""
        x_values = [0.01, 0.1, 1.0, 10.0]
        f_values = [rs_correction_function(x) for x in x_values]
        for i in range(len(f_values) - 1):
            assert f_values[i] < f_values[i + 1]

    def test_x_equals_1_specific(self):
        """F_RS(1) = 1 + 1/2 = 1.5."""
        assert abs(rs_correction_function(1.0) - 1.5) < 1e-10

    def test_large_x_gives_large_f_rs(self):
        """Large x → F_RS >> 1 (strongly RS-modified inflation)."""
        assert rs_correction_function(100.0) > 10.0

    def test_negative_x_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            rs_correction_function(-0.1)

    def test_returns_float(self):
        assert isinstance(rs_correction_function(0.5), float)


# ---------------------------------------------------------------------------
# slow_roll_from_um_predictions
# ---------------------------------------------------------------------------

class TestSlowRollFromUMPredictions:
    def setup_method(self):
        self.result = slow_roll_from_um_predictions()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_epsilon_is_r_over_16(self):
        assert abs(self.result["epsilon"] - R_UM / 16.0) < 1e-12

    def test_epsilon_small(self):
        """ε << 1 (slow roll required for inflation)."""
        assert self.result["epsilon"] < 0.01

    def test_eta_small(self):
        """|η| << 1 (slow roll)."""
        assert abs(self.result["eta"]) < 0.1

    def test_h_inf_over_mpl_very_small(self):
        """H_inf << M_Pl (sub-Planckian inflation)."""
        assert self.result["h_inf_over_mpl"] < 0.01

    def test_h_inf_gev_positive(self):
        assert self.result["h_inf_gev"] > 0

    def test_slow_roll_valid(self):
        assert self.result["slow_roll_valid"] is True

    def test_r_consistent_with_bicep(self):
        assert self.result["r_consistent_with_bicep"] is True

    def test_n_s_consistent_with_planck(self):
        """n_s = 0.9635 is within 3σ of Planck 0.9649 ± 0.0042."""
        assert self.result["n_s_consistent_with_planck"] is True

    def test_formula_string_nonempty(self):
        assert len(self.result["formula"]) > 10

    def test_note_nonempty(self):
        assert len(self.result["note"]) > 20

    def test_invalid_r_raises(self):
        with pytest.raises(ValueError, match="positive"):
            slow_roll_from_um_predictions(r_um=0.0)

    def test_invalid_n_s_raises(self):
        with pytest.raises(ValueError, match="positive"):
            slow_roll_from_um_predictions(n_s_um=0.0)

    def test_v_inf_gev_positive(self):
        assert self.result["v_inf_gev"] > 0


# ---------------------------------------------------------------------------
# rs_inflation_correction
# ---------------------------------------------------------------------------

class TestRSInflationCorrection:
    def test_returns_dict(self):
        result = rs_inflation_correction(1e-5)
        assert isinstance(result, dict)

    def test_small_h_gives_f_rs_near_1(self):
        """H_inf << k_RS → F_RS ≈ 1."""
        result = rs_inflation_correction(1e-10)
        assert abs(result["f_rs"] - 1.0) < 1e-15

    def test_f_rs_at_least_1(self):
        """RS correction always enhances (F_RS ≥ 1)."""
        for h_ratio in [1e-10, 1e-5, 0.01, 0.1]:
            result = rs_inflation_correction(h_ratio)
            assert result["f_rs"] >= 1.0

    def test_enhancement_positive(self):
        result = rs_inflation_correction(0.1)
        assert result["enhancement_pct"] >= 0

    def test_rs_direction_enhancement(self):
        result = rs_inflation_correction(0.01)
        assert "ENHANCEMENT" in result["rs_correction_direction"]

    def test_cannot_explain_suppression(self):
        """RS1 correction cannot suppress A_s → cannot explain CMB problem."""
        for h_ratio in [1e-5, 0.01, 0.1]:
            result = rs_inflation_correction(h_ratio)
            assert result["can_rs_explain_suppression"] is False

    def test_ratio_to_planck_at_exact_bd(self):
        """When using Planck A_s as A_s^{BD}, ratio = F_RS ≥ 1."""
        result = rs_inflation_correction(1e-10)
        assert abs(result["ratio_a_s_rs_to_planck"] - 1.0) < 1e-10

    def test_conclusion_nonempty(self):
        result = rs_inflation_correction(0.01)
        assert len(result["conclusion"]) > 50

    def test_reference_nonempty(self):
        result = rs_inflation_correction(0.01)
        assert len(result["reference"]) > 10

    def test_invalid_h_ratio_raises(self):
        with pytest.raises(ValueError, match="positive"):
            rs_inflation_correction(0.0)

    def test_epsilon_stored(self):
        result = rs_inflation_correction(0.01)
        assert abs(result["epsilon"] - R_UM / 16.0) < 1e-12


# ---------------------------------------------------------------------------
# inflation_energy_scale_um
# ---------------------------------------------------------------------------

class TestInflationEnergyScaleUM:
    def test_returns_dict(self):
        result = inflation_energy_scale_um()
        assert isinstance(result, dict)

    def test_h_inf_over_mpl_positive(self):
        result = inflation_energy_scale_um(1.0 / 6.0)
        assert result["h_inf_over_mpl"] > 0

    def test_h_inf_over_mpl_less_than_1(self):
        """H_inf < M_Pl (sub-Planckian)."""
        result = inflation_energy_scale_um(1.0 / 6.0)
        assert result["h_inf_over_mpl"] < 1.0

    def test_h_inf_decreases_with_larger_alpha(self):
        """Larger α → more warp suppression → smaller H_inf."""
        r1 = inflation_energy_scale_um(0.1)
        r2 = inflation_energy_scale_um(0.5)
        assert r1["h_inf_over_mpl"] > r2["h_inf_over_mpl"]

    def test_alpha_1_gives_ew_scale(self):
        """α = 1: H_inf ≈ M_Pl × e^{-37} ~ 10⁻¹⁶ M_Pl (EW scale)."""
        result = inflation_energy_scale_um(1.0)
        assert result["h_inf_over_mpl"] < 1e-10

    def test_a_s_5d_finite(self):
        result = inflation_energy_scale_um(1.0 / 6.0)
        assert math.isfinite(result["a_s_5d_predicted"])

    def test_a_s_5d_positive(self):
        result = inflation_energy_scale_um(1.0 / 6.0)
        assert result["a_s_5d_predicted"] > 0

    def test_f_rs_at_least_1(self):
        result = inflation_energy_scale_um(1.0 / 6.0)
        assert result["f_rs"] >= 1.0

    def test_note_nonempty(self):
        result = inflation_energy_scale_um(1.0 / 6.0)
        assert len(result["note"]) > 30

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError, match="positive"):
            inflation_energy_scale_um(0.0)

    def test_exponent_is_negative_alpha_pi_kr(self):
        alpha = 0.3
        result = inflation_energy_scale_um(alpha)
        expected_exp = -alpha * PI_KR
        assert abs(result["exponent"] - expected_exp) < 1e-10


# ---------------------------------------------------------------------------
# as_from_5d_geometry
# ---------------------------------------------------------------------------

class TestAsFrom5DGeometry:
    def setup_method(self):
        self.result = as_from_5d_geometry()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_alpha_gw_stored(self):
        assert abs(self.result["alpha_gw"] - 1.0 / 6.0) < 1e-10

    def test_a_s_5d_predicted_positive(self):
        assert self.result["a_s_5d_predicted"] > 0

    def test_partial_closure_true(self):
        assert self.result["partial_closure"] is True

    def test_rs_direction_identified(self):
        assert self.result["rs_direction_identified"] is True

    def test_rs_enhancement_only(self):
        assert self.result["rs_enhancement_only"] is True

    def test_alpha_for_planck_as_positive(self):
        """The α needed to give Planck A_s should be a reasonable positive value."""
        alpha = self.result["alpha_for_planck_as"]
        assert alpha > 0

    def test_open_problem_nonempty(self):
        assert len(self.result["open_problem"]) > 50

    def test_conclusion_contains_partial(self):
        assert "PARTIAL" in self.result["conclusion"]

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError, match="positive"):
            as_from_5d_geometry(alpha_gw=-0.1)

    def test_ratio_to_planck_finite(self):
        assert math.isfinite(self.result["ratio_to_planck"])


# ---------------------------------------------------------------------------
# cmb_suppression_diagnosis
# ---------------------------------------------------------------------------

class TestCMBSuppressionDiagnosis:
    def setup_method(self):
        self.result = cmb_suppression_diagnosis()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_156(self):
        assert self.result["pillar"] == 156

    def test_status_partially_closed(self):
        assert "PARTIAL" in self.result["status"]

    def test_suppression_factor_nonempty(self):
        assert len(self.result["suppression_factor_observed"]) > 0

    def test_slow_roll_present(self):
        sr = self.result["step_1_slow_roll"]
        assert "epsilon" in sr
        assert "eta" in sr

    def test_rs_correction_present(self):
        rs = self.result["step_2_rs_correction_alpha_1_6"]
        assert "f_rs" in rs

    def test_rs_enhances_not_suppresses(self):
        assert self.result["rs_enhances_not_suppresses"] is True

    def test_rs_correction_insufficient(self):
        assert self.result["rs_correction_insufficient"] is True

    def test_root_cause_nonempty(self):
        assert len(self.result["root_cause"]) > 30

    def test_partial_closure_list_nonempty(self):
        assert len(self.result["partial_closure_achieved"]) >= 3

    def test_remaining_open_list_nonempty(self):
        assert len(self.result["remaining_open"]) >= 2

    def test_path_to_resolution_nonempty(self):
        assert len(self.result["path_to_full_resolution"]) > 30

    def test_reference_pillars_nonempty(self):
        assert len(self.result["reference_pillars"]) >= 3

    def test_alpha_needed_positive(self):
        assert self.result["step_4_alpha_for_planck_as"] > 0


# ---------------------------------------------------------------------------
# pillar156_summary
# ---------------------------------------------------------------------------

class TestPillar156Summary:
    def setup_method(self):
        self.result = pillar156_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_156(self):
        assert self.result["pillar"] == 156

    def test_title_nonempty(self):
        assert len(self.result["title"]) > 10

    def test_new_status_partial(self):
        assert "PARTIAL" in self.result["new_status"]

    def test_a_s_planck_stored(self):
        assert abs(self.result["a_s_planck"] - A_S_PLANCK) < 1e-15

    def test_n_s_um_stored(self):
        assert abs(self.result["n_s_um"] - N_S_UM) < 1e-10

    def test_r_um_stored(self):
        assert abs(self.result["r_um"] - R_UM) < 1e-10

    def test_epsilon_um_is_r_over_16(self):
        assert abs(self.result["epsilon_um"] - R_UM / 16.0) < 1e-12

    def test_eta_um_finite(self):
        assert math.isfinite(self.result["eta_um"])

    def test_f_rs_at_default_alpha_near_1(self):
        """At default α = 1/6, F_RS should be very close to 1."""
        f = self.result["f_rs_at_default_alpha"]
        assert 1.0 <= f <= 2.0

    def test_rs_correction_pct_non_negative(self):
        assert self.result["rs_correction_pct"] >= 0

    def test_rs_enhances_not_suppresses_true(self):
        assert self.result["rs_enhances_not_suppresses"] is True

    def test_rs_cannot_explain_cmb_suppression_true(self):
        assert self.result["rs_can_explain_cmb_suppression"] is False

    def test_alpha_needed_positive(self):
        assert self.result["alpha_needed_for_planck_as"] > 0

    def test_partial_closure_true(self):
        assert self.result["partial_closure"] is True

    def test_partial_closure_items_nonempty(self):
        assert len(self.result["partial_closure_items"]) >= 3

    def test_remaining_open_nonempty(self):
        assert len(self.result["remaining_open"]) >= 2

    def test_root_cause_nonempty(self):
        assert len(self.result["root_cause"]) > 30

    def test_open_problem_nonempty(self):
        assert len(self.result["open_problem"]) > 50

    def test_pillar_references_nonempty(self):
        assert len(self.result["pillar_references"]) >= 3
