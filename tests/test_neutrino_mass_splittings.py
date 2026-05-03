# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_mass_splittings.py
=======================================
Tests for Pillar 135 — Neutrino Mass Splittings from RS Dirac Zero-Mode Framework.

All tests verify:
  - δc_ν = ln(35)/(2×37) ≈ 0.048 from braid geometry
  - RS Dirac zero-mode profile f₀(c) is positive and decreasing in c
  - Geometric mass ratios: m_ν₂/m_ν₁ = √35, m_ν₃/m_ν₁ = 35
  - Splitting ratio Δm²₃₁/Δm²₂₁ ≈ 36 (pure geometry, 10% off PDG 32.6)
  - Δm²₃₁ predicted from Δm²₂₁ to ~10% accuracy
  - Σm_ν < 120 meV (Planck consistent)
  - c_L parameters are well-separated and > 1/2
  - Error handling for invalid inputs
  - Pillar 135 summary structure
"""
import math
import pytest

from src.core.neutrino_mass_splittings import (
    neutrino_generation_step,
    rs_dirac_zero_mode_profile,
    rs_neutrino_mass_ratio,
    neutrino_c_parameters,
    neutrino_mass_splittings_rs,
    neutrino_sum_constraint,
    pillar135_summary,
    N1_CANONICAL,
    N2_CANONICAL,
    PI_KR_CANONICAL,
    DM2_21_PDG_EV2,
    DM2_31_PDG_EV2,
    DM2_RATIO_PDG,
    DM2_RATIO_GEO,
    SUM_MNU_PLANCK_EV,
)


class TestNeutrinoGenerationStep:
    def test_canonical_value(self):
        dc = neutrino_generation_step()
        expected = math.log(35) / (2 * 37)
        assert abs(dc - expected) < 1e-10

    def test_approximately_0_048(self):
        dc = neutrino_generation_step()
        assert 0.045 < dc < 0.052

    def test_larger_braid_product_gives_larger_step(self):
        dc_57 = neutrino_generation_step(5, 7)
        dc_35 = neutrino_generation_step(3, 5)
        # 5×7=35 > 3×5=15, so log(35) > log(15)
        assert dc_57 > dc_35

    def test_invalid_n1_raises(self):
        with pytest.raises(ValueError):
            neutrino_generation_step(n1=0)

    def test_invalid_pi_kr_raises(self):
        with pytest.raises(ValueError):
            neutrino_generation_step(pi_kr=-1.0)

    def test_larger_pi_kr_gives_smaller_step(self):
        dc1 = neutrino_generation_step(pi_kr=30.0)
        dc2 = neutrino_generation_step(pi_kr=40.0)
        assert dc2 < dc1


class TestRsDiracZeroModeProfile:
    def test_positive_output(self):
        f = rs_dirac_zero_mode_profile(0.7)
        assert f > 0

    def test_larger_c_gives_smaller_profile(self):
        f1 = rs_dirac_zero_mode_profile(0.6)
        f2 = rs_dirac_zero_mode_profile(0.8)
        assert f2 < f1

    def test_c_below_half_raises(self):
        with pytest.raises(ValueError):
            rs_dirac_zero_mode_profile(0.5)

    def test_c_below_half_strict_raises(self):
        with pytest.raises(ValueError):
            rs_dirac_zero_mode_profile(0.49)

    def test_invalid_pi_kr_raises(self):
        with pytest.raises(ValueError):
            rs_dirac_zero_mode_profile(0.7, pi_kr=-1.0)

    def test_large_c_gives_very_small_profile(self):
        f = rs_dirac_zero_mode_profile(2.0)
        assert f < 1e-10

    def test_profile_ratio_matches_braid(self):
        # For step δc: f₀(c+δc)/f₀(c) ≈ exp(-δc×πkR) = exp(-ln(35)/2) = 1/√35
        dc = neutrino_generation_step()
        c_base = 0.70
        f1 = rs_dirac_zero_mode_profile(c_base)
        f2 = rs_dirac_zero_mode_profile(c_base + dc)
        ratio = f2 / f1
        expected = 1.0 / math.sqrt(35)
        # Allow 15% tolerance (approximation)
        assert abs(ratio - expected) / expected < 0.15


class TestRsNeutrinoMassRatio:
    def test_mass_ratio_21_is_sqrt35(self):
        result = rs_neutrino_mass_ratio()
        expected = math.sqrt(35)
        assert abs(result["m_nu2_over_m_nu1"] - expected) < 1e-8

    def test_mass_ratio_31_is_35(self):
        result = rs_neutrino_mass_ratio()
        assert abs(result["m_nu3_over_m_nu1"] - 35.0) < 1e-8

    def test_splitting_ratio_geo_is_36(self):
        result = rs_neutrino_mass_ratio()
        assert abs(result["splitting_ratio_geo"] - 36.0) < 1e-8

    def test_splitting_ratio_pdg_correct(self):
        result = rs_neutrino_mass_ratio()
        assert abs(result["splitting_ratio_pdg"] - DM2_RATIO_PDG) < 1e-8

    def test_splitting_ratio_error_below_15pct(self):
        result = rs_neutrino_mass_ratio()
        assert result["splitting_ratio_pct_err"] < 15.0

    def test_braid_pair_stored(self):
        result = rs_neutrino_mass_ratio(n1=5, n2=7)
        assert result["n1"] == 5 and result["n2"] == 7

    def test_different_pair_gives_different_ratio(self):
        r1 = rs_neutrino_mass_ratio(5, 7)
        r2 = rs_neutrino_mass_ratio(3, 5)
        assert abs(r1["m_nu3_over_m_nu1"] - r2["m_nu3_over_m_nu1"]) > 0.1

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            rs_neutrino_mass_ratio(n1=0, n2=7)


class TestNeutrinoCParameters:
    def test_c_nu1_greater_than_c_nu2(self):
        result = neutrino_c_parameters()
        assert result["c_nu1"] > result["c_nu2"]

    def test_c_nu2_greater_than_c_nu3(self):
        result = neutrino_c_parameters()
        assert result["c_nu2"] > result["c_nu3"]

    def test_all_c_above_half(self):
        result = neutrino_c_parameters()
        assert result["c_nu1"] > 0.5
        assert result["c_nu2"] > 0.5
        assert result["c_nu3"] > 0.5

    def test_step_is_delta_c(self):
        dc = neutrino_generation_step()
        result = neutrino_c_parameters()
        assert abs(result["c_nu1"] - result["c_nu2"] - dc) < 1e-10
        assert abs(result["c_nu2"] - result["c_nu3"] - dc) < 1e-10

    def test_profiles_are_positive(self):
        result = neutrino_c_parameters()
        assert result["f0_nu1"] > 0
        assert result["f0_nu2"] > 0
        assert result["f0_nu3"] > 0

    def test_f0_nu3_largest(self):
        # More IR-localized = larger profile
        result = neutrino_c_parameters()
        assert result["f0_nu3"] > result["f0_nu2"] > result["f0_nu1"]


class TestNeutrinoMassSplittingsRs:
    def test_dm2_21_preserved(self):
        result = neutrino_mass_splittings_rs()
        # Δm²₂₁ is the input — it's preserved by construction
        assert abs(result["dm2_21_geo_eV2"] - DM2_21_PDG_EV2) < 1e-15

    def test_dm2_31_within_15pct(self):
        result = neutrino_mass_splittings_rs()
        assert result["dm2_31_pct_err"] < 15.0

    def test_masses_ordered_nh(self):
        result = neutrino_mass_splittings_rs()
        assert result["m_nu1_eV"] < result["m_nu2_eV"] < result["m_nu3_eV"]

    def test_m_nu1_approximately_1_5_meV(self):
        result = neutrino_mass_splittings_rs()
        assert 1.0e-3 < result["m_nu1_eV"] < 3.0e-3

    def test_splitting_ratio_approximately_36(self):
        result = neutrino_mass_splittings_rs()
        assert abs(result["splitting_ratio_geo"] - 36.0) < 0.1

    def test_planck_consistent(self):
        result = neutrino_mass_splittings_rs()
        assert result["planck_consistent"] is True

    def test_sum_mnu_below_120_meV(self):
        result = neutrino_mass_splittings_rs()
        assert result["sum_mnu_eV"] < SUM_MNU_PLANCK_EV

    def test_status_contains_constrained(self):
        result = neutrino_mass_splittings_rs()
        assert "CONSTRAINED" in result["status"] or "DERIVED" in result["status"]

    def test_dm2_31_predicted_gev_correct_order(self):
        result = neutrino_mass_splittings_rs()
        # Δm²₃₁ should be order 10⁻³ eV²
        assert 1e-3 < result["dm2_31_geo_eV2"] < 5e-3

    def test_derivation_is_string(self):
        result = neutrino_mass_splittings_rs()
        assert isinstance(result["derivation"], str)

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            neutrino_mass_splittings_rs(n1=0)

    def test_invalid_dm2_raises(self):
        with pytest.raises(ValueError):
            neutrino_mass_splittings_rs(dm2_21_input_ev2=-1.0)


class TestNeutrinoSumConstraint:
    def test_consistent(self):
        result = neutrino_sum_constraint()
        assert result["consistent"] is True

    def test_sum_below_planck_limit(self):
        result = neutrino_sum_constraint()
        assert result["sum_mnu_eV"] < result["planck_limit_eV"]

    def test_headroom_positive(self):
        result = neutrino_sum_constraint()
        assert result["headroom_meV"] > 0

    def test_planck_limit_correct(self):
        result = neutrino_sum_constraint()
        assert abs(result["planck_limit_eV"] - SUM_MNU_PLANCK_EV) < 1e-10

    def test_masses_positive(self):
        result = neutrino_sum_constraint()
        assert result["m_nu1_meV"] > 0
        assert result["m_nu2_meV"] > 0
        assert result["m_nu3_meV"] > 0


class TestModuleConstants:
    def test_dm2_21_pdg(self):
        assert abs(DM2_21_PDG_EV2 - 7.53e-5) < 1e-10

    def test_dm2_31_pdg(self):
        assert abs(DM2_31_PDG_EV2 - 2.453e-3) < 1e-10

    def test_ratio_pdg_correct(self):
        expected = 2.453e-3 / 7.53e-5
        assert abs(DM2_RATIO_PDG - expected) < 1e-8

    def test_ratio_geo_is_36(self):
        assert abs(DM2_RATIO_GEO - 36.0) < 1e-10

    def test_planck_limit(self):
        assert abs(SUM_MNU_PLANCK_EV - 0.12) < 1e-10


class TestPillar135Summary:
    def test_pillar_number_135(self):
        result = pillar135_summary()
        assert result["pillar"] == 135

    def test_is_constrained(self):
        result = pillar135_summary()
        # Should be ⚠️ CONSTRAINED, not ❌ OPEN
        assert "CONSTRAINED" in result["toe_status"] or "DERIVED" in result["toe_status"]

    def test_splitting_ratio_close_to_36(self):
        result = pillar135_summary()
        assert abs(result["splitting_ratio_geo"] - 36.0) < 0.1

    def test_planck_consistent(self):
        result = pillar135_summary()
        assert result["planck_consistent"] is True

    def test_braid_pair(self):
        result = pillar135_summary()
        assert result["braid_pair"] == (5, 7)

    def test_dm2_31_pct_err_reasonable(self):
        result = pillar135_summary()
        assert result["dm2_31_pct_err"] < 15.0

    def test_improvement_over_open_in_result(self):
        result = pillar135_summary()
        assert "improvement_over_open" in result
        assert len(result["improvement_over_open"]) > 10

    def test_sum_mnu_below_120(self):
        result = pillar135_summary()
        assert result["sum_mnu_meV"] < 120.0
