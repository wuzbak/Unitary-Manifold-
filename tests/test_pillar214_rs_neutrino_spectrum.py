# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar214_rs_neutrino_spectrum.py
============================================
Test suite for Pillar 214 — RS Dirac Neutrino Mass Spectrum from UM Geometry.

Tests cover:
  - All exported constants have the correct geometric values
  - Internal helper _f0 matches the RS zero-mode formula
  - RHN localisation parameters (leading, color-correction, per-generation)
  - Leading-order Dirac mass predictions (~37.7 meV each, sum < 120 meV)
  - Geometric splitting ratio n₁n₂+1 = 36 and 10% discrepancy with PDG
  - Planck self-consistency check (Σm_ν < 0.12 eV)
  - Full summary dict keys and values
  - Edge cases and parametrisation invariants

Theory: ThomasCory Walker-Pearson.
Code architecture and tests: GitHub Copilot (AI).
"""

import math
import pytest

from src.core.pillar214_rs_neutrino_spectrum import (
    # Constants
    N_W, N1_BRAID, N2_BRAID, K_CS, N_C, PI_KR,
    V_EW_EV, YUKAWA5,
    C_LNU_VALUES,
    SPLITTING_RATIO_GEO,
    PDG_DM2_21_EV2, PDG_DM2_31_EV2, PDG_RATIO,
    PLANCK_SUM_MNU_EV,
    # Functions
    _f0,
    c_rnu_leading,
    c_rnu_color_correction,
    c_rnu_generation,
    neutrino_masses_ev,
    neutrino_splittings,
    planck_constraint_check,
    pillar214_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def masses():
    return neutrino_masses_ev()


@pytest.fixture(scope="module")
def splittings():
    return neutrino_splittings()


@pytest.fixture(scope="module")
def planck():
    return planck_constraint_check()


@pytest.fixture(scope="module")
def summary():
    return pillar214_summary()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n1_braid(self):
        assert N1_BRAID == 5

    def test_n2_braid(self):
        assert N2_BRAID == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_v_ew_ev(self):
        assert V_EW_EV == pytest.approx(246.22e9, rel=1e-4)

    def test_yukawa5(self):
        assert YUKAWA5 == pytest.approx(1.0)

    def test_c_lnu_values_length(self):
        assert len(C_LNU_VALUES) == 3

    def test_c_lnu_values_first(self):
        assert C_LNU_VALUES[0] == pytest.approx(0.9)

    def test_c_lnu_values_second(self):
        assert C_LNU_VALUES[1] == pytest.approx(0.8)

    def test_c_lnu_values_third(self):
        assert C_LNU_VALUES[2] == pytest.approx(0.7)

    def test_c_lnu_values_decreasing(self):
        assert C_LNU_VALUES[0] > C_LNU_VALUES[1] > C_LNU_VALUES[2]

    def test_splitting_ratio_geo(self):
        assert SPLITTING_RATIO_GEO == pytest.approx(36.0)

    def test_splitting_ratio_geo_formula(self):
        assert SPLITTING_RATIO_GEO == pytest.approx(N1_BRAID * N2_BRAID + 1)

    def test_pdg_dm2_21(self):
        assert PDG_DM2_21_EV2 == pytest.approx(7.53e-5, rel=1e-3)

    def test_pdg_dm2_31(self):
        assert PDG_DM2_31_EV2 == pytest.approx(2.453e-3, rel=1e-3)

    def test_pdg_ratio_value(self):
        assert PDG_RATIO == pytest.approx(PDG_DM2_31_EV2 / PDG_DM2_21_EV2, rel=1e-6)

    def test_pdg_ratio_near_33(self):
        assert 30.0 < PDG_RATIO < 35.0

    def test_planck_bound(self):
        assert PLANCK_SUM_MNU_EV == pytest.approx(0.12)

    def test_kcs_from_braids(self):
        assert K_CS == N1_BRAID**2 + N2_BRAID**2

    def test_pi_kr_from_kcs(self):
        assert PI_KR == pytest.approx(K_CS / 2.0)


# ─────────────────────────────────────────────────────────────────────────────
# 2. _f0 helper
# ─────────────────────────────────────────────────────────────────────────────

class TestF0:
    def test_f0_positive(self):
        assert _f0(0.9) > 0.0

    def test_f0_ir_limit(self):
        assert _f0(0.5) == pytest.approx(1.0)

    def test_f0_below_half(self):
        assert _f0(0.3) == pytest.approx(1.0)

    def test_f0_decreasing_in_c(self):
        assert _f0(0.9) < _f0(0.8) < _f0(0.7)

    def test_f0_formula_at_09(self):
        c = 0.9
        expected = math.sqrt((2*c-1) / (math.exp((2*c-1)*37) - 1))
        assert _f0(c) == pytest.approx(expected, rel=1e-10)

    def test_f0_formula_at_08(self):
        c = 0.8
        expected = math.sqrt((2*c-1) / (math.exp((2*c-1)*37) - 1))
        assert _f0(c) == pytest.approx(expected, rel=1e-10)

    def test_f0_formula_at_07(self):
        c = 0.7
        expected = math.sqrt((2*c-1) / (math.exp((2*c-1)*37) - 1))
        assert _f0(c) == pytest.approx(expected, rel=1e-10)

    def test_f0_at_09_tiny(self):
        # f0(0.9) must be much less than 1
        assert _f0(0.9) < 1e-5

    def test_f0_at_07_larger_than_09(self):
        # factor > 100 between f0(0.7) and f0(0.9)
        assert _f0(0.7) / _f0(0.9) > 100.0

    def test_f0_custom_pi_kr(self):
        # Smaller extra dimension → less suppression
        assert _f0(0.9, pi_kr=20.0) > _f0(0.9, pi_kr=37.0)

    def test_f0_large_c(self):
        # Very UV-localised → very small f0
        assert _f0(0.99) < _f0(0.9)

    def test_f0_exactly_half(self):
        assert _f0(0.5) == pytest.approx(1.0)


# ─────────────────────────────────────────────────────────────────────────────
# 3. c_rnu_leading
# ─────────────────────────────────────────────────────────────────────────────

class TestCRnuLeading:
    def test_value(self):
        assert c_rnu_leading() == pytest.approx(6.0/7.0, rel=1e-12)

    def test_formula(self):
        expected = 0.5 + N_W / (2.0 * N2_BRAID)
        assert c_rnu_leading() == pytest.approx(expected, rel=1e-12)

    def test_greater_than_half(self):
        assert c_rnu_leading() > 0.5

    def test_less_than_one(self):
        assert c_rnu_leading() < 1.0

    def test_approx_857(self):
        assert c_rnu_leading() == pytest.approx(0.857143, rel=1e-4)


# ─────────────────────────────────────────────────────────────────────────────
# 4. c_rnu_color_correction
# ─────────────────────────────────────────────────────────────────────────────

class TestCRnuColorCorrection:
    def test_value(self):
        assert c_rnu_color_correction() == pytest.approx(5.0/147.0, rel=1e-12)

    def test_formula(self):
        expected = N_W / (float(N2_BRAID**2) * N_C)
        assert c_rnu_color_correction() == pytest.approx(expected, rel=1e-12)

    def test_positive(self):
        assert c_rnu_color_correction() > 0.0

    def test_approx_034(self):
        assert c_rnu_color_correction() == pytest.approx(0.03401, abs=1e-4)

    def test_small_compared_to_leading(self):
        assert c_rnu_color_correction() < c_rnu_leading()


# ─────────────────────────────────────────────────────────────────────────────
# 5. c_rnu_generation
# ─────────────────────────────────────────────────────────────────────────────

class TestCRnuGeneration:
    def test_gen0_equals_leading_plus_color(self):
        expected = c_rnu_leading() + c_rnu_color_correction()
        assert c_rnu_generation(0) == pytest.approx(expected, rel=1e-10)

    def test_gen0_approx_0891(self):
        assert c_rnu_generation(0) == pytest.approx(0.891, abs=1e-3)

    def test_gen_decreasing(self):
        assert c_rnu_generation(0) > c_rnu_generation(1) > c_rnu_generation(2)

    def test_delta_positive(self):
        delta = c_rnu_generation(0) - c_rnu_generation(1)
        assert delta > 0.0

    def test_delta_small(self):
        delta = c_rnu_generation(0) - c_rnu_generation(1)
        assert delta < 0.05

    def test_delta_formula(self):
        delta_expected = math.log(N1_BRAID * N2_BRAID) / (PI_KR * N2_BRAID)
        delta_actual = c_rnu_generation(0) - c_rnu_generation(1)
        assert delta_actual == pytest.approx(delta_expected, rel=1e-10)

    def test_step_is_constant(self):
        d01 = c_rnu_generation(0) - c_rnu_generation(1)
        d12 = c_rnu_generation(1) - c_rnu_generation(2)
        assert d01 == pytest.approx(d12, rel=1e-10)

    def test_all_greater_than_half(self):
        for i in range(3):
            assert c_rnu_generation(i) > 0.5


# ─────────────────────────────────────────────────────────────────────────────
# 6. neutrino_masses_ev — default (leading-order degenerate)
# ─────────────────────────────────────────────────────────────────────────────

class TestNeutrinoMassesEv:
    def setup_method(self):
        self.masses = neutrino_masses_ev()

    def test_returns_three_masses(self):
        assert len(self.masses) == 3

    def test_all_positive(self):
        assert all(m > 0.0 for m in self.masses)

    def test_degenerate_default(self):
        # All three are equal at leading order (c_L = [0.9, 0.9, 0.9])
        m0, m1, m2 = self.masses
        assert m0 == pytest.approx(m1, rel=1e-10)
        assert m1 == pytest.approx(m2, rel=1e-10)

    def test_first_mass_near_38_mev(self):
        # ≈ 37.7 meV
        assert 0.020 <= self.masses[0] <= 0.080

    def test_all_masses_sub_ev(self):
        assert all(m < 1.0 for m in self.masses)

    def test_sum_below_planck(self):
        assert sum(self.masses) < PLANCK_SUM_MNU_EV

    def test_sum_near_114_mev(self):
        s = sum(self.masses)
        assert 0.08 <= s <= 0.12

    def test_sum_order_of_magnitude(self):
        s = sum(self.masses)
        assert 0.05 <= s <= 0.5

    def test_custom_c_lnu_changes_result(self):
        m_custom = neutrino_masses_ev([0.85, 0.80, 0.75])
        # different from default [0.9,0.9,0.9]
        assert m_custom[0] != pytest.approx(self.masses[0], rel=1e-3)

    def test_custom_c_lnu_returns_three(self):
        assert len(neutrino_masses_ev([0.85, 0.80, 0.75])) == 3

    def test_custom_c_lnu_all_positive(self):
        assert all(m > 0.0 for m in neutrino_masses_ev([0.85, 0.80, 0.75]))

    def test_custom_larger_c_gives_smaller_mass(self):
        # Larger c → smaller f0 → smaller mass
        m_uv = neutrino_masses_ev([0.95, 0.95, 0.95])
        m_ir = neutrino_masses_ev([0.75, 0.75, 0.75])
        assert max(m_uv) < min(m_ir)

    def test_first_mass_lightest_or_equal(self):
        # At leading order all three are equal (masses[0] <= masses[1])
        assert self.masses[0] <= self.masses[1] + 1e-30

    def test_each_mass_mev_scale(self):
        for m in self.masses:
            assert 0.001 <= m <= 0.200

    def test_uses_vew_scale(self):
        # mass must be far below EW scale
        for m in self.masses:
            assert m < V_EW_EV * 1e-6


# ─────────────────────────────────────────────────────────────────────────────
# 7. neutrino_splittings
# ─────────────────────────────────────────────────────────────────────────────

class TestNeutrinoSplittings:
    def setup_method(self):
        self.sp = neutrino_splittings()

    def test_returns_dict(self):
        assert isinstance(self.sp, dict)

    def test_keys_present(self):
        for k in ("Dm2_21", "Dm2_31", "ratio", "pct_err_ratio"):
            assert k in self.sp

    def test_dm2_31_positive(self):
        assert self.sp["Dm2_31"] > 0.0

    def test_dm2_21_positive(self):
        assert self.sp["Dm2_21"] > 0.0

    def test_dm2_31_greater_than_dm2_21(self):
        assert self.sp["Dm2_31"] > self.sp["Dm2_21"]

    def test_ratio_is_geometric(self):
        # Must equal SPLITTING_RATIO_GEO = n₁n₂+1 = 36
        assert self.sp["ratio"] == pytest.approx(SPLITTING_RATIO_GEO)

    def test_ratio_is_36(self):
        assert self.sp["ratio"] == pytest.approx(36.0)

    def test_ratio_from_dm2(self):
        # The returned ratio is the geometric ratio, not computed from Dm2 values
        assert self.sp["ratio"] == pytest.approx(36.0, rel=1e-9)

    def test_pct_err_positive(self):
        assert self.sp["pct_err_ratio"] > 0.0

    def test_pct_err_gt_5(self):
        # 36 vs 32.58 → ~10.5% > 5%: honestly a GEOMETRIC ESTIMATE
        assert self.sp["pct_err_ratio"] > 5.0

    def test_pct_err_lt_20(self):
        # Not wild — within order of magnitude
        assert self.sp["pct_err_ratio"] < 20.0

    def test_pct_err_formula(self):
        expected = abs(SPLITTING_RATIO_GEO - PDG_RATIO) / PDG_RATIO * 100.0
        assert self.sp["pct_err_ratio"] == pytest.approx(expected, rel=1e-8)

    def test_ratio_in_10_to_100_range(self):
        # 36 ∈ [10, 100] — appropriate hierarchy
        assert 10.0 < self.sp["ratio"] < 100.0

    def test_dm2_31_dm2_21_ratio_consistent(self):
        # Dm2_31 / Dm2_21 should equal the geometric ratio
        ratio_check = self.sp["Dm2_31"] / self.sp["Dm2_21"]
        assert ratio_check == pytest.approx(SPLITTING_RATIO_GEO, rel=1e-9)

    def test_dm2_31_mev_squared_scale(self):
        # Expected: (37.7 meV)^2 ≈ 1.4e-3 eV^2 — order-of-magnitude check
        assert 1e-5 <= self.sp["Dm2_31"] <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# 8. planck_constraint_check
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanckConstraintCheck:
    def setup_method(self):
        self.pc = planck_constraint_check()

    def test_returns_dict(self):
        assert isinstance(self.pc, dict)

    def test_keys(self):
        for k in ("sum_mnu", "is_consistent", "margin"):
            assert k in self.pc

    def test_sum_mnu_positive(self):
        assert self.pc["sum_mnu"] > 0.0

    def test_sum_mnu_below_planck(self):
        assert self.pc["sum_mnu"] < PLANCK_SUM_MNU_EV

    def test_is_consistent_true(self):
        assert self.pc["is_consistent"] is True

    def test_margin_positive(self):
        assert self.pc["margin"] > 0.0

    def test_margin_formula(self):
        assert self.pc["margin"] == pytest.approx(
            PLANCK_SUM_MNU_EV - self.pc["sum_mnu"], rel=1e-10
        )

    def test_sum_in_reasonable_range(self):
        assert 0.05 < self.pc["sum_mnu"] < 0.12

    def test_sum_equals_mass_sum(self):
        masses = neutrino_masses_ev()
        assert self.pc["sum_mnu"] == pytest.approx(sum(masses), rel=1e-12)


# ─────────────────────────────────────────────────────────────────────────────
# 9. pillar214_summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar214Summary:
    def setup_method(self):
        self.s = pillar214_summary()

    def test_returns_dict(self):
        assert isinstance(self.s, dict)

    def test_c_rnu_leading_key(self):
        assert "c_Rnu_leading" in self.s

    def test_c_rnu_color_correction_key(self):
        assert "c_Rnu_color_correction" in self.s

    def test_c_rnu_values_key(self):
        assert "c_Rnu_values" in self.s

    def test_neutrino_masses_ev_key(self):
        assert "neutrino_masses_ev" in self.s

    def test_sum_mnu_key(self):
        assert "sum_mnu_ev" in self.s

    def test_planck_consistent_key(self):
        assert "planck_consistent" in self.s

    def test_splitting_ratio_geo_key(self):
        assert "splitting_ratio_geo" in self.s

    def test_splitting_ratio_pdg_key(self):
        assert "splitting_ratio_pdg" in self.s

    def test_splitting_ratio_pct_err_key(self):
        assert "splitting_ratio_pct_err" in self.s

    def test_honest_status_key(self):
        assert "honest_status" in self.s

    def test_toe_delta_key(self):
        assert "toe_delta" in self.s

    def test_p19_status_key(self):
        assert "p19_status" in self.s

    def test_p20_p21_status_key(self):
        assert "p20_p21_status" in self.s

    def test_c_rnu_leading_value(self):
        assert self.s["c_Rnu_leading"] == pytest.approx(6.0/7.0, rel=1e-10)

    def test_c_rnu_color_correction_value(self):
        assert self.s["c_Rnu_color_correction"] == pytest.approx(5.0/147.0, rel=1e-10)

    def test_c_rnu_values_length(self):
        assert len(self.s["c_Rnu_values"]) == 3

    def test_c_rnu_values_decreasing(self):
        v = self.s["c_Rnu_values"]
        assert v[0] > v[1] > v[2]

    def test_masses_length(self):
        assert len(self.s["neutrino_masses_ev"]) == 3

    def test_planck_consistent_true(self):
        assert self.s["planck_consistent"] is True

    def test_splitting_ratio_geo_36(self):
        assert self.s["splitting_ratio_geo"] == pytest.approx(36.0)

    def test_splitting_ratio_pdg_value(self):
        assert self.s["splitting_ratio_pdg"] == pytest.approx(PDG_RATIO, rel=1e-6)

    def test_splitting_ratio_pct_err_gt5(self):
        assert self.s["splitting_ratio_pct_err"] > 5.0

    def test_splitting_ratio_pct_err_lt20(self):
        assert self.s["splitting_ratio_pct_err"] < 20.0

    def test_toe_delta_zero(self):
        assert self.s["toe_delta"] == 0

    def test_p19_constrained(self):
        assert "CONSTRAINED" in self.s["p19_status"]

    def test_p20_p21_geometric_estimate(self):
        assert "GEOMETRIC ESTIMATE" in self.s["p20_p21_status"]

    def test_sum_matches_masses(self):
        assert self.s["sum_mnu_ev"] == pytest.approx(
            sum(self.s["neutrino_masses_ev"]), rel=1e-12
        )

    def test_honest_status_mentions_constrained(self):
        assert "CONSTRAINED" in self.s["honest_status"]

    def test_honest_status_mentions_geometric(self):
        assert "GEOMETRIC ESTIMATE" in self.s["honest_status"]


# ─────────────────────────────────────────────────────────────────────────────
# 10. Cross-checks and invariants
# ─────────────────────────────────────────────────────────────────────────────

class TestCrossChecks:
    def test_c_rnu_leading_from_braids(self):
        assert c_rnu_leading() == pytest.approx(0.5 + N_W/(2*N2_BRAID), rel=1e-12)

    def test_color_correction_from_braids(self):
        assert c_rnu_color_correction() == pytest.approx(
            N_W / (float(N2_BRAID**2) * N_C), rel=1e-12
        )

    def test_f0_product_gives_mev_scale(self):
        c_rnu0 = c_rnu_generation(0)
        mass = V_EW_EV * YUKAWA5 * _f0(0.9) * _f0(c_rnu0)
        # Should be ~37.7 meV
        assert 0.020 <= mass <= 0.070

    def test_sum_mnu_three_times_single(self):
        masses = neutrino_masses_ev()
        # All three equal at leading order
        assert sum(masses) == pytest.approx(3 * masses[0], rel=1e-10)

    def test_neutrino_mass_scale_not_ev(self):
        masses = neutrino_masses_ev()
        assert all(m < 0.15 for m in masses)

    def test_splitting_geo_formula(self):
        assert SPLITTING_RATIO_GEO == N1_BRAID * N2_BRAID + 1

    def test_splitting_pct_err_near_10(self):
        sp = neutrino_splittings()
        assert 8.0 < sp["pct_err_ratio"] < 13.0

    def test_planck_margin_nonzero(self):
        pc = planck_constraint_check()
        assert pc["margin"] > 1e-4

    def test_leading_order_color_correction_raises_c(self):
        # c_rnu0 > c_rnu_leading (color correction is positive)
        assert c_rnu_generation(0) > c_rnu_leading()

    def test_f0_rnu0_less_than_f0_leading(self):
        # Larger c → smaller f0
        assert _f0(c_rnu_generation(0)) < _f0(c_rnu_leading())

    def test_k_cs_74(self):
        assert K_CS == 74

    def test_n1n2_plus1_is_36(self):
        assert N1_BRAID * N2_BRAID + 1 == 36

    def test_all_exported(self):
        from src.core import pillar214_rs_neutrino_spectrum as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing export: {name}"

    def test_provenance_pillar(self):
        from src.core.pillar214_rs_neutrino_spectrum import __provenance__
        assert __provenance__["pillar"] == 214

    def test_pi_kr_is_37(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-12)

    def test_vew_order_of_magnitude(self):
        assert 200e9 < V_EW_EV < 300e9
