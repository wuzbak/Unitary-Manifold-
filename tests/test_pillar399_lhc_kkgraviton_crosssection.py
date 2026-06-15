# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar399_lhc_kkgraviton_crosssection.py
====================================================
Tests for Pillar 399 — LHC KK Graviton Cross-Section.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar399_lhc_kkgraviton_crosssection import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    M_KK_GEV,
    PI_KR,
    K_CS,
    M_PL_BAR_GEV,
    BESSEL_J1_X1,
    LHC_BENCHMARK_C,
    LHC_EXCLUSION_SENSITIVITY_PB,
    C1_UM,
    CL_U_QUARK,
    CL_D_QUARK,
    CL_CRITICAL,
    lhc_kk_coupling_from_um_geometry,
    fermion_channel_effective_coupling,
    gluon_channel_coupling,
    lhc_kk_exclusion_verdict,
    admission_10_closure_verdict,
    pillar399_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 399

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_k_cs(self):
        assert K_CS == 74

    def test_m_kk_gev(self):
        assert M_KK_GEV == pytest.approx(1040.0, rel=1e-6)

    def test_m_pl_bar_gev_order(self):
        """M̄_Pl should be ~2.4 × 10¹⁸ GeV."""
        assert 2.0e18 < M_PL_BAR_GEV < 3.0e18

    def test_bessel_x1(self):
        assert BESSEL_J1_X1 == pytest.approx(3.8317, rel=1e-4)

    def test_lhc_benchmark_c(self):
        assert LHC_BENCHMARK_C == pytest.approx(0.1, rel=1e-9)

    def test_c1_um_order_unity(self):
        """c₁ = k/M̄_Pl should be O(1), not exp(-37)."""
        assert 0.5 < C1_UM < 3.0

    def test_c1_um_formula(self):
        """Verify c₁ = M_KK × exp(+πkR) / (x₁ × M̄_Pl)."""
        expected = M_KK_GEV * math.exp(PI_KR) / (BESSEL_J1_X1 * M_PL_BAR_GEV)
        assert C1_UM == pytest.approx(expected, rel=1e-8)

    def test_cl_u_uv_localised(self):
        """u-quark c_L > 0.5 (UV-localised)."""
        assert CL_U_QUARK > CL_CRITICAL

    def test_cl_d_uv_localised(self):
        """d-quark c_L > 0.5 (UV-localised)."""
        assert CL_D_QUARK > CL_CRITICAL

    def test_pillar_status(self):
        assert PILLAR_STATUS == "CONSTRAINED_QUANTIFIED"


# ─────────────────────────────────────────────────────────────────────────────
# Coupling calculation
# ─────────────────────────────────────────────────────────────────────────────

class TestLhcKkCoupling:
    @pytest.fixture(scope="class")
    def result(self):
        return lhc_kk_coupling_from_um_geometry()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_c1_correct_order_unity(self, result):
        """Correct c₁ = k/M̄_Pl is O(1)."""
        assert 0.5 < result["c1_correct"] < 3.0

    def test_c1_correct_approx(self, result):
        """c₁ ≈ 1.3 for UM parameters."""
        assert result["c1_correct"] == pytest.approx(1.31, abs=0.1)

    def test_c1_pillar187_small(self, result):
        """Pillar 187's incorrect formula gives tiny value."""
        assert result["c1_pillar187_incorrect"] < 1e-10

    def test_c1_much_larger_than_pillar187(self, result):
        """Correct c₁ is many orders larger than Pillar 187's value."""
        ratio = result["c1_correct"] / result["c1_pillar187_incorrect"]
        assert ratio > 1e10

    def test_c1_vs_benchmark_ratio_large(self, result):
        """c₁/c_benchmark >> 1."""
        assert result["c1_vs_benchmark_ratio"] > 5.0

    def test_correction_note(self, result):
        """Correction note mentions Pillar 187 error."""
        assert "Pillar 187" in result["correction_note"]
        assert "incorrect" in result["correction_note"].lower() or "error" in result["correction_note"].lower() or "conflat" in result["correction_note"].lower()

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert len(result["verdict"]) > 20

    def test_k_gev_order_planck(self, result):
        """k should be ~ M_Pl (order 10¹⁸ GeV)."""
        assert 1e17 < result["k_gev"] < 1e20


# ─────────────────────────────────────────────────────────────────────────────
# Fermion channel coupling
# ─────────────────────────────────────────────────────────────────────────────

class TestFermionChannelCoupling:
    def test_u_quark_returns_dict(self):
        result = fermion_channel_effective_coupling(CL_U_QUARK)
        assert isinstance(result, dict)

    def test_u_quark_uv_class(self):
        result = fermion_channel_effective_coupling(CL_U_QUARK)
        assert result["zone"] == "UV-class"

    def test_u_quark_suppression_small(self):
        """UV-localisation suppression for c_L=0.7 is ~6×10⁻⁴."""
        result = fermion_channel_effective_coupling(0.70)
        assert result["uv_suppression_factor"] == pytest.approx(
            math.exp(-0.20 * 37.0), rel=1e-6
        )

    def test_u_quark_c1_eff_tiny(self):
        """Effective coupling for u-quark << LHC benchmark."""
        result = fermion_channel_effective_coupling(CL_U_QUARK)
        assert result["c1_eff"] < LHC_BENCHMARK_C

    def test_u_quark_safe_from_lhc(self):
        """Fermion channel is safe."""
        result = fermion_channel_effective_coupling(CL_U_QUARK)
        assert result["safe_from_lhc"] is True

    def test_d_quark_safe_from_lhc(self):
        """d-quark fermion channel is safe."""
        result = fermion_channel_effective_coupling(CL_D_QUARK)
        assert result["safe_from_lhc"] is True

    def test_sigma_ratio_fermion_small(self):
        """Fermion σ_UM / σ_benchmark << 1."""
        result = fermion_channel_effective_coupling(CL_U_QUARK)
        assert result["sigma_ratio_vs_benchmark"] < 1e-3

    def test_ir_localised_fermion_not_suppressed(self):
        """IR-localised fermion (c_L < 0.5) has no UV suppression."""
        result = fermion_channel_effective_coupling(0.20)  # IR-class
        assert result["zone"] == "IR-class"
        assert result["uv_suppression_factor"] == pytest.approx(1.0, rel=1e-10)

    def test_cl_critical_exactly_unity_suppression(self):
        """At c_L = 0.5 exactly, suppression = 1."""
        result = fermion_channel_effective_coupling(0.50)
        assert result["uv_suppression_factor"] == pytest.approx(1.0, abs=1e-10)

    def test_verdict_string(self):
        result = fermion_channel_effective_coupling(CL_U_QUARK)
        assert isinstance(result["verdict"], str)
        assert "SAFE" in result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# Gluon channel coupling
# ─────────────────────────────────────────────────────────────────────────────

class TestGluonChannelCoupling:
    @pytest.fixture(scope="class")
    def result(self):
        return gluon_channel_coupling()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_c1_correct(self, result):
        assert result["c1"] == pytest.approx(C1_UM, rel=1e-6)

    def test_sigma_ratio_large(self, result):
        """Gluon channel σ_UM / σ_benchmark > 100."""
        assert result["sigma_ratio_vs_benchmark"] > 100.0

    def test_sigma_ratio_formula(self, result):
        expected = (C1_UM / LHC_BENCHMARK_C) ** 2
        assert result["sigma_ratio_vs_benchmark"] == pytest.approx(expected, rel=1e-6)

    def test_in_tension_true(self, result):
        assert result["in_tension"] is True

    def test_caveat_mentions_b_mu(self, result):
        """Caveat should mention the B_μ coupling uncertainty."""
        assert "B_μ" in result["caveat"] or "B_mu" in result["caveat"] or "irreversibility" in result["caveat"]

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "TENSION" in result["verdict"]

    def test_gluon_coupling_scales_c1_squared(self):
        """Cross-section ratio scales as c₁²."""
        r1 = gluon_channel_coupling(c1=0.5)["sigma_ratio_vs_benchmark"]
        r2 = gluon_channel_coupling(c1=1.0)["sigma_ratio_vs_benchmark"]
        assert r2 / r1 == pytest.approx(4.0, rel=1e-6)


# ─────────────────────────────────────────────────────────────────────────────
# Full exclusion verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestLhcKkExclusionVerdict:
    @pytest.fixture(scope="class")
    def result(self):
        return lhc_kk_exclusion_verdict()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_admission_number(self, result):
        assert result["admission"] == 10

    def test_c1_correct_order_unity(self, result):
        assert 0.5 < result["c1_correct"] < 3.0

    def test_fermion_channels_safe(self, result):
        assert result["fermion_channels_safe"] is True

    def test_gluon_in_tension(self, result):
        assert result["gluon_channel_in_tension"] is True

    def test_overall_status(self, result):
        assert result["overall_status"] == "CONSTRAINED_QUANTIFIED"

    def test_admission_10_status_contains_fermion(self, result):
        status = result["admission_10_status"]
        assert "fermion" in status.lower() or "SAFE" in status

    def test_admission_10_status_contains_gluon(self, result):
        status = result["admission_10_status"]
        assert "gluon" in status.lower() or "TENSION" in status

    def test_m_gkk1_tev_range(self, result):
        assert 3.0 < result["m_gkk1_tev"] < 5.0

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert len(result["verdict"]) > 30

    def test_citation(self, result):
        assert "399" in result["citation"]

    def test_correction_note(self, result):
        """Correction note about Pillar 187 error."""
        assert "Pillar 187" in result["correction_note"]


# ─────────────────────────────────────────────────────────────────────────────
# Admission 10 closure verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission10ClosureVerdict:
    @pytest.fixture(scope="class")
    def verdict(self):
        return admission_10_closure_verdict()

    def test_returns_dict(self, verdict):
        assert isinstance(verdict, dict)

    def test_admission_number(self, verdict):
        assert verdict["admission"] == 10

    def test_previous_status(self, verdict):
        assert verdict["previous_status"] == "CONSTRAINED"

    def test_new_status(self, verdict):
        assert verdict["new_status"] == "CONSTRAINED_QUANTIFIED"

    def test_c1_correct_order_unity(self, verdict):
        assert 0.5 < verdict["c1_correct"] < 3.0

    def test_fermion_channels_safe(self, verdict):
        assert verdict["fermion_channels_safe"] is True

    def test_gluon_in_tension(self, verdict):
        assert verdict["gluon_channel_in_tension"] is True

    def test_key_finding(self, verdict):
        assert isinstance(verdict["key_finding"], str)
        assert "Pillar 187" in verdict["key_finding"] or "1.3" in verdict["key_finding"] or "c₁" in verdict["key_finding"]

    def test_path_forward(self, verdict):
        assert isinstance(verdict["path_forward"], str)
        assert len(verdict["path_forward"]) > 20

    def test_citation(self, verdict):
        assert "399" in verdict["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar399Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar399_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_pillar_number(self, summary):
        assert summary["pillar_number"] == 399

    def test_admission_number(self, summary):
        assert summary["admission"] == 10

    def test_status(self, summary):
        assert summary["status"] == "CONSTRAINED_QUANTIFIED"

    def test_c1_correct_order_unity(self, summary):
        assert 0.5 < summary["c1_correct"] < 3.0

    def test_c1_pillar187_incorrect_tiny(self, summary):
        assert summary["c1_pillar187_incorrect"] < 1e-10

    def test_fermion_u_sigma_ratio_small(self, summary):
        assert summary["fermion_u_sigma_ratio"] < 1e-3

    def test_gluon_sigma_ratio_large(self, summary):
        assert summary["gluon_sigma_ratio"] > 100.0

    def test_fermion_channels_safe(self, summary):
        assert summary["fermion_channels_safe"] is True

    def test_gluon_in_tension(self, summary):
        assert summary["gluon_in_tension"] is True

    def test_key_result(self, summary):
        assert isinstance(summary["key_result"], str)
        assert len(summary["key_result"]) > 30

    def test_honest_residual(self, summary):
        assert isinstance(summary["honest_residual"], str)
        assert "gluon" in summary["honest_residual"].lower() or "B_μ" in summary["honest_residual"]
