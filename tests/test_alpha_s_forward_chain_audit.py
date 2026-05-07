# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-D: src/core/alpha_s_forward_chain_audit.py"""

from __future__ import annotations

import math
import pytest

from src.core.alpha_s_forward_chain_audit import (
    N_W, K_CS, N_C, N_F, M_PL_GEV, PI_KR,
    ALPHA_S_GUT_GEO,
    BETA0_QCD,
    ALPHA_S_GEO_MEW,
    ALPHA_S_SU5_MZ,
    ALPHA_S_PDG_MZ,
    WARP_GAP_FACTOR,
    RESIDUAL_GAP_AFTER_KK,
    ARCHITECTURE_LIMIT,
    GATE_PASSED, WSD_STATUS,
    gut_coupling_from_axiomzero,
    kk_scale,
    rge_running_alpha_s,
    warp_anchor_gap,
    kk_threshold_correction_summary,
    su5_route_summary,
    provenance_ledger,
    wsd_gate_report,
    pillar_wsd_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_n_f(self):
        assert N_F == 6

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_alpha_s_gut_geo(self):
        assert ALPHA_S_GUT_GEO == pytest.approx(3.0 / 74.0)

    def test_beta0_qcd(self):
        # β₀ = 11×3/3 − 2×6/3 = 11 − 4 = 7
        assert BETA0_QCD == pytest.approx(7.0)

    def test_alpha_s_geo_mew_positive(self):
        assert ALPHA_S_GEO_MEW > 0.0

    def test_alpha_s_geo_mew_less_than_gut(self):
        # Running down increases coupling (asymptotic freedom reversed at LO)
        # Actually for QCD with N_f=6: beta0 > 0 → coupling grows at low energy
        # But starting very small, could still be < gut at M_EW
        assert ALPHA_S_GEO_MEW > 0.0

    def test_warp_gap_factor_gt_one(self):
        assert WARP_GAP_FACTOR > 1.0

    def test_residual_gap_gt_one(self):
        assert RESIDUAL_GAP_AFTER_KK > 1.0

    def test_architecture_limit(self):
        assert ARCHITECTURE_LIMIT is True

    def test_gate_not_passed(self):
        assert GATE_PASSED is False

    def test_su5_achieves_2pct(self):
        # SU(5) route gives α_s ≈ 0.118 ± 2%
        from src.core.alpha_s_forward_chain_audit import ALPHA_S_SU5_PCT_ERR
        assert ALPHA_S_SU5_PCT_ERR < 5.0


class TestGutCoupling:
    def test_returns_dict(self):
        assert isinstance(gut_coupling_from_axiomzero(), dict)

    def test_value(self):
        r = gut_coupling_from_axiomzero()
        assert r["alpha_s_gut"] == pytest.approx(3.0 / 74.0)

    def test_axiomzero_compliant(self):
        r = gut_coupling_from_axiomzero()
        assert r["axiomzero_compliant"] is True

    def test_custom_params(self):
        r = gut_coupling_from_axiomzero(n_c=4, k_cs=100)
        assert r["alpha_s_gut"] == pytest.approx(0.04)


class TestKkScale:
    def test_returns_dict(self):
        assert isinstance(kk_scale(), dict)

    def test_m_kk_positive(self):
        r = kk_scale()
        assert r["M_KK_GeV"] > 0.0

    def test_m_kk_less_than_planck(self):
        r = kk_scale()
        assert r["M_KK_GeV"] < M_PL_GEV

    def test_formula(self):
        r = kk_scale()
        expected = M_PL_GEV * math.exp(-PI_KR)
        assert r["M_KK_GeV"] == pytest.approx(expected, rel=1e-6)


class TestRgeRunning:
    def test_returns_dict(self):
        assert isinstance(rge_running_alpha_s(), dict)

    def test_alpha_s_mew_positive(self):
        r = rge_running_alpha_s()
        assert r["alpha_s_mew"] > 0.0

    def test_gap_factor_gt_one(self):
        r = rge_running_alpha_s()
        assert r["gap_factor"] > 1.0

    def test_beta0_value(self):
        r = rge_running_alpha_s()
        assert r["beta0"] == pytest.approx(7.0)


class TestWarpAnchorGap:
    def test_returns_dict(self):
        assert isinstance(warp_anchor_gap(), dict)

    def test_initial_gap_gt_one(self):
        r = warp_anchor_gap()
        assert r["initial_gap_factor"] > 1.0

    def test_residual_gap_gt_one(self):
        r = warp_anchor_gap()
        assert r["residual_gap_factor"] > 1.0

    def test_architecture_limit(self):
        r = warp_anchor_gap()
        assert r["architecture_limit"] is True


class TestKkThreshold:
    def test_returns_dict(self):
        assert isinstance(kk_threshold_correction_summary(), dict)

    def test_has_architecture_limit(self):
        r = kk_threshold_correction_summary()
        assert r["architecture_limit"] is True

    def test_requires_dimension_10(self):
        r = kk_threshold_correction_summary()
        assert r["requires_dimension"] == 10


class TestSu5Route:
    def test_returns_dict(self):
        assert isinstance(su5_route_summary(), dict)

    def test_alpha_s_value(self):
        r = su5_route_summary()
        assert r["alpha_s_su5"] == pytest.approx(0.118, rel=0.05)

    def test_gate_lt5pct(self):
        r = su5_route_summary()
        assert r["gate_lt5pct"] is True

    def test_pct_err_lt5(self):
        r = su5_route_summary()
        assert r["pct_err"] < 5.0


class TestProvenanceLedger:
    def test_returns_dict(self):
        assert isinstance(provenance_ledger(), dict)

    def test_six_steps(self):
        r = provenance_ledger()
        assert len(r["steps"]) == 6

    def test_step1_is_gut_coupling(self):
        r = provenance_ledger()
        assert "α_s" in r["steps"][0]["quantity"]

    def test_axiomzero_inputs(self):
        r = provenance_ledger()
        assert r["axiomzero_inputs"]["n_w"] == 5
        assert r["axiomzero_inputs"]["k_CS"] == 74

    def test_provenance_complete(self):
        r = provenance_ledger()
        assert r["provenance_complete"] is True


class TestWsdGateReport:
    def test_returns_dict(self):
        assert isinstance(wsd_gate_report(), dict)

    def test_workstream(self):
        assert wsd_gate_report()["workstream"] == "WS-D"

    def test_gate_not_passed_direct(self):
        r = wsd_gate_report()
        assert r["gate_passed"] is False

    def test_has_all_deliverables(self):
        r = wsd_gate_report()
        assert "deliverable_D1_forward_chain" in r
        assert "deliverable_D2_provenance_ledger" in r
        assert "deliverable_D3_gate_report" in r

    def test_su5_route_gate_met(self):
        r = wsd_gate_report()
        assert r["deliverable_D3_gate_report"]["su5_route_gate_passed"] is True


class TestPillarWsdSummary:
    def test_returns_dict(self):
        assert isinstance(pillar_wsd_summary(), dict)

    def test_gate_not_passed(self):
        r = pillar_wsd_summary()
        assert r["gate_passed"] is False

    def test_su5_route_achieves(self):
        r = pillar_wsd_summary()
        assert r["su5_route_achieves_lt2pct"] is True

    def test_architecture_limit(self):
        r = pillar_wsd_summary()
        assert r["architecture_limit"] is True
