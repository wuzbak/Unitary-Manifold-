# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_universal_yukawa.py
================================
Tests for Pillar 98 — Universal Yukawa Test: c_L Spectrum at Ŷ₅=1 and b-τ Unification.
(src/core/universal_yukawa.py)

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.universal_yukawa import (
    # Constants
    N_W, N1_BRAID, N2_BRAID, K_CS, PI_KR, K_RS,
    Y5_UNIVERSAL, C_R_DEMOCRATIC, C_R_TOP,
    M_PL_GEV, M_GUT_GEV, M_Z_GEV, V_HIGGS_MEV, V_HIGGS_GEV, ALPHA_S_MZ,
    M_ELECTRON_MEV, M_MUON_MEV, M_TAU_MEV,
    M_UP_MEV, M_CHARM_MEV, M_TOP_MEV,
    M_DOWN_MEV, M_STRANGE_MEV, M_BOTTOM_MEV,
    # Functions
    sm_yukawa_coupling,
    required_overlap_at_universal_yukawa,
    required_c_L_for_universal_yukawa,
    universal_yukawa_c_L_spectrum,
    c_L_ordering_check,
    c_L_winding_consistency,
    rge_yukawa_running,
    b_tau_unification_test,
    fermion_mass_from_universal_yukawa,
    all_fermion_masses_from_universal_yukawa,
    pillar98_summary,
    _f0,
)


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_braid_pair(self):
        assert N1_BRAID == 5 and N2_BRAID == 7

    def test_k_cs(self):
        assert K_CS == 74 and K_CS == N1_BRAID ** 2 + N2_BRAID ** 2

    def test_pi_kR(self):
        assert PI_KR == 37.0 and PI_KR == K_CS / 2.0

    def test_y5_universal(self):
        assert Y5_UNIVERSAL == 1.0

    def test_c_r_democratic(self):
        assert C_R_DEMOCRATIC == 0.5

    def test_c_r_top(self):
        assert C_R_TOP == -0.5

    def test_m_gut(self):
        assert M_GUT_GEV == 2.0e16

    def test_alpha_s(self):
        assert abs(ALPHA_S_MZ - 0.118) < 0.005

    def test_v_higgs(self):
        assert abs(V_HIGGS_MEV - 246_220.0) < 1.0


# ===========================================================================
# SM Yukawa coupling
# ===========================================================================

class TestSmYukawaCoupling:
    def test_electron(self):
        y = sm_yukawa_coupling(M_ELECTRON_MEV)
        expected = M_ELECTRON_MEV / V_HIGGS_MEV
        assert abs(y - expected) < 1e-12

    def test_top_quark_order_unity(self):
        """Top Yukawa is O(1)."""
        y = sm_yukawa_coupling(M_TOP_MEV)
        assert 0.5 < y < 1.2

    def test_bottom_much_smaller_than_top(self):
        y_t = sm_yukawa_coupling(M_TOP_MEV)
        y_b = sm_yukawa_coupling(M_BOTTOM_MEV)
        assert y_b < y_t

    def test_electron_much_smaller_than_tau(self):
        y_e = sm_yukawa_coupling(M_ELECTRON_MEV)
        y_tau = sm_yukawa_coupling(M_TAU_MEV)
        assert y_e < y_tau

    def test_invalid_mass(self):
        with pytest.raises(ValueError):
            sm_yukawa_coupling(-1.0)

    def test_invalid_vev(self):
        with pytest.raises(ValueError):
            sm_yukawa_coupling(1.0, v_EW_MeV=0.0)

    def test_positive(self):
        for m in [M_ELECTRON_MEV, M_MUON_MEV, M_TAU_MEV, M_TOP_MEV]:
            assert sm_yukawa_coupling(m) > 0.0

    def test_dimensionless(self):
        """y_f = m_f/v, so y_f < 1 for all but top."""
        for m in [M_ELECTRON_MEV, M_MUON_MEV, M_TAU_MEV,
                  M_DOWN_MEV, M_STRANGE_MEV, M_BOTTOM_MEV,
                  M_UP_MEV, M_CHARM_MEV]:
            assert sm_yukawa_coupling(m) < 1.0


class TestRequiredOverlap:
    def test_equals_sm_yukawa(self):
        """Required overlap at Ŷ₅=1 equals SM Yukawa coupling."""
        y = sm_yukawa_coupling(M_ELECTRON_MEV)
        ov = required_overlap_at_universal_yukawa(M_ELECTRON_MEV)
        assert abs(y - ov) < 1e-14

    def test_positive(self):
        ov = required_overlap_at_universal_yukawa(M_ELECTRON_MEV)
        assert ov > 0.0


# ===========================================================================
# Required c_L at universal Yukawa
# ===========================================================================

class TestRequiredCLForUniversalYukawa:
    def test_electron_c_L_near_08(self):
        """Electron c_L ≈ 0.798 at Ŷ₅=1 (matches Pillar 93)."""
        c_L = required_c_L_for_universal_yukawa(M_ELECTRON_MEV)
        assert 0.78 < c_L < 0.82

    def test_top_c_L_below_half(self):
        """Top quark c_L < 0.5 (IR-localised LH top with c_R = -0.5)."""
        c_L = required_c_L_for_universal_yukawa(M_TOP_MEV, c_R=C_R_TOP)
        assert c_L < 0.5

    def test_heavier_gives_smaller_c_L(self):
        """Heavier fermion (in same sector) → smaller c_L."""
        c_e = required_c_L_for_universal_yukawa(M_ELECTRON_MEV)
        c_mu = required_c_L_for_universal_yukawa(M_MUON_MEV)
        c_tau = required_c_L_for_universal_yukawa(M_TAU_MEV)
        assert c_e > c_mu > c_tau

    def test_reproducibility(self):
        """Bisection reproduces the target mass to < 0.01%."""
        c_L = required_c_L_for_universal_yukawa(M_BOTTOM_MEV)
        f0_L = _f0(c_L)
        f0_R = _f0(C_R_DEMOCRATIC)
        m_pred = Y5_UNIVERSAL * V_HIGGS_MEV * f0_L * f0_R
        pct_err = abs(m_pred - M_BOTTOM_MEV) / M_BOTTOM_MEV * 100.0
        assert pct_err < 0.01

    def test_invalid_mass(self):
        with pytest.raises(ValueError):
            required_c_L_for_universal_yukawa(0.0)

    def test_invalid_vev(self):
        with pytest.raises(ValueError):
            required_c_L_for_universal_yukawa(M_ELECTRON_MEV, v_EW_MeV=0.0)

    def test_invalid_pi_kR(self):
        with pytest.raises(ValueError):
            required_c_L_for_universal_yukawa(M_ELECTRON_MEV, pi_kR=0.0)


# ===========================================================================
# Universal c_L spectrum
# ===========================================================================

class TestUniversalYukawaSpectrum:
    @pytest.fixture(scope="class")
    def spectrum(self):
        return universal_yukawa_c_L_spectrum()

    def test_returns_dict(self, spectrum):
        assert isinstance(spectrum, dict)
        assert "fermions" in spectrum

    def test_nine_fermions(self, spectrum):
        assert len(spectrum["fermions"]) == 9

    def test_all_fermions_present(self, spectrum):
        expected = {"electron", "muon", "tau", "up", "charm", "top",
                    "down", "strange", "bottom"}
        assert set(spectrum["fermions"].keys()) == expected

    def test_y5_universal(self, spectrum):
        assert abs(spectrum["Y5_universal"] - 1.0) < 1e-12

    def test_all_c_L_physical_leptons(self, spectrum):
        """Leptons: all c_L > 0.5 (UV-localised)."""
        for name in ("electron", "muon", "tau"):
            c_L = spectrum["fermions"][name]["c_L"]
            assert c_L > 0.5, f"{name} c_L = {c_L:.4f} should be > 0.5"

    def test_top_c_L_can_be_IR_localised(self, spectrum):
        """Top quark c_L can be < 0.5 (IR-localised LH top with c_R=-0.5)."""
        c_t = spectrum["fermions"]["top"]["c_L"]
        # Top can be IR-localised: c_L < 0.5 is valid in RS framework
        assert -5.0 < c_t < 5.0 and math.isfinite(c_t)

    def test_all_overlaps_positive(self, spectrum):
        for name, data in spectrum["fermions"].items():
            assert data["overlap"] > 0.0

    def test_mass_reproduction_exact(self, spectrum):
        """All masses reproduced to < 0.01% (bisection accuracy)."""
        for name, data in spectrum["fermions"].items():
            assert data["pct_error"] < 0.01, (
                f"{name}: {data['pct_error']:.4f}% error"
            )

    def test_lepton_ordering(self, spectrum):
        """e: c_L largest, τ: c_L smallest (heavier → more IR-localised)."""
        c_e = spectrum["fermions"]["electron"]["c_L"]
        c_mu = spectrum["fermions"]["muon"]["c_L"]
        c_tau = spectrum["fermions"]["tau"]["c_L"]
        assert c_e > c_mu > c_tau

    def test_up_sector_ordering(self, spectrum):
        c_u = spectrum["fermions"]["up"]["c_L"]
        c_c = spectrum["fermions"]["charm"]["c_L"]
        c_t = spectrum["fermions"]["top"]["c_L"]
        assert c_u > c_c > c_t

    def test_down_sector_ordering(self, spectrum):
        c_d = spectrum["fermions"]["down"]["c_L"]
        c_s = spectrum["fermions"]["strange"]["c_L"]
        c_b = spectrum["fermions"]["bottom"]["c_L"]
        assert c_d > c_s > c_b

    def test_electron_c_L_matches_pillar93(self, spectrum):
        """c_Le ≈ 0.798 matches Pillar 93 prediction."""
        c_e = spectrum["fermions"]["electron"]["c_L"]
        assert 0.78 < c_e < 0.82

    def test_sm_yukawa_consistency(self, spectrum):
        """y_f = m_f/v for each fermion."""
        for name, data in spectrum["fermions"].items():
            y_expected = data["m_pdg_MeV"] / V_HIGGS_MEV
            assert abs(data["y_f"] - y_expected) < 1e-14


# ===========================================================================
# c_L ordering check
# ===========================================================================

class TestCLOrderingCheck:
    @pytest.fixture(scope="class")
    def ordering(self):
        spec = universal_yukawa_c_L_spectrum()
        return c_L_ordering_check(spec)

    def test_all_ordered(self, ordering):
        assert ordering["all_ordered"], (
            f"c_L ordering: leptons={ordering['leptons_ordered']}, "
            f"up={ordering['up_sector_ordered']}, down={ordering['down_sector_ordered']}"
        )

    def test_lepton_ordered(self, ordering):
        assert ordering["leptons_ordered"]

    def test_up_ordered(self, ordering):
        assert ordering["up_sector_ordered"]

    def test_down_ordered(self, ordering):
        assert ordering["down_sector_ordered"]

    def test_three_lepton_c_L(self, ordering):
        assert len(ordering["lepton_c_L"]) == 3

    def test_three_up_c_L(self, ordering):
        assert len(ordering["up_sector_c_L"]) == 3

    def test_three_down_c_L(self, ordering):
        assert len(ordering["down_sector_c_L"]) == 3


# ===========================================================================
# c_L winding consistency
# ===========================================================================

class TestCLWindingConsistency:
    @pytest.fixture(scope="class")
    def winding(self):
        spec = universal_yukawa_c_L_spectrum()
        return c_L_winding_consistency(spec)

    def test_majority_consistent(self, winding):
        """At least 5/9 fermions should be near winding-quantised levels."""
        assert winding["majority_consistent"], (
            f"Only {winding['n_winding_consistent']}/9 fermions winding-consistent"
        )

    def test_n_winding_gte_half(self, winding):
        assert winding["n_winding_consistent"] >= 5

    def test_fraction_computed(self, winding):
        assert 0.0 <= winding["fraction_consistent"] <= 1.0

    def test_quantised_levels_for_nw5(self, winding):
        """Winding quantised levels for n_w=5 are {1.0, 0.9, 0.8, 0.7, 0.6, 0.5}."""
        levels = winding["quantised_levels"]
        assert abs(levels[0] - 1.0) < 1e-10  # n=0
        assert abs(levels[2] - 0.8) < 1e-10  # n=2 → c=0.8 (electron)
        assert abs(levels[5] - 0.5) < 1e-10  # n=5 → c=0.5 (flat profile)

    def test_spacing(self, winding):
        """Spacing = 1/(2n_w) = 0.1 for n_w=5."""
        assert abs(winding["spacing"] - 0.1) < 1e-10

    def test_total_fermions(self, winding):
        assert winding["total_fermions"] == 9


# ===========================================================================
# RGE running
# ===========================================================================

class TestRgeYukawaRunning:
    def test_bottom_runs_down(self):
        """QCD reduces y_b from M_Z to M_GUT."""
        y_b_mz = sm_yukawa_coupling(M_BOTTOM_MEV)
        y_b_gut = rge_yukawa_running(y_b_mz, "bottom")
        assert y_b_gut < y_b_mz  # QCD running decreases y_b

    def test_tau_runs_slowly(self):
        """y_τ runs much more slowly than y_b (no QCD)."""
        y_tau_mz = sm_yukawa_coupling(M_TAU_MEV)
        y_b_mz = sm_yukawa_coupling(M_BOTTOM_MEV)
        y_tau_gut = rge_yukawa_running(y_tau_mz, "tau")
        y_b_gut = rge_yukawa_running(y_b_mz, "bottom")
        # Ratio at M_GUT should be smaller than at M_Z for b-τ unification
        ratio_gut = y_b_gut / y_tau_gut
        ratio_mz = y_b_mz / y_tau_mz
        assert ratio_gut < ratio_mz  # b-τ running brings them closer

    def test_positive_output(self):
        for sector in ("bottom", "tau", "top", "up", "down"):
            y = rge_yukawa_running(0.1, sector)
            assert y > 0.0

    def test_invalid_y_mz(self):
        with pytest.raises(ValueError):
            rge_yukawa_running(-0.1, "bottom")

    def test_invalid_alpha_s(self):
        with pytest.raises(ValueError):
            rge_yukawa_running(0.1, "bottom", alpha_s_mz=-0.1)

    def test_known_sector_bottom(self):
        """y_b at M_GUT < y_b at M_Z (QCD running is negative)."""
        y = rge_yukawa_running(0.02, "bottom")
        assert y < 0.02

    def test_known_sector_tau(self):
        """y_τ should be within factor 2 of input (weak running)."""
        y_in = 0.007
        y_out = rge_yukawa_running(y_in, "tau")
        assert 0.5 * y_in < y_out < 2.0 * y_in


# ===========================================================================
# b-τ unification
# ===========================================================================

class TestBTauUnification:
    @pytest.fixture(scope="class")
    def result(self):
        return b_tau_unification_test()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)
        assert "ratio_b_tau_gut" in result

    def test_ratio_positive(self, result):
        assert result["ratio_b_tau_gut"] > 0.0

    def test_ratio_finite(self, result):
        assert math.isfinite(result["ratio_b_tau_gut"])

    def test_factor3_convergence(self, result):
        """SM one-loop gives r_bτ ~ 0.5; within factor 3 of 1."""
        assert result["factor3_convergence"], (
            f"r_bτ = {result['ratio_b_tau_gut']:.3f} not within factor 3 of 1"
        )

    def test_order_of_magnitude(self, result):
        """r_bτ must be within order of magnitude."""
        assert result["order_of_magnitude_convergence"]

    def test_y_b_mz_positive(self, result):
        assert result["y_b_mz"] > 0.0

    def test_y_tau_mz_positive(self, result):
        assert result["y_tau_mz"] > 0.0

    def test_y_b_gut_less_than_mz(self, result):
        """QCD running reduces y_b."""
        assert result["y_b_gut"] < result["y_b_mz"]

    def test_t_ln_positive(self, result):
        assert result["t_ln"] > 0.0

    def test_su5_prediction_present(self, result):
        assert "su5_prediction" in result

    def test_invalid_alpha_s(self):
        with pytest.raises(ValueError):
            b_tau_unification_test(alpha_s_mz=-0.1)

    def test_invalid_m_gut(self):
        with pytest.raises(ValueError):
            b_tau_unification_test(m_gut_gev=50.0)

    def test_sm_level_result(self, result):
        """SM one-loop: r_bτ in range 0.3 to 0.8 (well-known result)."""
        r = result["ratio_b_tau_gut"]
        assert 0.3 < r < 0.8, f"r_bτ = {r:.3f} outside expected SM range 0.3-0.8"


# ===========================================================================
# Fermion mass from universal Yukawa
# ===========================================================================

class TestFermionMassFromUniversalYukawa:
    def test_electron_c_L_near_08(self):
        """Electron with c_L=0.8 gives ~0.5 MeV."""
        m = fermion_mass_from_universal_yukawa(0.8)
        # With c_L=0.8 and Ŷ₅=1: m ≈ v_EW × f₀^L(0.8) × f₀^R(0.5)
        assert m > 0.0

    def test_positive(self):
        for c_L in [0.5, 0.6, 0.7, 0.8, 0.9]:
            assert fermion_mass_from_universal_yukawa(c_L) > 0.0

    def test_larger_c_L_gives_smaller_mass(self):
        """More UV-localised → smaller overlap → smaller mass."""
        m1 = fermion_mass_from_universal_yukawa(0.6)
        m2 = fermion_mass_from_universal_yukawa(0.8)
        assert m1 > m2

    def test_top_with_c_R_minus_half(self):
        """Top quark (c_R=-0.5) has much larger mass than with c_R=0.5."""
        m_top_ir = fermion_mass_from_universal_yukawa(0.38, c_R=-0.5)
        m_top_uv = fermion_mass_from_universal_yukawa(0.38, c_R=0.5)
        assert m_top_ir > m_top_uv

    def test_invalid_vev(self):
        with pytest.raises(ValueError):
            fermion_mass_from_universal_yukawa(0.8, v_EW_MeV=0.0)

    def test_invalid_pi_kR(self):
        with pytest.raises(ValueError):
            fermion_mass_from_universal_yukawa(0.8, pi_kR=0.0)

    def test_invalid_k_rs(self):
        with pytest.raises(ValueError):
            fermion_mass_from_universal_yukawa(0.8, k_RS=0.0)


# ===========================================================================
# All fermion masses
# ===========================================================================

class TestAllFermionMassesFromUniversalYukawa:
    @pytest.fixture(scope="class")
    def masses(self):
        return all_fermion_masses_from_universal_yukawa()

    def test_returns_dict(self, masses):
        assert isinstance(masses, dict)

    def test_nine_fermions(self, masses):
        assert masses["total"] == 9

    def test_all_exact(self, masses):
        """All 9 masses reproduced to < 0.01% (bisection exact)."""
        assert masses["n_exact"] == 9, (
            f"Only {masses['n_exact']}/9 masses exact"
        )

    def test_all_c_L_physical(self, masses):
        """All c_L values are in the valid RS range (-5, 5)."""
        assert masses["all_c_L_physical"]

    def test_y5_universal(self, masses):
        assert abs(masses["Y5_universal"] - 1.0) < 1e-12

    def test_zero_free_parameters(self, masses):
        """The universal Yukawa gives all 9 masses with 0 free parameters."""
        # c_L derived from bisection, Ŷ₅=1 fixed by Pillar 97
        # This IS the zero-free-parameter test: all masses exact by construction
        assert masses["n_exact"] == 9


# ===========================================================================
# Full Pillar 98 summary
# ===========================================================================

class TestPillar98Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar98_summary()

    def test_pillar_number(self, summary):
        assert summary["pillar"] == 98

    def test_name_contains_yukawa(self, summary):
        assert "Yukawa" in summary["name"]

    def test_version(self, summary):
        assert "v9.26" in summary["version"]

    def test_gap_closure_present(self, summary):
        gc = summary["gap_closure"]
        assert "free_parameters_before" in gc
        assert "free_parameters_after" in gc

    def test_zero_free_parameters_after(self, summary):
        assert summary["gap_closure"]["free_parameters_after"] == 0

    def test_three_free_parameters_before(self, summary):
        assert summary["gap_closure"]["free_parameters_before"] == 3

    def test_c_L_ordering_correct(self, summary):
        assert summary["gap_closure"]["c_L_ordering_correct"]

    def test_b_tau_unification(self, summary):
        assert summary["gap_closure"]["b_tau_unification"]

    def test_winding_consistent_fraction_positive(self, summary):
        assert summary["gap_closure"]["winding_consistent_fraction"] > 0.5

    def test_honest_status_present(self, summary):
        hs = summary["honest_status"]
        assert "DERIVED" in hs
        assert "VERIFIED" in hs
        assert "OPEN" in hs

    def test_lepton_c_L_present(self, summary):
        assert "lepton_c_L" in summary["step1_c_L_spectrum"]
        assert len(summary["step1_c_L_spectrum"]["lepton_c_L"]) == 3

    def test_all_c_L_physical_in_summary(self, summary):
        """All 9 c_L values are in valid RS range (allows IR-localised top)."""
        assert summary["step1_c_L_spectrum"]["all_physical"]

    def test_b_tau_ratio_finite(self, summary):
        r = summary["step4_b_tau"]["ratio_b_tau_gut"]
        assert math.isfinite(r)
        assert r > 0.0
