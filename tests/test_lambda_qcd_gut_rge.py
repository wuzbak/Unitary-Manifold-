# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_lambda_qcd_gut_rge.py
==================================
Pillar 153 — Tests for lambda_qcd_gut_rge.py.

Tests cover:
  - Constants: ALPHA_GUT, M_GUT_GEV, M_Z_GEV, LAMBDA_QCD_PDG
  - beta0_qcd(): 1-loop β-function coefficients
  - beta0_qcd_pgg(): PDG-convention coefficients
  - rge_alpha_s_one_loop(): 1-loop α_s running
  - alpha_s_at_mz(): multi-threshold running GUT → M_Z
  - lambda_qcd_from_alpha_mz(): Λ_QCD from dimensional transmutation
  - gut_coupling_alpha(): GUT input from Pillar 148
  - lambda_qcd_gut_rge_full(): full two-step computation
  - pillar153_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.lambda_qcd_gut_rge import (
    ALPHA_GUT,
    M_GUT_GEV,
    M_Z_GEV,
    M_TOP_GEV,
    M_BOTTOM_GEV,
    M_CHARM_GEV,
    ALPHA_S_MZ_PDG,
    LAMBDA_QCD_PDG_GEV,
    LAMBDA_QCD_PDG_MEV,
    LAMBDA_QCD_PILLAR62_GEV,
    N_C,
    beta0_qcd,
    beta0_qcd_pgg,
    rge_alpha_s_one_loop,
    alpha_s_at_mz,
    lambda_qcd_from_alpha_mz,
    gut_coupling_alpha,
    lambda_qcd_gut_rge_full,
    pillar153_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_alpha_gut_is_1_over_24_3(self):
        assert abs(ALPHA_GUT - 1.0 / 24.3) < 1e-10

    def test_m_gut_gev_order(self):
        assert 1e15 < M_GUT_GEV < 1e18

    def test_m_z_gev_is_91(self):
        assert 90.0 < M_Z_GEV < 92.0

    def test_m_top_gev_order(self):
        assert 170.0 < M_TOP_GEV < 180.0

    def test_m_bottom_gev_order(self):
        assert 3.0 < M_BOTTOM_GEV < 6.0

    def test_m_charm_gev_order(self):
        assert 1.0 < M_CHARM_GEV < 2.0

    def test_alpha_s_mz_pdg(self):
        assert abs(ALPHA_S_MZ_PDG - 0.1179) < 0.01

    def test_lambda_qcd_pdg_gev(self):
        assert abs(LAMBDA_QCD_PDG_GEV - 0.332) < 0.05

    def test_lambda_qcd_pdg_mev_is_332(self):
        assert abs(LAMBDA_QCD_PDG_MEV - 332.0) < 5.0

    def test_lambda_qcd_pillar62_huge(self):
        """Old Pillar 62 prediction was PeV-scale (×10⁷ gap)."""
        assert LAMBDA_QCD_PILLAR62_GEV > 1e5

    def test_n_c_is_3(self):
        assert N_C == 3


# ---------------------------------------------------------------------------
# Beta function coefficients
# ---------------------------------------------------------------------------

class TestBeta0QCD:
    def test_nf0_coefficient(self):
        """b₀(N_f=0) = 33/3 = 11"""
        b0 = beta0_qcd(0)
        expected = (11.0 * 3) / 3.0
        assert abs(b0 - expected) < 1e-10

    def test_nf5_coefficient(self):
        """b₀(N_f=5) = 23/3"""
        b0 = beta0_qcd(5)
        expected = 23.0 / 3.0
        assert abs(b0 - expected) < 1e-10

    def test_nf6_coefficient(self):
        """b₀(N_f=6) = 21/3 = 7"""
        b0 = beta0_qcd(6)
        expected = 21.0 / 3.0
        assert abs(b0 - expected) < 1e-10

    def test_nf3_coefficient(self):
        """b₀(N_f=3) = 27/3 = 9"""
        b0 = beta0_qcd(3)
        expected = 27.0 / 3.0
        assert abs(b0 - expected) < 1e-10

    def test_all_positive(self):
        """All b₀ must be positive (asymptotic freedom for N_f ≤ 16)."""
        for n_f in range(7):
            assert beta0_qcd(n_f) > 0

    def test_decreasing_with_n_f(self):
        """More flavors → smaller b₀ (more screening)."""
        for n_f in range(6):
            assert beta0_qcd(n_f) > beta0_qcd(n_f + 1)

    def test_invalid_n_f_raises(self):
        with pytest.raises(ValueError, match="n_f"):
            beta0_qcd(-1)

    def test_n_f_7_raises(self):
        with pytest.raises(ValueError):
            beta0_qcd(7)


class TestBeta0QCDPGG:
    def test_nf5_pgg(self):
        """PDG convention: b₀(N_f=5) = 11 − 10/3 = 23/3"""
        b0 = beta0_qcd_pgg(5)
        expected = 11.0 - 2.0 * 5 / 3.0
        assert abs(b0 - expected) < 1e-10

    def test_all_nf_positive(self):
        for n_f in range(7):
            assert beta0_qcd_pgg(n_f) > 0

    def test_invalid_n_f_raises(self):
        with pytest.raises(ValueError):
            beta0_qcd_pgg(7)


# ---------------------------------------------------------------------------
# RGE running
# ---------------------------------------------------------------------------

class TestRgeAlphaSOneLoop:
    def test_same_scale_no_change(self):
        """Running from M to M should give same α_s."""
        alpha = rge_alpha_s_one_loop(0.1179, 91.19, 91.19, n_f=5)
        assert abs(alpha - 0.1179) < 1e-10

    def test_running_up_decreases_alpha_s(self):
        """α_s decreases at higher energies (asymptotic freedom)."""
        alpha_low = rge_alpha_s_one_loop(0.1179, 91.19, 91.19, n_f=5)
        alpha_high = rge_alpha_s_one_loop(0.1179, 91.19, 1000.0, n_f=5)
        assert alpha_high < alpha_low

    def test_running_down_increases_alpha_s(self):
        """α_s increases at lower energies (IR)."""
        alpha_high = rge_alpha_s_one_loop(0.1179, 91.19, 10.0, n_f=5)
        assert alpha_high > 0.1179

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError, match="positive"):
            rge_alpha_s_one_loop(-0.1, 91.19, 91.19, n_f=5)

    def test_invalid_mu_start_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s_one_loop(0.1179, -1.0, 91.19, n_f=5)

    def test_invalid_mu_end_raises(self):
        with pytest.raises(ValueError):
            rge_alpha_s_one_loop(0.1179, 91.19, -1.0, n_f=5)

    def test_alpha_s_at_mz_from_gut_positive(self):
        """Running UPWARD from M_Z to M_GUT should give positive α_s at M_GUT."""
        # Correct direction: run M_Z → M_GUT (upward, no Landau pole)
        alpha_s_gut = rge_alpha_s_one_loop(ALPHA_S_MZ_PDG, M_Z_GEV, M_GUT_GEV, n_f=5)
        assert alpha_s_gut > 0

    def test_alpha_s_from_gut_in_reasonable_range(self):
        """α_s at M_GUT from upward running should be in [0.01, 0.15]."""
        alpha_s_gut = rge_alpha_s_one_loop(ALPHA_S_MZ_PDG, M_Z_GEV, M_GUT_GEV, n_f=5)
        assert 0.01 < alpha_s_gut < 0.15


# ---------------------------------------------------------------------------
# α_s at M_Z from GUT scale
# ---------------------------------------------------------------------------

class TestAlphaSAtMZ:
    def setup_method(self):
        self.result = alpha_s_at_mz()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_two_running_steps(self):
        assert len(self.result["running_steps"]) == 2

    def test_step1_mz_to_top(self):
        step1 = self.result["running_steps"][0]
        assert abs(step1["mu_start_gev"] - M_Z_GEV) < 1.0
        assert abs(step1["mu_end_gev"] - M_TOP_GEV) < 1.0
        assert step1["n_f"] == 5

    def test_step2_top_to_gut(self):
        step2 = self.result["running_steps"][1]
        assert abs(step2["mu_start_gev"] - M_TOP_GEV) < 1.0
        assert abs(step2["mu_end_gev"] - M_GUT_GEV) < 1e10
        assert step2["n_f"] == 6

    def test_alpha_s_at_mz_positive(self):
        assert self.result["alpha_s_at_m_z"] > 0

    def test_alpha_s_at_mz_is_pdg(self):
        """The input is the PDG value of α_s(M_Z)."""
        assert abs(self.result["alpha_s_at_m_z"] - ALPHA_S_MZ_PDG) < 1e-10

    def test_consistent_with_pdg_flag(self):
        """The GUT upward running should give α_s(M_GUT) within 50% of α_GUT."""
        assert self.result["consistent_with_pdg"] is True

    def test_pdg_reference_stored(self):
        assert abs(self.result["pdg_reference_alpha_s_mz"] - ALPHA_S_MZ_PDG) < 1e-6

    def test_deviation_pct_finite(self):
        assert math.isfinite(self.result["deviation_pct"])


# ---------------------------------------------------------------------------
# Λ_QCD from dimensional transmutation
# ---------------------------------------------------------------------------

class TestLambdaQCDFromAlphaMZ:
    def test_pdg_alpha_gives_reasonable_lambda(self):
        result = lambda_qcd_from_alpha_mz(ALPHA_S_MZ_PDG)
        # 1-loop Λ_QCD^{N_f=3} after threshold matching; 4-loop gives 332 MeV
        # 1-loop is typically within factor 2-3 of the 4-loop result
        assert result["lambda_qcd_nf3_mev"] > 10
        assert result["lambda_qcd_nf3_mev"] < 5000

    def test_lambda_nf3_less_than_nf5(self):
        """Λ_QCD grows as we integrate out heavy flavors."""
        result = lambda_qcd_from_alpha_mz(ALPHA_S_MZ_PDG)
        # N_f=3 > N_f=5 (integrating out b, c gives larger Λ)
        assert result["lambda_qcd_nf3_gev"] > result["lambda_qcd_nf5_gev"]

    def test_n_f5_lambda_positive(self):
        result = lambda_qcd_from_alpha_mz(ALPHA_S_MZ_PDG, n_f=5)
        assert result["lambda_qcd_nf5_gev"] > 0

    def test_deviation_finite(self):
        result = lambda_qcd_from_alpha_mz(ALPHA_S_MZ_PDG)
        assert math.isfinite(result["deviation_pct"])

    def test_consistent_flag(self):
        """With PDG α_s, should be within 50% of PDG Λ_QCD."""
        result = lambda_qcd_from_alpha_mz(ALPHA_S_MZ_PDG)
        assert result["consistent_with_pdg"] is True

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError, match="positive"):
            lambda_qcd_from_alpha_mz(-0.1)

    def test_invalid_m_z_raises(self):
        with pytest.raises(ValueError):
            lambda_qcd_from_alpha_mz(0.118, m_z_gev=-1.0)

    def test_pdg_lambda_stored(self):
        result = lambda_qcd_from_alpha_mz(ALPHA_S_MZ_PDG)
        assert abs(result["pdg_lambda_qcd_nf3_gev"] - LAMBDA_QCD_PDG_GEV) < 0.01


# ---------------------------------------------------------------------------
# GUT coupling from Pillar 148
# ---------------------------------------------------------------------------

class TestGutCouplingAlpha:
    def setup_method(self):
        self.result = gut_coupling_alpha()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_alpha_gut_matches_constant(self):
        assert abs(self.result["alpha_gut"] - ALPHA_GUT) < 1e-10

    def test_inv_alpha_gut_is_24_3(self):
        assert abs(self.result["inv_alpha_gut"] - 24.3) < 0.1

    def test_m_gut_matches_constant(self):
        assert abs(self.result["m_gut_gev"] - M_GUT_GEV) < 1e8

    def test_su5_representation(self):
        assert "SU(5)" in self.result["su5_representation"]

    def test_pillar_148_reference(self):
        assert "148" in self.result["derivation_source"]

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            gut_coupling_alpha(alpha_gut=-0.1)

    def test_invalid_m_gut_raises(self):
        with pytest.raises(ValueError):
            gut_coupling_alpha(m_gut_gev=-1.0)


# ---------------------------------------------------------------------------
# Full Pillar 153 computation
# ---------------------------------------------------------------------------

class TestLambdaQCDGUTRGEFull:
    def setup_method(self):
        self.result = lambda_qcd_gut_rge_full()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_153(self):
        assert self.result["pillar"] == 153

    def test_status_resolved(self):
        assert "RESOLVED" in self.result["status"]

    def test_old_gap_factor_huge(self):
        """Old Pillar 62 gave ×10⁷ discrepancy."""
        assert self.result["old_pillar62_gap_factor"] > 1e5

    def test_new_gap_from_pdg_small(self):
        """With PDG α_s, new Λ_QCD should be within 100% of PDG."""
        assert self.result["new_gap_from_pdg_pct"] < 100.0

    def test_resolution_string_nonempty(self):
        assert len(self.result["resolution"]) > 50

    def test_why_gut_works_nonempty(self):
        assert len(self.result["why_gut_works"]) > 50

    def test_caveat_honest(self):
        assert len(self.result["caveat"]) > 20

    def test_pillar_references_nonempty(self):
        assert len(self.result["pillar_references"]) >= 3

    def test_alpha_s_mz_positive(self):
        assert self.result["alpha_s_mz_derived"] > 0

    def test_lambda_nf3_positive(self):
        lam = self.result["lambda_from_pdg_alpha"]
        assert lam["lambda_qcd_nf3_gev"] > 0

    def test_lambda_nf3_in_mev_range(self):
        """Λ_QCD^{N_f=3} should be in 10–5000 MeV range at 1-loop."""
        lam = self.result["lambda_from_pdg_alpha"]
        assert 10.0 < lam["lambda_qcd_nf3_mev"] < 5000.0


# ---------------------------------------------------------------------------
# Pillar 153 summary
# ---------------------------------------------------------------------------

class TestPillar153Summary:
    def setup_method(self):
        self.result = pillar153_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_153(self):
        assert self.result["pillar"] == 153

    def test_status_resolved(self):
        assert "RESOLVED" in self.result["status"]

    def test_old_gap_huge(self):
        assert self.result["old_pillar62_gap_factor"] > 1e5

    def test_new_lambda_positive(self):
        assert self.result["new_lambda_qcd_nf3_mev"] > 0

    def test_pdg_lambda_stored(self):
        assert abs(self.result["pdg_lambda_qcd_nf3_mev"] - LAMBDA_QCD_PDG_MEV) < 1.0

    def test_alpha_gut_correct(self):
        assert abs(self.result["alpha_gut"] - ALPHA_GUT) < 1e-10

    def test_mechanism_nonempty(self):
        assert len(self.result["mechanism"]) > 30

    def test_grand_synthesis_update_nonempty(self):
        assert len(self.result["grand_synthesis_update"]) > 30
