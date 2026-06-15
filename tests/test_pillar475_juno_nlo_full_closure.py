# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 475 — JUNO Δm²₃₁ NLO Full-Chain Closure."""
from __future__ import annotations

import math

from src.core.pillar475_juno_nlo_full_closure import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    DM2_31_PDG_EV2,
    DM2_31_LO_EV2,
    DM2_31_NLO_EV2,
    JUNO_PRECISION,
    P_R_CENTRAL,
    P_R_MIN,
    P_R_MAX,
    N_W,
    K_CS,
    rge_tau_yukawa_correction,
    gs_correction,
    twoloop_kk_seesaw_correction,
    seesaw_applied_correction,
    nlo_prediction,
    residual_pct,
    juno_safety_verdict,
    p_r_band_verdict,
    full_chain_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'JUNO_NLO_FULL_CHAIN_SAFE'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 475

    def test_pdg_value(self):
        assert abs(DM2_31_PDG_EV2 - 2.453e-3) < 1e-10

    def test_lo_value(self):
        assert abs(DM2_31_LO_EV2 - 2.400e-3) < 1e-10

    def test_nlo_value(self):
        assert abs(DM2_31_NLO_EV2 - 2.452e-3) < 1e-10

    def test_juno_precision(self):
        assert JUNO_PRECISION == 0.005

    def test_p_r_range(self):
        assert P_R_MIN < P_R_CENTRAL < P_R_MAX
        assert 0.3 <= P_R_MIN <= 0.35
        assert 0.40 <= P_R_MAX <= 0.45

    def test_nw_kcs(self):
        assert N_W == 5
        assert K_CS == 74


class TestRGECorrection:
    def test_positive(self):
        delta = rge_tau_yukawa_correction()
        assert delta > 0.0

    def test_small(self):
        delta = rge_tau_yukawa_correction()
        assert delta < 0.01  # < 1%

    def test_order_of_magnitude(self):
        # Expected: ~1.79e-4 (0.018%)
        delta = rge_tau_yukawa_correction()
        assert 1e-5 < delta < 1e-2

    def test_larger_at_larger_scale_ratio(self):
        # Larger M_KK/m_atm ratio → larger RGE correction
        d1 = rge_tau_yukawa_correction(m_kk_gev=1e3)
        d2 = rge_tau_yukawa_correction(m_kk_gev=1e4)
        assert d2 > d1


class TestGSCorrection:
    def test_negligible(self):
        delta = gs_correction()
        assert delta < 1e-10  # negligible at atmospheric scale

    def test_non_negative(self):
        assert gs_correction() >= 0.0

    def test_zero_at_zero_scale(self):
        assert gs_correction(m_kk_gev=0.0) == 0.0


class TestTwoLoopCorrection:
    def test_returns_float(self):
        delta = twoloop_kk_seesaw_correction()
        assert isinstance(delta, float)

    def test_positive(self):
        assert twoloop_kk_seesaw_correction() > 0.0

    def test_small(self):
        # 2-loop correction should be small (< 5%)
        assert twoloop_kk_seesaw_correction() < 0.05

    def test_zero_at_zero_mass(self):
        assert twoloop_kk_seesaw_correction(m_r_gev=0.0) == 0.0


class TestSeesawCorrection:
    def test_central_value(self):
        delta = seesaw_applied_correction(P_R_CENTRAL)
        assert 0.01 < delta < 0.05  # ~2.16%

    def test_scales_with_p_r(self):
        d1 = seesaw_applied_correction(0.3)
        d2 = seesaw_applied_correction(0.4)
        assert d2 > d1

    def test_zero_at_zero_p_r(self):
        assert seesaw_applied_correction(0.0) == 0.0

    def test_max_less_than_full_seesaw(self):
        # Full seesaw is (246/1000)^2 ≈ 6%
        assert seesaw_applied_correction(1.0) < 0.07


class TestNLOPrediction:
    def test_larger_than_lo(self):
        pred = nlo_prediction()
        assert pred > DM2_31_LO_EV2

    def test_within_juno_range(self):
        pred = nlo_prediction()
        # Should be close to PDG 2.453e-3 eV^2
        assert 2.40e-3 < pred < 2.47e-3

    def test_central_matches_nlo_constant(self):
        pred = nlo_prediction(P_R_CENTRAL)
        # Should be ~ DM2_31_NLO_EV2 = 2.452e-3 eV^2
        assert abs(pred - DM2_31_NLO_EV2) < 0.002e-3  # within 0.2e-3

    def test_scales_with_p_r(self):
        p1 = nlo_prediction(0.30)
        p2 = nlo_prediction(0.43)
        assert p2 > p1

    def test_rge_only(self):
        pred = nlo_prediction(0.0, include_rge=True, include_gs=False, include_seesaw=False)
        assert pred > DM2_31_LO_EV2

    def test_no_correction(self):
        pred = nlo_prediction(0.0, include_rge=False, include_gs=False, include_seesaw=False)
        assert abs(pred - DM2_31_LO_EV2) < 1e-10


class TestResidualPct:
    def test_perfect_match(self):
        assert residual_pct(DM2_31_PDG_EV2) < 1e-10

    def test_lo_residual(self):
        res = residual_pct(DM2_31_LO_EV2)
        # ~2.18%
        assert 2.0 < res < 2.4

    def test_nlo_residual(self):
        res = residual_pct(nlo_prediction(P_R_CENTRAL))
        # Should be < 0.5% JUNO gate
        assert res < 0.5

    def test_nlo_residual_very_small(self):
        res = residual_pct(nlo_prediction(P_R_CENTRAL))
        # Expect < 0.15%
        assert res < 0.15


class TestJUNOSafetyVerdict:
    def test_central_juno_safe(self):
        verdict = juno_safety_verdict(P_R_CENTRAL)
        assert verdict['juno_safe'] is True

    def test_central_status(self):
        verdict = juno_safety_verdict(P_R_CENTRAL)
        assert verdict['status'] == 'JUNO_NLO_SAFE'

    def test_returns_dict(self):
        verdict = juno_safety_verdict(P_R_CENTRAL)
        assert isinstance(verdict, dict)

    def test_residual_small(self):
        verdict = juno_safety_verdict(P_R_CENTRAL)
        assert verdict['residual_pct'] < 0.5

    def test_sigma_less_than_one(self):
        verdict = juno_safety_verdict(P_R_CENTRAL)
        assert verdict['juno_sigma_projection'] < 1.0

    def test_min_p_r_safe(self):
        verdict = juno_safety_verdict(P_R_MIN)
        assert verdict['juno_safe'] is True

    def test_max_p_r_safe(self):
        verdict = juno_safety_verdict(P_R_MAX)
        assert verdict['juno_safe'] is True


class TestBandVerdict:
    def setup_method(self):
        self.band = p_r_band_verdict()

    def test_returns_dict(self):
        assert isinstance(self.band, dict)

    def test_all_safe(self):
        assert self.band['all_safe'] is True

    def test_band_verdict(self):
        assert self.band['band_verdict'] == 'JUNO_NLO_BAND_SAFE'

    def test_max_residual_below_juno(self):
        assert self.band['max_residual_pct'] < 0.5

    def test_has_per_point_results(self):
        assert len(self.band['per_point_results']) > 0

    def test_all_points_safe(self):
        for r in self.band['per_point_results']:
            assert r['juno_safe'] is True, f"Point {r['p_r']:.3f} not safe: {r['residual_pct']:.3f}%"


class TestFullChainReport:
    def setup_method(self):
        self.report = full_chain_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_status(self):
        assert self.report['status'] == 'JUNO_NLO_FULL_CHAIN_SAFE'

    def test_has_corrections(self):
        assert 'corrections' in self.report
        assert 'delta_rge_pct' in self.report['corrections']

    def test_t3_closed(self):
        assert self.report['verdict']['T3_status'] == 'JUNO_NLO_FULL_CHAIN_SAFE'

    def test_nlo_central_safe(self):
        assert self.report['nlo_central']['juno_safe'] is True

    def test_p_r_band_safe(self):
        assert self.report['p_r_band']['all_safe'] is True

    def test_lo_residual_large(self):
        # LO residual should be ~2.18%
        assert self.report['p17_lo_residual_pct'] > 2.0

    def test_total_correction_positive(self):
        corr = self.report['corrections']['total_correction_central_pct']
        assert corr > 2.0  # ~2.18%
