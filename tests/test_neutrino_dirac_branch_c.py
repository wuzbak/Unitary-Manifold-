# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_dirac_branch_c.py
========================================
Pillar 157 — Tests for neutrino_dirac_branch_c.py.

Tests cover:
  - Constants: PI_KR, C_R_THEOREM, C_L_MIN_PLANCK, M_NU_ATMOSPHERIC_EV
  - rs_profile_uv(): UV-localised RS zero-mode profile
  - rs_profile_ir(): IR-localised RS zero-mode profile
  - dirac_neutrino_mass_ev(): 4D Dirac mass from wavefunction overlap
  - solve_c_r_for_target_mass(): binary search for c_R
  - branch_c_analysis(): full Branch C analysis
  - branch_c_vs_theorem(): comparison with orbifold fixed-point c_R = 23/25
  - pillar157_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.neutrino_dirac_branch_c import (
    PI_KR,
    C_R_THEOREM,
    C_L_MIN_PLANCK,
    HIGGS_VEV_GEV,
    PLANCK_SUM_MNU_EV,
    PLANCK_PER_SPECIES_EV,
    M_NU_ATMOSPHERIC_EV,
    GEV_TO_EV,
    Y5_DEFAULT,
    rs_profile_uv,
    rs_profile_ir,
    dirac_neutrino_mass_ev,
    solve_c_r_for_target_mass,
    branch_c_analysis,
    branch_c_vs_theorem,
    pillar157_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_pi_kr_is_37(self):
        assert abs(PI_KR - 37.0) < 1e-10

    def test_c_r_theorem_is_23_over_25(self):
        assert abs(C_R_THEOREM - 23.0 / 25.0) < 1e-12

    def test_c_r_theorem_is_0_920(self):
        assert abs(C_R_THEOREM - 0.920) < 1e-6

    def test_c_l_min_planck_is_0_88(self):
        assert abs(C_L_MIN_PLANCK - 0.88) < 1e-10

    def test_higgs_vev_order(self):
        assert 245.0 < HIGGS_VEV_GEV < 247.0

    def test_planck_sum_mnu_is_0_12(self):
        assert abs(PLANCK_SUM_MNU_EV - 0.12) < 1e-10

    def test_planck_per_species_is_sum_over_3(self):
        assert abs(PLANCK_PER_SPECIES_EV - 0.04) < 0.001

    def test_atmospheric_mass_50_mev(self):
        assert abs(M_NU_ATMOSPHERIC_EV - 0.050) < 1e-10

    def test_gev_to_ev_is_1e9(self):
        assert abs(GEV_TO_EV - 1.0e9) < 1.0

    def test_y5_default_is_1(self):
        assert abs(Y5_DEFAULT - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# rs_profile_uv
# ---------------------------------------------------------------------------

class TestRSProfileUV:
    def test_returns_positive_float(self):
        assert rs_profile_uv(0.920) > 0

    def test_c_r_theorem_profile(self):
        """c_R = 23/25 = 0.920 is strongly UV-localised → very small IR profile."""
        f0 = rs_profile_uv(0.920)
        assert f0 < 1e-5

    def test_c_close_to_0_5_larger_profile(self):
        """c close to 0.5 → less UV-localised → larger f₀."""
        f0_near = rs_profile_uv(0.51)
        f0_far = rs_profile_uv(0.90)
        assert f0_near > f0_far

    def test_profile_decreases_with_c(self):
        """f₀ should decrease as c increases (more UV-localised → smaller IR profile)."""
        c_values = [0.55, 0.65, 0.75, 0.85, 0.95]
        profiles = [rs_profile_uv(c) for c in c_values]
        for i in range(len(profiles) - 1):
            assert profiles[i] > profiles[i + 1]

    def test_profile_at_0_88(self):
        """c_L = 0.88 → f₀ should be of order 10⁻⁷."""
        f0 = rs_profile_uv(0.88)
        assert 1e-9 < f0 < 1e-5

    def test_invalid_c_equal_0_5_raises(self):
        with pytest.raises(ValueError, match="≤ 0.5"):
            rs_profile_uv(0.5)

    def test_invalid_c_below_0_5_raises(self):
        with pytest.raises(ValueError, match="≤ 0.5"):
            rs_profile_uv(0.3)

    def test_large_c_no_overflow(self):
        """c = 0.999 should not raise OverflowError."""
        f0 = rs_profile_uv(0.999)
        assert math.isfinite(f0)
        assert f0 > 0

    def test_profile_formula_consistency(self):
        """Verify f₀² = (2c-1) / (exp((2c-1)*πkR) - 1) for moderate c."""
        c = 0.60
        x = (2 * c - 1) * PI_KR  # x = 0.2 * 37 = 7.4 (not too large)
        expected = math.sqrt((2 * c - 1) / (math.exp(x) - 1))
        assert abs(rs_profile_uv(c) - expected) < 1e-12


# ---------------------------------------------------------------------------
# rs_profile_ir
# ---------------------------------------------------------------------------

class TestRSProfileIR:
    def test_returns_positive_float(self):
        assert rs_profile_ir(0.3) > 0

    def test_c_equal_0_not_exponentially_small(self):
        """c = 0 → IR-localised → f₀ not exponentially small."""
        f0 = rs_profile_ir(0.0)
        # For c=0: f₀ = √(1/(1-exp(-37))) ≈ 1
        assert f0 > 0.1

    def test_ir_profile_larger_than_uv_would_be(self):
        """IR profiles are NOT suppressed — they are O(1)."""
        f0_ir = rs_profile_ir(0.3)
        f0_uv = rs_profile_uv(0.7)  # UV-localised comparable c value
        assert f0_ir > f0_uv

    def test_invalid_c_at_0_5_raises(self):
        with pytest.raises(ValueError, match="≥ 0.5"):
            rs_profile_ir(0.5)

    def test_invalid_c_above_0_5_raises(self):
        with pytest.raises(ValueError, match="≥ 0.5"):
            rs_profile_ir(0.7)

    def test_invalid_negative_c_raises(self):
        with pytest.raises(ValueError, match="< 0"):
            rs_profile_ir(-0.1)

    def test_no_overflow_at_extremes(self):
        f0 = rs_profile_ir(0.01)
        assert math.isfinite(f0)


# ---------------------------------------------------------------------------
# dirac_neutrino_mass_ev
# ---------------------------------------------------------------------------

class TestDiracNeutrinoMassEV:
    def test_returns_positive_float(self):
        m = dirac_neutrino_mass_ev(0.88, 0.920)
        assert m > 0

    def test_mass_is_finite(self):
        m = dirac_neutrino_mass_ev(0.88, 0.920)
        assert math.isfinite(m)

    def test_mass_with_theorem_c_r_planck_consistent(self):
        """c_L = 0.88, c_R = 23/25 → mass should be well below 0.12 eV."""
        m = dirac_neutrino_mass_ev(C_L_MIN_PLANCK, C_R_THEOREM)
        assert m < PLANCK_SUM_MNU_EV

    def test_mass_scales_linearly_with_y5(self):
        """m_ν ∝ y_5."""
        m1 = dirac_neutrino_mass_ev(0.88, 0.920, y5=1.0)
        m2 = dirac_neutrino_mass_ev(0.88, 0.920, y5=2.0)
        assert abs(m2 / m1 - 2.0) < 0.01

    def test_mass_decreases_with_larger_c_l(self):
        """More UV-localised ν_L → smaller overlap → smaller mass."""
        m_low = dirac_neutrino_mass_ev(0.80, 0.920)
        m_high = dirac_neutrino_mass_ev(0.90, 0.920)
        assert m_low > m_high

    def test_mass_decreases_with_larger_c_r(self):
        """More UV-localised ν_R → smaller IR profile → smaller mass."""
        m_low = dirac_neutrino_mass_ev(0.88, 0.80)
        m_high = dirac_neutrino_mass_ev(0.88, 0.95)
        assert m_low > m_high

    def test_invalid_c_l_below_0_5_raises(self):
        with pytest.raises(ValueError, match="c_l"):
            dirac_neutrino_mass_ev(0.3, 0.920)

    def test_invalid_c_r_below_0_5_raises(self):
        with pytest.raises(ValueError, match="c_r"):
            dirac_neutrino_mass_ev(0.88, 0.3)

    def test_invalid_y5_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            dirac_neutrino_mass_ev(0.88, 0.920, y5=0.0)

    def test_invalid_higgs_vev_raises(self):
        with pytest.raises(ValueError, match="positive"):
            dirac_neutrino_mass_ev(0.88, 0.920, higgs_vev_gev=0.0)

    def test_mass_formula_consistency(self):
        """Manually verify m = y5 * v * f0(c_l) * f0(c_r) * 1e9 eV."""
        c_l, c_r = 0.88, 0.920
        f0_l = rs_profile_uv(c_l)
        f0_r = rs_profile_uv(c_r)
        expected_ev = 1.0 * HIGGS_VEV_GEV * f0_l * f0_r * GEV_TO_EV
        assert abs(dirac_neutrino_mass_ev(c_l, c_r) - expected_ev) < 1e-20


# ---------------------------------------------------------------------------
# solve_c_r_for_target_mass
# ---------------------------------------------------------------------------

class TestSolveC_RForTargetMass:
    def test_returns_float_in_valid_range(self):
        c_r = solve_c_r_for_target_mass(0.88, M_NU_ATMOSPHERIC_EV)
        assert 0.5 < c_r < 1.0

    def test_solution_recovers_target_mass(self):
        """The solved c_R should give a mass close to the target."""
        c_l = 0.88
        target = M_NU_ATMOSPHERIC_EV
        c_r = solve_c_r_for_target_mass(c_l, target)
        m_check = dirac_neutrino_mass_ev(c_l, c_r)
        # Should be within 1% of target
        assert abs(m_check / target - 1.0) < 0.01

    def test_larger_target_needs_smaller_c_r(self):
        """Larger target mass → smaller c_R (less UV-localised ν_R)."""
        c_l = 0.88
        c_r_50 = solve_c_r_for_target_mass(c_l, 0.050)
        c_r_10 = solve_c_r_for_target_mass(c_l, 0.010)
        assert c_r_50 < c_r_10

    def test_planck_boundary_target(self):
        """Target = Planck per-species limit (40 meV)."""
        c_r = solve_c_r_for_target_mass(0.88, PLANCK_PER_SPECIES_EV)
        assert 0.5 < c_r < 1.0

    def test_invalid_c_l_raises(self):
        with pytest.raises(ValueError, match="c_l"):
            solve_c_r_for_target_mass(0.3, 0.05)

    def test_invalid_target_mass_raises(self):
        with pytest.raises(ValueError, match="positive"):
            solve_c_r_for_target_mass(0.88, -0.05)

    def test_invalid_y5_raises(self):
        with pytest.raises(ValueError, match="positive"):
            solve_c_r_for_target_mass(0.88, 0.05, y5=-1.0)


# ---------------------------------------------------------------------------
# branch_c_analysis
# ---------------------------------------------------------------------------

class TestBranchCAnalysis:
    def setup_method(self):
        self.result = branch_c_analysis(C_L_MIN_PLANCK)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_branch_is_c(self):
        assert self.result["branch"] == "C"

    def test_c_l_stored(self):
        assert abs(self.result["c_l"] - C_L_MIN_PLANCK) < 1e-10

    def test_c_r_theorem_stored(self):
        assert abs(self.result["c_r_theorem"] - C_R_THEOREM) < 1e-12

    def test_f0_l_positive(self):
        assert self.result["f0_l"] > 0

    def test_f0_l_is_small(self):
        """f₀(c_L = 0.88) should be exponentially suppressed."""
        assert self.result["f0_l"] < 1e-5

    def test_mass_with_theorem_c_r_positive(self):
        assert self.result["m_nu_with_theorem_c_r_ev"] > 0

    def test_planck_consistent_with_theorem_c_r(self):
        """c_L = 0.88, c_R = 23/25 → should be Planck consistent."""
        assert self.result["planck_consistent_with_theorem_c_r"] is True

    def test_c_r_for_atmospheric_mass_in_range(self):
        assert 0.5 < self.result["c_r_for_atmospheric_mass"] < 1.0

    def test_mass_verify_close_to_50_mev(self):
        """Verification mass should be close to atmospheric scale."""
        assert abs(self.result["m_nu_verify_ev"] - M_NU_ATMOSPHERIC_EV) / M_NU_ATMOSPHERIC_EV < 0.01

    def test_delta_c_r_finite(self):
        assert math.isfinite(self.result["delta_c_r_from_theorem_atm"])

    def test_fine_tuning_pct_positive(self):
        assert self.result["fine_tuning_atm_pct"] > 0

    def test_verdict_viable(self):
        assert "VIABLE" in self.result["verdict"]

    def test_conclusion_nonempty(self):
        assert len(self.result["conclusion"]) > 50

    def test_invalid_c_l_raises(self):
        with pytest.raises(ValueError, match="c_l"):
            branch_c_analysis(0.3)

    def test_different_c_l_values(self):
        """Branch C analysis at various c_L values."""
        for c_l in [0.85, 0.90, 0.95]:
            result = branch_c_analysis(c_l)
            assert result["branch"] == "C"
            assert result["f0_l"] > 0
            assert result["m_nu_with_theorem_c_r_ev"] > 0


# ---------------------------------------------------------------------------
# branch_c_vs_theorem
# ---------------------------------------------------------------------------

class TestBranchCVsTheorem:
    def setup_method(self):
        self.result = branch_c_vs_theorem()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_c_r_theorem_stored(self):
        assert abs(self.result["c_r_theorem"] - C_R_THEOREM) < 1e-12

    def test_scan_results_nonempty(self):
        assert len(self.result["scan_results"]) > 0

    def test_scan_results_have_expected_keys(self):
        for r in self.result["scan_results"]:
            assert "c_l" in r
            assert "c_r_for_50meV" in r
            assert "delta_c_r" in r
            assert "fine_tuning_pct" in r

    def test_c_r_for_50mev_in_valid_range(self):
        for r in self.result["scan_results"]:
            assert 0.5 < r["c_r_for_50meV"] < 1.0

    def test_fine_tuning_pct_positive(self):
        for r in self.result["scan_results"]:
            assert r["fine_tuning_pct"] > 0

    def test_closest_match_key_present(self):
        assert "closest_match" in self.result
        assert self.result["closest_match"]["c_l"] > 0

    def test_summary_nonempty(self):
        assert len(self.result["summary"]) > 50

    def test_comparison_to_branch_b_nonempty(self):
        assert len(self.result["comparison_to_branch_b"]) > 30

    def test_consistent_with_theorem_flag_is_bool(self):
        assert isinstance(self.result["consistent_with_theorem_at_any_cl"], bool)


# ---------------------------------------------------------------------------
# pillar157_summary
# ---------------------------------------------------------------------------

class TestPillar157Summary:
    def setup_method(self):
        self.result = pillar157_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_157(self):
        assert self.result["pillar"] == 157

    def test_title_nonempty(self):
        assert len(self.result["title"]) > 10

    def test_new_status_analysed(self):
        assert "ANALYSED" in self.result["new_status"] or "VIABLE" in self.result["new_status"]

    def test_branch_is_c(self):
        assert self.result["branch"] == "C"

    def test_c_l_minimum_planck(self):
        assert abs(self.result["c_l_minimum_planck"] - C_L_MIN_PLANCK) < 1e-10

    def test_c_r_theorem_stored(self):
        assert abs(self.result["c_r_theorem"] - C_R_THEOREM) < 1e-12

    def test_c_r_for_50mev_in_range(self):
        assert 0.5 < self.result["c_r_for_50meV_at_cl088"] < 1.0

    def test_delta_c_r_finite(self):
        assert math.isfinite(self.result["delta_c_r"])

    def test_fine_tuning_pct_small_but_nonzero(self):
        """Fine-tuning should be small (~1%) but not zero."""
        pct = self.result["fine_tuning_pct"]
        assert 0 < pct < 10.0

    def test_planck_consistent_with_theorem_cr(self):
        assert self.result["planck_consistent_with_theorem_cr"] is True

    def test_branch_c_viable_true(self):
        assert self.result["branch_c_viable"] is True

    def test_branch_c_disfavoured_true(self):
        assert self.result["branch_c_disfavoured"] is True

    def test_branch_b_preferred_true(self):
        assert self.result["branch_b_preferred"] is True

    def test_reasons_disfavoured_nonempty(self):
        assert len(self.result["reasons_disfavoured"]) >= 3

    def test_conclusion_nonempty(self):
        assert len(self.result["conclusion"]) > 80

    def test_pillar_references_nonempty(self):
        assert len(self.result["pillar_references"]) >= 3

    def test_comparison_to_branch_b_nonempty(self):
        assert len(self.result["comparison_to_branch_b"]) > 30
