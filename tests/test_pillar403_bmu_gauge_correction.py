# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar403_bmu_gauge_correction.py
============================================
Tests for Pillar 403 — B_μ Gauge Kinetic Correction for Gluon→G_KK Channel.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar403_bmu_gauge_correction import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    PI_KR,
    K_CS,
    M_KK_GEV,
    M_PL_BAR_GEV,
    PHI0,
    K_OVER_MPL,
    C1_UM,
    LHC_BENCHMARK_C,
    SIGMA_RATIO_UNCORRECTED,
    ETA_B_SUPPRESSION,
    SIGMA_RATIO_CORRECTED,
    M_G_EFFECTIVE_LIMIT_TEV,
    bmu_overlap_correction,
    wavefunction_renorm_suppression,
    corrected_gluon_sigma_ratio,
    lhc_dijet_mass_limit,
    admission_10_bounded_verdict,
    pillar403_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 403

    def test_pillar_status(self):
        assert PILLAR_STATUS == "CONSTRAINED_BOUNDED"

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_k_cs(self):
        assert K_CS == 74

    def test_m_kk_gev(self):
        assert M_KK_GEV == pytest.approx(1040.0, rel=1e-6)

    def test_phi0_formula(self):
        assert PHI0 == pytest.approx(5.0 * math.pi / 74.0, rel=1e-9)

    def test_c1_um_positive(self):
        assert C1_UM > 0.0

    def test_c1_um_order(self):
        # c₁ ≈ 1.31 (Pillar 399 corrected value, large warp factor)
        assert 0.5 < C1_UM < 5.0

    def test_lhc_benchmark_c(self):
        assert LHC_BENCHMARK_C == pytest.approx(0.1, rel=1e-6)

    def test_sigma_ratio_uncorrected_large(self):
        # σ_UM/σ_benchmark >> 1 for gluon channel
        assert SIGMA_RATIO_UNCORRECTED > 10.0

    def test_eta_b_near_one(self):
        # B_μ correction is small: η_B ≈ 0.97
        assert 0.90 < ETA_B_SUPPRESSION < 1.0

    def test_sigma_ratio_corrected_still_large(self):
        # Correction insufficient to close tension
        assert SIGMA_RATIO_CORRECTED > 1.0

    def test_m_g_limit_tev_positive(self):
        assert M_G_EFFECTIVE_LIMIT_TEV > 0.0


# ─────────────────────────────────────────────────────────────────────────────
# B_μ overlap correction
# ─────────────────────────────────────────────────────────────────────────────

class TestBmuOverlapCorrection:
    def test_returns_dict(self):
        r = bmu_overlap_correction()
        assert isinstance(r, dict)

    def test_r_b_dimensionless_small(self):
        r = bmu_overlap_correction()
        assert r["r_b_dimensionless"] < 0.1

    def test_r_b_dimensionless_positive(self):
        r = bmu_overlap_correction()
        assert r["r_b_dimensionless"] > 0.0

    def test_delta_overlap_small(self):
        r = bmu_overlap_correction()
        assert r["delta_overlap"] < 0.1

    def test_exp_factor_near_one(self):
        r = bmu_overlap_correction()
        # For πkR = 37, 1 - e^{-74} ≈ 1
        assert r["exp_factor"] == pytest.approx(1.0, abs=1e-10)

    def test_interpretation_present(self):
        r = bmu_overlap_correction()
        assert len(r["interpretation"]) > 20

    def test_phi0_in_result(self):
        r = bmu_overlap_correction()
        assert r["phi0"] == pytest.approx(PHI0, rel=1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# Wavefunction renormalization suppression
# ─────────────────────────────────────────────────────────────────────────────

class TestWavefunctionRenormSuppression:
    def test_returns_dict(self):
        r = wavefunction_renorm_suppression()
        assert isinstance(r, dict)

    def test_r_b_positive(self):
        r = wavefunction_renorm_suppression()
        assert r["r_b"] > 0.0

    def test_r_b_small(self):
        # r_B = φ₀² × k/M̄_Pl ≈ (5π/74)² × 0.1 ≈ 0.027
        r = wavefunction_renorm_suppression()
        assert r["r_b"] < 0.1

    def test_eta_b_amplitude_less_one(self):
        r = wavefunction_renorm_suppression()
        assert r["eta_b_amplitude"] < 1.0

    def test_eta_b_cross_section_less_one(self):
        r = wavefunction_renorm_suppression()
        assert r["eta_b_cross_section"] < 1.0

    def test_c1_corrected_less_bare(self):
        r = wavefunction_renorm_suppression()
        assert r["c1_corrected"] < r["c1_bare"]

    def test_sigma_ratio_corrected_still_large(self):
        r = wavefunction_renorm_suppression()
        assert r["sigma_ratio_corrected"] > 1.0

    def test_suppression_pct_small(self):
        r = wavefunction_renorm_suppression()
        assert r["suppression_pct"] < 10.0

    def test_still_in_tension(self):
        r = wavefunction_renorm_suppression()
        assert r["still_in_tension"]

    def test_interpretation_mentions_tension(self):
        r = wavefunction_renorm_suppression()
        assert "IN TENSION" in r["interpretation"] or "tension" in r["interpretation"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# Corrected gluon sigma ratio
# ─────────────────────────────────────────────────────────────────────────────

class TestCorrectedGluonSigmaRatio:
    def test_returns_dict(self):
        r = corrected_gluon_sigma_ratio()
        assert isinstance(r, dict)

    def test_sigma_ratio_pillar399_positive(self):
        r = corrected_gluon_sigma_ratio()
        assert r["sigma_ratio_pillar399"] > 0.0

    def test_sigma_ratio_corrected_less_than_pillar399(self):
        r = corrected_gluon_sigma_ratio()
        assert r["sigma_ratio_corrected"] < r["sigma_ratio_pillar399"]

    def test_sigma_ratio_corrected_still_in_tension(self):
        r = corrected_gluon_sigma_ratio()
        assert r["in_tension"]

    def test_eta_total_between_0_and_1(self):
        r = corrected_gluon_sigma_ratio()
        assert 0.0 < r["eta_total"] < 1.0

    def test_suppression_pct_positive(self):
        r = corrected_gluon_sigma_ratio()
        assert r["suppression_pct"] > 0.0

    def test_c1_effective_positive(self):
        r = corrected_gluon_sigma_ratio()
        assert r["c1_effective"] > 0.0

    def test_verdict_mentions_tension(self):
        r = corrected_gluon_sigma_ratio()
        assert "IN TENSION" in r["verdict"] or "tension" in r["verdict"].lower()

    def test_verdict_mentions_bounded(self):
        r = corrected_gluon_sigma_ratio()
        assert "bounded" in r["verdict"].lower() or "bound" in r["verdict"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# LHC di-jet mass limit
# ─────────────────────────────────────────────────────────────────────────────

class TestLhcDijetMassLimit:
    def test_returns_dict(self):
        r = lhc_dijet_mass_limit()
        assert isinstance(r, dict)

    def test_m_limit_positive(self):
        r = lhc_dijet_mass_limit()
        assert r["m_limit_tev_estimate"] > 0.0

    def test_m_limit_above_m_g_kk1(self):
        r = lhc_dijet_mass_limit()
        assert r["m_limit_tev_estimate"] > r["m_g_kk1_tev"]

    def test_c1_effective_in_result(self):
        r = lhc_dijet_mass_limit()
        assert r["c1_effective"] > 0.0

    def test_disclaimer_present(self):
        r = lhc_dijet_mass_limit()
        assert len(r["disclaimer"]) > 20

    def test_verdict_mentions_tev(self):
        r = lhc_dijet_mass_limit()
        assert "TeV" in r["verdict"]

    def test_m_limit_finite(self):
        r = lhc_dijet_mass_limit()
        assert math.isfinite(r["m_limit_tev_estimate"])


# ─────────────────────────────────────────────────────────────────────────────
# Admission 10 bounded verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission10BoundedVerdict:
    def test_returns_dict(self):
        r = admission_10_bounded_verdict()
        assert isinstance(r, dict)

    def test_admission_number(self):
        r = admission_10_bounded_verdict()
        assert r["admission"] == 10

    def test_previous_status(self):
        r = admission_10_bounded_verdict()
        assert r["previous_status"] == "CONSTRAINED_QUANTIFIED"

    def test_new_status(self):
        r = admission_10_bounded_verdict()
        assert r["new_status"] == "CONSTRAINED_BOUNDED"

    def test_honest_conclusion_present(self):
        r = admission_10_bounded_verdict()
        assert len(r["honest_conclusion"]) > 50

    def test_mass_limit_in_result(self):
        r = admission_10_bounded_verdict()
        assert "TeV" in r["mass_limit"]

    def test_citation_present(self):
        r = admission_10_bounded_verdict()
        assert "pillar403" in r["citation"].lower() or "Pillar 403" in r["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Full summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar403Summary:
    def test_returns_dict(self):
        r = pillar403_summary()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = pillar403_summary()
        assert r["pillar_number"] == 403

    def test_status(self):
        r = pillar403_summary()
        assert r["status"] == "CONSTRAINED_BOUNDED"

    def test_admission_numbers(self):
        r = pillar403_summary()
        assert r["admission"] == 10

    def test_gluon_in_tension(self):
        r = pillar403_summary()
        assert r["gluon_in_tension"]

    def test_honest_residual_present(self):
        r = pillar403_summary()
        assert len(r["honest_residual"]) > 50

    def test_sigma_ratio_corrected_positive(self):
        r = pillar403_summary()
        assert r["sigma_ratio_corrected"] > 0.0

    def test_total_suppression_pct_small(self):
        r = pillar403_summary()
        assert r["total_suppression_pct"] < 20.0

    def test_verdict_dict_present(self):
        r = pillar403_summary()
        assert "verdict_dict" in r
        assert r["verdict_dict"]["new_status"] == "CONSTRAINED_BOUNDED"

    def test_m_limit_tev_positive(self):
        r = pillar403_summary()
        assert r["m_limit_tev"] > 0.0
