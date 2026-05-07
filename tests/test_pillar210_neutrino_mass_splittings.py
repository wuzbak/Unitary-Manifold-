# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar210_neutrino_mass_splittings.py
================================================
Test suite for Pillar 210 — Neutrino Mass Splittings from Braid Hierarchy.

~89 tests covering:
  1. Module constants and internal helper
  2. neutrino_c_L_from_braid()
  3. neutrino_mass_hierarchy()
  4. mass_splitting_prediction()
  5. oscillation_data_comparison()
  6. pillar210_summary()
  7. Physical constraints and honest-status assertions
"""

import math
import pytest

from src.core.pillar210_neutrino_mass_splittings import (
    # constants
    N_W, N1_BRAID, N2_BRAID, K_CS, PI_KR,
    BRAID_PRODUCT, DELTA_C_NU, SPLITTING_RATIO_GEO,
    PDG_DM2_21_EV2, PDG_DM2_31_EV2, PDG_RATIO,
    SUM_MNU_PLANCK_EV, V_HIGGS_MEV,
    # functions
    _f0,
    neutrino_c_L_from_braid,
    neutrino_mass_hierarchy,
    mass_splitting_prediction,
    oscillation_data_comparison,
    pillar210_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_braid_numbers(self):
        assert N_W == 5
        assert N1_BRAID == 5
        assert N2_BRAID == 7

    def test_k_cs(self):
        assert K_CS == 74  # 5² + 7²

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_braid_product(self):
        assert BRAID_PRODUCT == 35  # 5 × 7

    def test_delta_c_nu(self):
        expected = math.log(35) / (2 * 37)
        assert DELTA_C_NU == pytest.approx(expected, rel=1e-9)
        assert 0.04 < DELTA_C_NU < 0.06   # ~0.0480

    def test_splitting_ratio_geo(self):
        assert SPLITTING_RATIO_GEO == 36   # n₁n₂ + 1

    def test_pdg_values(self):
        assert PDG_DM2_21_EV2 == pytest.approx(7.53e-5, rel=1e-6)
        assert PDG_DM2_31_EV2 == pytest.approx(2.453e-3, rel=1e-6)
        assert PDG_RATIO == pytest.approx(PDG_DM2_31_EV2 / PDG_DM2_21_EV2, rel=1e-9)

    def test_planck_bound(self):
        assert SUM_MNU_PLANCK_EV == pytest.approx(0.12)

    def test_v_higgs(self):
        assert V_HIGGS_MEV == pytest.approx(246_220.0)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Internal helper _f0
# ─────────────────────────────────────────────────────────────────────────────

class TestF0Helper:
    def test_flat_profile(self):
        # c = 0.5 → f₀ = 1/√(πkR)
        result = _f0(0.5, pi_kR=37.0)
        assert result == pytest.approx(1.0 / math.sqrt(37.0), rel=1e-6)

    def test_uv_localised(self):
        # c > 0.5: UV-localised, wavefunction should be finite and > 0
        assert _f0(0.7, pi_kR=37.0) > 0
        assert _f0(0.9, pi_kR=37.0) > 0

    def test_uv_smaller_than_flat(self):
        # UV-localised (c > 0.5) → smaller coupling factor (Yukawa suppressed)
        assert _f0(0.7, pi_kR=37.0) < _f0(0.5, pi_kR=37.0)

    def test_monotone_in_c(self):
        # For c > 0.5: larger c → more UV-localised → smaller coupling factor
        assert _f0(0.8, pi_kR=37.0) < _f0(0.6, pi_kR=37.0)

    def test_finite(self):
        for c in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            val = _f0(c, pi_kR=37.0)
            assert math.isfinite(val)
            assert val >= 0


# ─────────────────────────────────────────────────────────────────────────────
# 3. neutrino_c_L_from_braid
# ─────────────────────────────────────────────────────────────────────────────

class TestNeutrinoCLFromBraid:
    @pytest.fixture(scope="class")
    def result(self):
        return neutrino_c_L_from_braid()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_c_lnu_length(self, result):
        assert len(result["c_Lnu"]) == 3

    def test_c_lnu_all_positive(self, result):
        for c in result["c_Lnu"]:
            assert c > 0.0

    def test_c_lnu_all_gt_half(self, result):
        # UV-localised: all c_L > 0.5
        for c in result["c_Lnu"]:
            assert c > 0.5, f"c_L = {c} should be > 0.5 (UV-localised)"

    def test_c_lnu_decreasing(self, result):
        # Normal ordering: c_Lν₀ > c_Lν₁ > c_Lν₂
        c = result["c_Lnu"]
        assert c[0] > c[1] > c[2]

    def test_delta_c_positive(self, result):
        assert result["delta_c_nu"] > 0
        assert result["delta_c_nu"] == pytest.approx(DELTA_C_NU, rel=1e-9)

    def test_beta_nu_positive(self, result):
        assert result["beta_nu"] > 0

    def test_m_nu_three_values(self, result):
        assert len(result["m_nu_eV"]) == 3

    def test_m_nu_all_positive(self, result):
        for m in result["m_nu_eV"]:
            assert m > 0.0

    def test_planck_consistent(self, result):
        assert result["planck_consistent"] is True

    def test_sum_mnu_below_planck(self, result):
        assert result["sum_mnu_eV"] <= SUM_MNU_PLANCK_EV

    def test_sum_mnu_positive(self, result):
        assert result["sum_mnu_eV"] > 0

    def test_v_nu_mev_positive(self, result):
        assert result["v_nu_MeV"] > 0

    def test_v_nu_mev_suppressed(self, result):
        # v_ν < v_EW (suppressed by braid)
        assert result["v_nu_MeV"] < V_HIGGS_MEV

    def test_braid_product(self, result):
        assert result["braid_product"] == BRAID_PRODUCT

    def test_status_beta_constrained(self, result):
        assert "CONSTRAINED" in result["status_beta"]

    def test_status_delta_derived(self, result):
        assert "DERIVED" in result["status_delta_c"]

    def test_invalid_winding(self):
        with pytest.raises(ValueError):
            neutrino_c_L_from_braid(n_w=0)

    def test_invalid_n1(self):
        with pytest.raises(ValueError):
            neutrino_c_L_from_braid(n1=-1)

    def test_invalid_pi_kr(self):
        with pytest.raises(ValueError):
            neutrino_c_L_from_braid(pi_kR=-1.0)

    def test_normal_mass_ordering(self, result):
        m = result["m_nu_eV"]
        # Normal ordering: most UV-localised (index 0) → lightest
        # c_Lν₀ largest → m_ν₁ smallest
        assert m[0] < m[1] < m[2], (
            f"Expected normal ordering m₁ < m₂ < m₃, got {m}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. neutrino_mass_hierarchy
# ─────────────────────────────────────────────────────────────────────────────

class TestNeutrinoMassHierarchy:
    @pytest.fixture(scope="class")
    def setup(self):
        c_result = neutrino_c_L_from_braid()
        return c_result["c_Lnu"], c_result["v_nu_MeV"]

    def test_returns_dict(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        assert isinstance(result, dict)

    def test_three_masses(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        assert len(result["m_nu_eV"]) == 3

    def test_masses_positive(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        for m in result["m_nu_eV"]:
            assert m > 0

    def test_ordering_normal(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        assert result["ordering"] == "normal"

    def test_planck_ok(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        assert result["planck_ok"] is True

    def test_sum_matches(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        expected_sum = sum(result["m_nu_eV"])
        assert result["sum_mnu_eV"] == pytest.approx(expected_sum, rel=1e-12)

    def test_invalid_c_lnu(self, setup):
        _, v_nu = setup
        with pytest.raises(ValueError):
            neutrino_mass_hierarchy([0.6, 0.7], v_nu)

    def test_invalid_v_nu(self, setup):
        c_Lnu, _ = setup
        with pytest.raises(ValueError):
            neutrino_mass_hierarchy(c_Lnu, -1.0)

    def test_individual_mass_keys(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        assert "m_nu1_eV" in result
        assert "m_nu2_eV" in result
        assert "m_nu3_eV" in result

    def test_masses_in_sub_eV_range(self, setup):
        c_Lnu, v_nu = setup
        result = neutrino_mass_hierarchy(c_Lnu, v_nu)
        # Each mass should be < 0.12 eV individually
        for m in result["m_nu_eV"]:
            assert m < 0.12, f"Mass {m:.4e} eV should be < 0.12 eV"


# ─────────────────────────────────────────────────────────────────────────────
# 5. mass_splitting_prediction
# ─────────────────────────────────────────────────────────────────────────────

class TestMassSplittingPrediction:
    @pytest.fixture(scope="class")
    def result(self):
        return mass_splitting_prediction()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_dm2_21_positive(self, result):
        assert result["dm2_21_pred_eV2"] > 0

    def test_dm2_31_positive(self, result):
        assert result["dm2_31_pred_eV2"] > 0

    def test_dm2_31_gt_dm2_21(self, result):
        # Normal ordering: |Δm²₃₁| > |Δm²₂₁|
        assert result["dm2_31_pred_eV2"] > result["dm2_21_pred_eV2"]

    def test_ratio_geo_is_36(self, result):
        assert result["ratio_geo"] == 36

    def test_ratio_pred_near_geo(self, result):
        # The predicted ratio from the mass calculation should be close to 36
        assert 20 < result["ratio_pred"] < 60, (
            f"ratio_pred = {result['ratio_pred']:.1f} should be between 20 and 60"
        )

    def test_geo_ratio_pct_err(self, result):
        # 10% discrepancy documented — assert it's in a reasonable range
        pct = result["ratio_geo_pct_err"]
        assert 5.0 < pct < 20.0, (
            f"ratio_geo_pct_err = {pct:.1f}% should be 5–20% (known discrepancy)"
        )

    def test_status_ratio_geometric_estimate(self, result):
        assert "GEOMETRIC ESTIMATE" in result["status_ratio"]

    def test_status_absolutes_constrained(self, result):
        assert "CONSTRAINED" in result["status_absolutes"]

    def test_status_p20(self, result):
        assert "GEOMETRIC ESTIMATE" in result["status_p20"]

    def test_status_p21(self, result):
        assert "GEOMETRIC ESTIMATE" in result["status_p21"]

    def test_planck_consistent(self, result):
        assert result["planck_consistent"] is True

    def test_pdg_references_present(self, result):
        assert result["dm2_21_pdg_eV2"] == pytest.approx(PDG_DM2_21_EV2)
        assert result["dm2_31_pdg_eV2"] == pytest.approx(PDG_DM2_31_EV2)

    def test_no_false_derived_in_absolutes(self, result):
        # The absolute splittings should NOT claim DERIVED status
        assert "DERIVED" not in result["status_absolutes"]


# ─────────────────────────────────────────────────────────────────────────────
# 6. oscillation_data_comparison
# ─────────────────────────────────────────────────────────────────────────────

class TestOscillationDataComparison:
    @pytest.fixture(scope="class")
    def result(self):
        return oscillation_data_comparison()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_pct_err_keys(self, result):
        assert "dm2_21_pct_err" in result
        assert "dm2_31_pct_err" in result

    def test_ratio_pct_err_present(self, result):
        assert "ratio_pct_err" in result
        assert result["ratio_pct_err"] > 0

    def test_assessment_p19(self, result):
        assert "assessment_p19" in result
        assert "CONSTRAINED" in result["assessment_p19"]

    def test_assessment_p20(self, result):
        assert "assessment_p20" in result
        assert "GEOMETRIC ESTIMATE" in result["assessment_p20"]

    def test_assessment_p21(self, result):
        assert "assessment_p21" in result
        assert "GEOMETRIC ESTIMATE" in result["assessment_p21"]

    def test_assessment_ratio(self, result):
        assert "assessment_ratio" in result
        assert "GEOMETRIC ESTIMATE" in result["assessment_ratio"]

    def test_sum_mnu_meV_positive(self, result):
        assert result["sum_mnu_meV"] > 0

    def test_sum_mnu_meV_below_planck(self, result):
        assert result["sum_mnu_meV"] < 120.0   # Planck bound in meV

    def test_ratio_geo_present(self, result):
        assert result["ratio_geo"] == SPLITTING_RATIO_GEO

    def test_delta_c_nu_present(self, result):
        assert result["delta_c_nu"] == pytest.approx(DELTA_C_NU, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# 7. pillar210_summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar210Summary:
    @pytest.fixture(scope="class")
    def result(self):
        return pillar210_summary()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_pillar_number(self, result):
        assert result["pillar"] == 210

    def test_name(self, result):
        assert "Neutrino" in result["name"]

    def test_inputs_section(self, result):
        inp = result["inputs"]
        assert inp["n_w"] == N_W
        assert inp["n1"] == N1_BRAID
        assert inp["n2"] == N2_BRAID
        assert inp["K_CS"] == K_CS
        assert inp["braid_product"] == BRAID_PRODUCT

    def test_derived_section(self, result):
        derived = result["derived"]
        assert "delta_c_nu" in derived
        assert "splitting_ratio_geo" in derived
        assert derived["splitting_ratio_geo"] == 36
        assert "DERIVED" in derived["delta_c_nu_status"]
        assert "GEOMETRIC ESTIMATE" in derived["splitting_ratio_status"]

    def test_constrained_section(self, result):
        c = result["constrained"]
        assert c["planck_consistent"] is True
        assert c["sum_mnu_meV"] > 0
        assert c["sum_mnu_meV"] < 120.0
        assert c["m_nu1_meV"] > 0
        assert c["m_nu2_meV"] > c["m_nu1_meV"]
        assert c["m_nu3_meV"] > c["m_nu2_meV"]

    def test_splittings_section(self, result):
        s = result["splittings"]
        assert s["dm2_21_pred_eV2"] > 0
        assert s["dm2_31_pred_eV2"] > 0
        assert s["dm2_31_pred_eV2"] > s["dm2_21_pred_eV2"]
        assert s["ratio_geo"] == 36
        assert 5.0 < s["ratio_pct_err"] < 20.0

    def test_toe_score_impact(self, result):
        toe = result["toe_score_impact"]
        assert "P19_m_nu1" in toe
        assert "P20_dm2_21" in toe
        assert "P21_dm2_31" in toe
        assert "CONSTRAINED" in toe["P19_m_nu1"]
        assert "GEOMETRIC ESTIMATE" in toe["P20_dm2_21"]
        assert "GEOMETRIC ESTIMATE" in toe["P21_dm2_31"]

    def test_open_problems_present(self, result):
        assert len(result["open_problems"]) >= 2

    def test_no_false_derived_in_toe(self, result):
        toe = result["toe_score_impact"]
        # P19 must not claim DERIVED (it's CONSTRAINED)
        assert "DERIVED" not in toe["P19_m_nu1"]


# ─────────────────────────────────────────────────────────────────────────────
# 8. Physical plausibility cross-checks
# ─────────────────────────────────────────────────────────────────────────────

class TestPhysicalPlausibility:
    def test_geometric_ratio_vs_pdg(self):
        """Pillar 90 ratio 36 vs PDG 32.6: should be 5–15% discrepancy."""
        pct = abs(SPLITTING_RATIO_GEO - PDG_RATIO) / PDG_RATIO * 100.0
        assert 5.0 < pct < 20.0, f"Expected 5–20%, got {pct:.1f}%"

    def test_dm2_21_order_of_magnitude(self):
        """Δm²₂₁ should be ~10⁻⁵ eV² (solar)."""
        result = mass_splitting_prediction()
        dm2_21 = result["dm2_21_pred_eV2"]
        assert 1e-6 < dm2_21 < 1e-3, f"Δm²₂₁ = {dm2_21:.2e} eV² out of expected range"

    def test_dm2_31_order_of_magnitude(self):
        """Δm²₃₁ should be ~10⁻³ eV² (atmospheric)."""
        result = mass_splitting_prediction()
        dm2_31 = result["dm2_31_pred_eV2"]
        assert 1e-4 < dm2_31 < 1e-1, f"Δm²₃₁ = {dm2_31:.2e} eV² out of expected range"

    def test_sum_mnu_lt_120_mev(self):
        """Σm_ν must satisfy Planck bound."""
        c_result = neutrino_c_L_from_braid()
        assert c_result["sum_mnu_eV"] < SUM_MNU_PLANCK_EV

    def test_all_masses_positive(self):
        c_result = neutrino_c_L_from_braid()
        for m in c_result["m_nu_eV"]:
            assert m > 0

    def test_normal_ordering(self):
        """Braid hierarchy should give normal ordering m₁ < m₂ < m₃."""
        c_result = neutrino_c_L_from_braid()
        m = c_result["m_nu_eV"]
        assert m[0] < m[1] < m[2]

    def test_v_nu_suppression_factor(self):
        """v_ν/v_EW = 1/√35 should equal 1/√(n₁n₂)."""
        c_result = neutrino_c_L_from_braid()
        expected_ratio = 1.0 / math.sqrt(BRAID_PRODUCT)
        actual_ratio = c_result["v_nu_MeV"] / V_HIGGS_MEV
        assert actual_ratio == pytest.approx(expected_ratio, rel=1e-9)

    def test_delta_c_nu_derivation(self):
        """δc_ν = ln(35)/(2×37) must be exactly reproduced."""
        expected = math.log(35.0) / (2.0 * 37.0)
        assert DELTA_C_NU == pytest.approx(expected, rel=1e-12)

    def test_inter_generation_step_applied(self):
        """c_Lν values must differ by exactly δc_ν."""
        result = neutrino_c_L_from_braid()
        c = result["c_Lnu"]
        dc = result["delta_c_nu"]
        assert c[0] - c[1] == pytest.approx(dc, rel=1e-9)
        assert c[1] - c[2] == pytest.approx(dc, rel=1e-9)
