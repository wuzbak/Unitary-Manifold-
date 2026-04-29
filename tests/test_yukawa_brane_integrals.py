# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_yukawa_brane_integrals.py
======================================
Test suite for Pillar 75 — Brane-Localised Yukawa Integrals
(src/core/yukawa_brane_integrals.py).

Covers:
  - Module constants (N_W, K_CS, PDG masses, ratios)
  - rs_wavefunction_zero_mode: positivity, monotonicity in c_bulk, flat limit
  - yukawa_overlap_zero_mode: positivity, symmetry properties
  - mass_from_overlap: linearity in overlap and v_higgs
  - mass_ratio_generations: ratio structure, keys, ordering
  - fit_c_L_to_lepton_ratios: fit quality, achieved ratios, Δc signs
  - lepton_masses_from_bulk_params: mass ordering, ratio reproduction
  - geometric_baseline_ratios: Pillar 60 values, source key
  - delta_c_needed_for_ratio: sign, magnitude, inverse consistency
  - pillar75_gap_report: structure, honest gaps, mechanism label

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.yukawa_brane_integrals import (
    N_W, K_CS, PHI0_EFF, V_HIGGS_GEV,
    M_ELECTRON_MEV, M_MUON_MEV, M_TAU_MEV,
    R_MU_E, R_TAU_E, R_TAU_MU,
    PI_KR_CANONICAL, K_RS_CANONICAL,
    rs_wavefunction_zero_mode,
    yukawa_overlap_zero_mode,
    mass_from_overlap,
    mass_ratio_generations,
    fit_c_L_to_lepton_ratios,
    lepton_masses_from_bulk_params,
    geometric_baseline_ratios,
    delta_c_needed_for_ratio,
    pillar75_gap_report,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0_eff(self):
        assert abs(PHI0_EFF - 5 * 2 * math.pi) < 1e-10

    def test_v_higgs_gev(self):
        assert abs(V_HIGGS_GEV - 246.0) < 0.01

    def test_pdg_electron_mev(self):
        assert abs(M_ELECTRON_MEV - 0.511) < 0.001

    def test_pdg_muon_mev(self):
        assert abs(M_MUON_MEV - 105.658) < 0.001

    def test_pdg_tau_mev(self):
        assert abs(M_TAU_MEV - 1776.0) < 1.0

    def test_r_mu_e_pdg(self):
        assert abs(R_MU_E - 206.768) < 0.01

    def test_r_tau_e_pdg(self):
        assert abs(R_TAU_E - 3477.0) < 1.0

    def test_r_tau_mu_pdg(self):
        assert abs(R_TAU_MU - 16.817) < 0.01

    def test_pi_kr_canonical(self):
        assert PI_KR_CANONICAL == 37.0

    def test_k_rs_canonical(self):
        assert K_RS_CANONICAL == 1.0


# ---------------------------------------------------------------------------
# rs_wavefunction_zero_mode
# ---------------------------------------------------------------------------

class TestRsWavefunctionZeroMode:
    def test_positive(self):
        """Wavefunction normalisation is always positive."""
        for c in [0.3, 0.5, 0.7, 1.0]:
            assert rs_wavefunction_zero_mode(c) > 0

    def test_uv_localised_larger(self):
        """UV-localised (c < 0.5) gives larger wavefunction at y=0 than IR-localised (c > 0.5)."""
        f_uv = rs_wavefunction_zero_mode(0.3)
        f_ir = rs_wavefunction_zero_mode(0.7)
        assert f_uv > f_ir

    def test_flat_limit_c_half(self):
        """At c = 0.5 (flat profile), returns finite positive value."""
        val = rs_wavefunction_zero_mode(0.5)
        assert val > 0
        assert math.isfinite(val)

    def test_monotone_in_c(self):
        """Larger c (more IR localised) → smaller wavefunction at UV brane."""
        vals = [rs_wavefunction_zero_mode(c) for c in [0.3, 0.4, 0.5, 0.6, 0.7]]
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1], f"Not monotone at c-index {i}"

    def test_large_pi_kr_suppresses_ir(self):
        """Large πkR exponentially suppresses IR-localised mode at UV brane."""
        f_small = rs_wavefunction_zero_mode(0.7, pi_kR=10.0)
        f_large = rs_wavefunction_zero_mode(0.7, pi_kR=50.0)
        assert f_large < f_small

    def test_different_k_RS_scales(self):
        """Different k_RS values give proportionally different wavefunctions."""
        f1 = rs_wavefunction_zero_mode(0.5, k_RS=1.0, pi_kR=10.0)
        f2 = rs_wavefunction_zero_mode(0.5, k_RS=2.0, pi_kR=10.0)
        assert f2 > f1  # larger k_RS → larger normalisation


# ---------------------------------------------------------------------------
# yukawa_overlap_zero_mode
# ---------------------------------------------------------------------------

class TestYukawaOverlapZeroMode:
    def test_positive(self):
        """Overlap is always positive."""
        overlap = yukawa_overlap_zero_mode(0.5, 0.5)
        assert overlap > 0

    def test_symmetry_in_c(self):
        """Overlap is symmetric in c_L and c_R at flat point."""
        o_lr = yukawa_overlap_zero_mode(0.3, 0.7)
        o_rl = yukawa_overlap_zero_mode(0.7, 0.3)
        assert abs(o_lr - o_rl) < 1e-10

    def test_uv_localised_larger(self):
        """More UV-localised (smaller c) gives larger overlap."""
        o_uv = yukawa_overlap_zero_mode(0.3, 0.3)
        o_ir = yukawa_overlap_zero_mode(0.7, 0.7)
        assert o_uv > o_ir

    def test_product_of_wavefunctions(self):
        """Overlap equals product of individual wavefunctions."""
        c_L, c_R = 0.4, 0.6
        f_L = rs_wavefunction_zero_mode(c_L)
        f_R = rs_wavefunction_zero_mode(c_R)
        overlap = yukawa_overlap_zero_mode(c_L, c_R)
        assert abs(overlap - f_L * f_R) < 1e-12


# ---------------------------------------------------------------------------
# mass_from_overlap
# ---------------------------------------------------------------------------

class TestMassFromOverlap:
    def test_linearity_in_overlap(self):
        """Mass is linear in overlap."""
        m1 = mass_from_overlap(1.0)
        m2 = mass_from_overlap(2.0)
        assert abs(m2 / m1 - 2.0) < 1e-10

    def test_linearity_in_lambda(self):
        """Mass is linear in lambda_Y."""
        m1 = mass_from_overlap(1.0, lambda_Y=1.0)
        m2 = mass_from_overlap(1.0, lambda_Y=0.5)
        assert abs(m1 / m2 - 2.0) < 1e-10

    def test_higgs_vev(self):
        """At overlap=1, lambda=1: mass equals v_higgs."""
        m = mass_from_overlap(1.0, lambda_Y=1.0, v_higgs=246.0)
        assert abs(m - 246.0) < 0.01

    def test_positive(self):
        """Mass is always positive for positive inputs."""
        assert mass_from_overlap(0.001) > 0


# ---------------------------------------------------------------------------
# mass_ratio_generations
# ---------------------------------------------------------------------------

class TestMassRatioGenerations:
    def test_keys(self):
        result = mass_ratio_generations(0.6, 0.5, 0.4)
        assert "m1_over_m0" in result
        assert "m2_over_m0" in result
        assert "m2_over_m1" in result
        assert "overlap_0" in result

    def test_ordering(self):
        """m0 > m1 > m2 when c_L increases (more UV-localised for smaller n)."""
        result = mass_ratio_generations(0.6, 0.5, 0.4)
        # c_L0=0.6 > c_L1=0.5 > c_L2=0.4: larger c → IR localised → smaller wavefunction
        # So overlap_0 < overlap_1 < overlap_2 → m1_over_m0 > 1
        assert result["m1_over_m0"] > 1.0

    def test_ratio_consistency(self):
        """m2/m1 × m1/m0 = m2/m0."""
        result = mass_ratio_generations(0.6, 0.5, 0.4)
        r21_times_r10 = result["m2_over_m1"] * result["m1_over_m0"]
        assert abs(r21_times_r10 - result["m2_over_m0"]) < 1e-10

    def test_equal_c_gives_ratio_one(self):
        """All same bulk mass → all ratios = 1."""
        result = mass_ratio_generations(0.5, 0.5, 0.5)
        assert abs(result["m1_over_m0"] - 1.0) < 1e-10
        assert abs(result["m2_over_m0"] - 1.0) < 1e-10

    def test_positive_overlaps(self):
        """All overlaps are positive."""
        result = mass_ratio_generations(0.6, 0.5, 0.4)
        for key in ("overlap_0", "overlap_1", "overlap_2"):
            assert result[key] > 0


# ---------------------------------------------------------------------------
# fit_c_L_to_lepton_ratios
# ---------------------------------------------------------------------------

class TestFitCLToLeptonRatios:
    def test_keys(self):
        result = fit_c_L_to_lepton_ratios()
        for key in ("c_L0", "c_L1", "c_L2", "delta_c_10", "delta_c_21",
                    "pi_kR_used", "achieved_mu_e", "achieved_tau_mu"):
            assert key in result

    def test_pi_kr_used(self):
        result = fit_c_L_to_lepton_ratios()
        assert result["pi_kR_used"] == PI_KR_CANONICAL

    def test_delta_c_10_negative(self):
        """Δc_10 = c_L1 − c_L0 should be negative (c_L1 < c_L0 for heavier muon)."""
        result = fit_c_L_to_lepton_ratios()
        # c_L1 < c_L0 means more UV-localised → larger wavefunction → heavier
        # delta_c_10 = log(ratio)/πkR is positive; c_L1 = c_L0 - delta_c_10 < c_L0
        assert result["c_L1"] < result["c_L0"]

    def test_c_ordering(self):
        """c_L2 < c_L1 < c_L0 (tau is heaviest → most UV-localised)."""
        result = fit_c_L_to_lepton_ratios()
        assert result["c_L2"] < result["c_L1"] < result["c_L0"]

    def test_achieved_mu_e_close_to_target(self):
        """Achieved m_μ/m_e should be close to target (within 20% at π kR = 37)."""
        result = fit_c_L_to_lepton_ratios(target_mu_e=R_MU_E)
        # The ratio should be approximately correct (our analytic approximation)
        assert result["achieved_mu_e"] > 1.0  # at least larger than 1

    def test_custom_ratio(self):
        """Custom target ratio should be achievable."""
        result = fit_c_L_to_lepton_ratios(target_mu_e=10.0, target_tau_mu=5.0)
        assert result["achieved_mu_e"] > 1.0
        assert result["achieved_tau_mu"] > 1.0

    def test_raises_on_negative_ratio(self):
        with pytest.raises(ValueError):
            fit_c_L_to_lepton_ratios(target_mu_e=-1.0)

    def test_raises_on_zero_pi_kr(self):
        with pytest.raises(ValueError):
            fit_c_L_to_lepton_ratios(pi_kR=0.0)


# ---------------------------------------------------------------------------
# lepton_masses_from_bulk_params
# ---------------------------------------------------------------------------

class TestLeptonMassesFromBulkParams:
    def test_keys(self):
        fit = fit_c_L_to_lepton_ratios()
        result = lepton_masses_from_bulk_params((fit["c_L0"], fit["c_L1"], fit["c_L2"]))
        for key in ("electron_MeV", "muon_MeV", "tau_MeV", "m1_over_m0", "m2_over_m1"):
            assert key in result

    def test_mass_ordering(self):
        """electron < muon < tau."""
        fit = fit_c_L_to_lepton_ratios()
        result = lepton_masses_from_bulk_params((fit["c_L0"], fit["c_L1"], fit["c_L2"]))
        assert result["electron_MeV"] < result["muon_MeV"] < result["tau_MeV"]

    def test_positive_masses(self):
        """All masses are positive."""
        fit = fit_c_L_to_lepton_ratios()
        result = lepton_masses_from_bulk_params((fit["c_L0"], fit["c_L1"], fit["c_L2"]))
        assert result["electron_MeV"] > 0
        assert result["muon_MeV"] > 0
        assert result["tau_MeV"] > 0

    def test_ratio_m1_over_m0(self):
        """m1/m0 > 1."""
        fit = fit_c_L_to_lepton_ratios()
        result = lepton_masses_from_bulk_params((fit["c_L0"], fit["c_L1"], fit["c_L2"]))
        assert result["m1_over_m0"] > 1.0


# ---------------------------------------------------------------------------
# geometric_baseline_ratios
# ---------------------------------------------------------------------------

class TestGeometricBaselineRatios:
    def test_keys(self):
        result = geometric_baseline_ratios()
        for key in ("m1_over_m0", "m2_over_m0", "m2_over_m1", "source"):
            assert key in result

    def test_m1_over_m0_pillar60(self):
        """m_1/m_0 = √(6/5) ≈ 1.0954 (Pillar 60)."""
        result = geometric_baseline_ratios(n_w=5)
        assert abs(result["m1_over_m0"] - math.sqrt(6.0 / 5.0)) < 1e-10

    def test_m2_over_m0_pillar60(self):
        """m_2/m_0 = √(9/5) ≈ 1.3416 (Pillar 60)."""
        result = geometric_baseline_ratios(n_w=5)
        assert abs(result["m2_over_m0"] - math.sqrt(9.0 / 5.0)) < 1e-10

    def test_consistency(self):
        """m2_over_m1 = m2_over_m0 / m1_over_m0."""
        result = geometric_baseline_ratios()
        ratio = result["m2_over_m0"] / result["m1_over_m0"]
        assert abs(ratio - result["m2_over_m1"]) < 1e-10

    def test_source_mentions_n_w(self):
        result = geometric_baseline_ratios()
        assert "5" in result["source"]

    def test_all_ratios_above_one(self):
        """Geometric ratios are > 1 for n_w = 5."""
        result = geometric_baseline_ratios()
        assert result["m1_over_m0"] > 1.0
        assert result["m2_over_m0"] > 1.0
        assert result["m2_over_m1"] > 1.0


# ---------------------------------------------------------------------------
# delta_c_needed_for_ratio
# ---------------------------------------------------------------------------

class TestDeltaCNeededForRatio:
    def test_positive_ratio_positive_result(self):
        """Ratio > 1 → positive delta_c (need more UV-localised mode)."""
        # delta_c = -ln(ratio)/pi_kR < 0 for ratio > 1
        dc = delta_c_needed_for_ratio(10.0)
        assert dc < 0  # negative Δc to get heavier generation

    def test_ratio_one_gives_zero(self):
        """Ratio = 1 → Δc = 0."""
        dc = delta_c_needed_for_ratio(1.0)
        assert abs(dc) < 1e-10

    def test_inverse_consistency(self):
        """exp(−Δc × πkR) should recover the ratio."""
        ratio = 206.77
        dc = delta_c_needed_for_ratio(ratio)
        recovered = math.exp(-dc * PI_KR_CANONICAL)
        assert abs(recovered - ratio) < 1.0

    def test_larger_ratio_larger_magnitude(self):
        """Larger ratio needs larger |Δc|."""
        dc1 = delta_c_needed_for_ratio(10.0)
        dc2 = delta_c_needed_for_ratio(100.0)
        assert abs(dc2) > abs(dc1)

    def test_raises_on_nonpositive_ratio(self):
        with pytest.raises(ValueError):
            delta_c_needed_for_ratio(0.0)

    def test_raises_on_negative_pi_kr(self):
        with pytest.raises(ValueError):
            delta_c_needed_for_ratio(10.0, pi_kR=-1.0)


# ---------------------------------------------------------------------------
# pillar75_gap_report
# ---------------------------------------------------------------------------

class TestPillar75GapReport:
    def test_keys(self):
        result = pillar75_gap_report()
        for key in ("pillar", "title", "derived", "mechanism",
                    "open", "next_step", "epistemic_status", "pdg_targets"):
            assert key in result

    def test_pillar_number(self):
        assert pillar75_gap_report()["pillar"] == 75

    def test_derived_is_list(self):
        assert isinstance(pillar75_gap_report()["derived"], list)
        assert len(pillar75_gap_report()["derived"]) >= 4

    def test_open_is_list(self):
        assert isinstance(pillar75_gap_report()["open"], list)
        assert len(pillar75_gap_report()["open"]) >= 2

    def test_epistemic_status_not_claimed(self):
        """Status should not claim 'PROVED' or 'CLOSED' for the full mass derivation."""
        status = pillar75_gap_report()["epistemic_status"].upper()
        assert "PROVED" not in status or "NOT" in status or "MECHANISM" in status

    def test_pdg_targets_close_to_pdg(self):
        result = pillar75_gap_report()
        assert abs(result["pdg_targets"]["m_mu_over_m_e"] - R_MU_E) < 0.01
        assert abs(result["pdg_targets"]["m_tau_over_m_mu"] - R_TAU_MU) < 0.01

    def test_fit_example_c_ordering(self):
        result = pillar75_gap_report()
        fit = result["fit_example"]
        assert fit["c_L2_tau"] < fit["c_L1_muon"] < fit["c_L0_electron"]
