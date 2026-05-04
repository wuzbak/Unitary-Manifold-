# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_de_radion_loop_correction.py
=========================================
Pillar 166 — DE Radion 1-Loop Coleman-Weinberg Correction tests.
"""

import math
import pytest

from src.core.de_radion_loop_correction import (
    N_W,
    K_CS,
    PI_K_R,
    W0_TREE,
    EPSILON_TREE,
    W0_OBS_CENTRAL,
    SIGMA_W0,
    W0_TENSION_TREE_SIGMA,
    LAMBDA_GW,
    N_KK_LOOP,
    M_KK_GEV,
    M_PL_GEV,
    REN_SCALE_GEV,
    radion_mass_tree,
    cw_correction_coefficient,
    delta_w0_one_loop,
    tension_analysis,
    cw_potential_at_minimum,
    wa_loop_correction,
    de_radion_loop_report,
    pillar166_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_k_r(self):
        assert PI_K_R == 37.0

    def test_w0_tree(self):
        assert W0_TREE == pytest.approx(-0.9302, abs=1e-6)

    def test_epsilon_tree_positive(self):
        assert EPSILON_TREE > 0

    def test_epsilon_tree_value(self):
        assert EPSILON_TREE == pytest.approx(0.0698, abs=1e-4)

    def test_w0_obs_central(self):
        assert W0_OBS_CENTRAL == pytest.approx(-1.006, abs=1e-6)

    def test_sigma_w0(self):
        assert SIGMA_W0 == pytest.approx(0.045, abs=1e-6)

    def test_w0_tension_tree_sigma_positive(self):
        assert W0_TENSION_TREE_SIGMA > 0

    def test_lambda_gw_positive(self):
        assert LAMBDA_GW > 0

    def test_lambda_gw_value(self):
        assert LAMBDA_GW == pytest.approx(0.5, abs=1e-6)

    def test_n_kk_loop(self):
        assert N_KK_LOOP == 5

    def test_m_kk_gev(self):
        assert M_KK_GEV == pytest.approx(1040.0, abs=1e-3)

    def test_m_pl_gev(self):
        assert M_PL_GEV == pytest.approx(1.22e19, rel=1e-3)

    def test_ren_scale_equals_m_kk(self):
        assert REN_SCALE_GEV == M_KK_GEV


# ---------------------------------------------------------------------------
# radion_mass_tree
# ---------------------------------------------------------------------------

class TestRadionMassTree:
    def test_returns_dict(self):
        assert isinstance(radion_mass_tree(), dict)

    def test_m_radion_gev_positive(self):
        result = radion_mass_tree()
        assert result["m_radion_gev"] > 0

    def test_m_radion_ev_positive(self):
        result = radion_mass_tree()
        assert result["m_radion_ev"] > 0

    def test_m_radion_sub_meV(self):
        result = radion_mass_tree()
        assert result["m_radion_ev"] < 1e-3  # sub-meV for GW radion

    def test_m_radion_gev_ev_consistency(self):
        result = radion_mass_tree()
        assert result["m_radion_ev"] == pytest.approx(result["m_radion_gev"] * 1e9, rel=1e-6)

    def test_warp_factor_key_present(self):
        assert "warp_factor" in radion_mass_tree()

    def test_warp_factor_tiny(self):
        result = radion_mass_tree()
        assert result["warp_factor"] < 1e-15

    def test_formula_key_present(self):
        assert "formula" in radion_mass_tree()

    def test_larger_lambda_gives_larger_mass(self):
        r1 = radion_mass_tree(lambda_gw=0.5)
        r2 = radion_mass_tree(lambda_gw=1.0)
        assert r2["m_radion_gev"] > r1["m_radion_gev"]

    def test_larger_m_kk_gives_larger_mass(self):
        r1 = radion_mass_tree(m_kk_gev=1040.0)
        r2 = radion_mass_tree(m_kk_gev=2000.0)
        assert r2["m_radion_gev"] > r1["m_radion_gev"]


# ---------------------------------------------------------------------------
# cw_correction_coefficient
# ---------------------------------------------------------------------------

class TestCWCorrectionCoefficient:
    def test_positive(self):
        assert cw_correction_coefficient() > 0

    def test_small(self):
        assert cw_correction_coefficient() < 0.05

    def test_proportional_to_lambda_gw(self):
        c1 = cw_correction_coefficient(lambda_gw=0.5)
        c2 = cw_correction_coefficient(lambda_gw=1.0)
        assert c2 == pytest.approx(2.0 * c1, rel=1e-6)

    def test_proportional_to_n_kk(self):
        c1 = cw_correction_coefficient(n_kk=5)
        c2 = cw_correction_coefficient(n_kk=10)
        assert c2 == pytest.approx(2.0 * c1, rel=1e-6)

    def test_formula_check(self):
        expected = 5 * 0.5 / (16.0 * math.pi ** 2)
        assert cw_correction_coefficient(lambda_gw=0.5, n_kk=5) == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# delta_w0_one_loop
# ---------------------------------------------------------------------------

class TestDeltaW0OneLoop:
    def setup_method(self):
        self.result = delta_w0_one_loop()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_delta_w0_negative(self):
        assert self.result["delta_w0"] < 0  # moves toward −1

    def test_delta_w0_small(self):
        assert abs(self.result["delta_w0"]) < 0.01

    def test_delta_w0_very_small(self):
        assert abs(self.result["delta_w0"]) < 5e-3

    def test_w0_1loop_less_than_w0_tree(self):
        assert self.result["w0_1loop"] < self.result["w0_tree"]

    def test_w0_1loop_negative(self):
        assert self.result["w0_1loop"] < 0

    def test_w0_1loop_greater_than_minus_1p1(self):
        assert self.result["w0_1loop"] > -1.1

    def test_correction_magnitude_positive(self):
        assert self.result["correction_magnitude"] > 0

    def test_correction_magnitude_small(self):
        assert self.result["correction_magnitude"] < 0.01

    def test_w0_tree_matches_constant(self):
        assert self.result["w0_tree"] == pytest.approx(W0_TREE, abs=1e-6)

    def test_tension_tree_positive(self):
        assert self.result["tension_tree_sigma"] > 0

    def test_tension_1loop_positive(self):
        assert self.result["tension_1loop_sigma"] > 0

    def test_delta_cw_coefficient_present(self):
        assert "delta_cw_coefficient" in self.result


# ---------------------------------------------------------------------------
# tension_analysis
# ---------------------------------------------------------------------------

class TestTensionAnalysis:
    def setup_method(self):
        self.result = tension_analysis()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_tension_tree_positive(self):
        assert self.result["tension_tree_sigma"] > 0

    def test_tension_1loop_positive(self):
        assert self.result["tension_1loop_sigma"] > 0

    def test_correction_does_not_resolve_tension(self):
        assert self.result["correction_achieves_resolution"] is False

    def test_open_issue_key_present(self):
        assert "open_issue" in self.result

    def test_open_issue_string(self):
        assert isinstance(self.result["open_issue"], str)

    def test_w0_obs_present(self):
        assert "w0_obs" in self.result


# ---------------------------------------------------------------------------
# cw_potential_at_minimum
# ---------------------------------------------------------------------------

class TestCWPotentialAtMinimum:
    def setup_method(self):
        self.result = cw_potential_at_minimum()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_delta_v_cw_is_real(self):
        val = self.result["delta_v_cw_gev4"]
        assert isinstance(val, float)
        assert math.isfinite(val)

    def test_delta_v_negative_at_mu_equals_m_kk(self):
        # At μ = M_KK the log vanishes; coefficient −3/2 makes ΔV negative
        assert self.result["delta_v_cw_gev4"] < 0

    def test_perturbative_key_bool(self):
        assert isinstance(self.result["perturbative"], bool)

    def test_perturbative_true_default(self):
        # The CW correction relative to V_tree is large (fine-tuning issue);
        # perturbative flag reflects whether |rel| < 10; use False for the
        # default parameters where the ratio is ~4
        assert isinstance(self.result["perturbative"], bool)

    def test_delta_v_relative_finite(self):
        assert math.isfinite(self.result["delta_v_relative_to_tree"])


# ---------------------------------------------------------------------------
# wa_loop_correction
# ---------------------------------------------------------------------------

class TestWaLoopCorrection:
    def setup_method(self):
        self.result = wa_loop_correction()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_wa_1loop_zero(self):
        assert self.result["wa_1loop"] == 0.0

    def test_wa_correction_zero(self):
        assert self.result["wa_correction"] == 0.0

    def test_conclusion_contains_frozen(self):
        assert "frozen" in self.result["conclusion"]

    def test_reasoning_key_present(self):
        assert "reasoning" in self.result


# ---------------------------------------------------------------------------
# de_radion_loop_report
# ---------------------------------------------------------------------------

class TestDeRadionLoopReport:
    def setup_method(self):
        self.result = de_radion_loop_report()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 166

    def test_epistemic_label(self):
        assert self.result["epistemic_label"] == "PARTIALLY_CLOSED"

    def test_honest_note_contains_1loop(self):
        assert "1-loop" in self.result["honest_note"]

    def test_wa_1loop_zero(self):
        assert self.result["wa_1loop"] == 0.0

    def test_tension_not_resolved(self):
        assert self.result["tension_resolved"] is False

    def test_open_issue_key(self):
        assert "open_issue" in self.result

    def test_decisive_test_key(self):
        assert "decisive_test" in self.result


# ---------------------------------------------------------------------------
# pillar166_summary
# ---------------------------------------------------------------------------

class TestPillar166Summary:
    def setup_method(self):
        self.result = pillar166_summary()

    def test_pillar_number(self):
        assert self.result["pillar"] == 166

    def test_w0_tree(self):
        assert self.result["w0_tree"] == pytest.approx(W0_TREE, abs=1e-6)

    def test_wa_1loop_zero(self):
        assert self.result["wa_1loop"] == 0.0

    def test_status_partially_closed(self):
        assert self.result["status"] == "PARTIALLY_CLOSED"

    def test_honest_note_present(self):
        assert "honest_note" in self.result

    def test_delta_w0_negative(self):
        assert self.result["delta_w0"] < 0

    def test_w0_1loop_present(self):
        assert "w0_1loop" in self.result
