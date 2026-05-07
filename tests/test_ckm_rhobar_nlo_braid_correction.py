# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-C: src/core/ckm_rhobar_nlo_braid_correction.py"""

from __future__ import annotations

import math
import pytest

from src.core.ckm_rhobar_nlo_braid_correction import (
    N_W, K_CS, N1_BRAID, N2_BRAID, ALPHA_GUT,
    DELTA_CP_LEADING_DEG,
    DELTA_CP_SUBLEADING_DEG,
    DELTA_CP_NLO1_DEG,
    DELTA_CP_NLO2_DEG,
    DELTA_CP_NLO_AVG_DEG,
    RHO_BAR_PDG,
    RHO_BAR_NLO,
    RHO_BAR_NLO_PCT_ERR,
    GATE_PASSED, WSC_STATUS,
    r_b_geometric,
    delta_cp_leading,
    delta_cp_subleading,
    delta_cp_nlo1,
    delta_cp_nlo2,
    rho_bar_from_delta,
    sensitivity_decomposition,
    delta_ckm_correction_artifact,
    rhobar_sensitivity_pipeline,
    wsc_gate_report,
    pillar_wsc_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n1_n2(self):
        assert N1_BRAID == 5
        assert N2_BRAID == 7

    def test_alpha_gut(self):
        assert ALPHA_GUT == pytest.approx(3.0 / 74.0)

    def test_leading_deg(self):
        assert DELTA_CP_LEADING_DEG == pytest.approx(72.0)

    def test_subleading_lt_leading(self):
        # 2 arctan(5/7) < 72°
        assert DELTA_CP_SUBLEADING_DEG < DELTA_CP_LEADING_DEG

    def test_nlo1_lt_subleading(self):
        assert DELTA_CP_NLO1_DEG < DELTA_CP_SUBLEADING_DEG

    def test_nlo2_lt_subleading(self):
        assert DELTA_CP_NLO2_DEG < DELTA_CP_SUBLEADING_DEG

    def test_nlo_avg_between_nlo1_nlo2(self):
        lo = min(DELTA_CP_NLO1_DEG, DELTA_CP_NLO2_DEG)
        hi = max(DELTA_CP_NLO1_DEG, DELTA_CP_NLO2_DEG)
        assert lo <= DELTA_CP_NLO_AVG_DEG <= hi

    def test_rho_bar_pdg(self):
        assert RHO_BAR_PDG == pytest.approx(0.159, rel=0.01)

    def test_rho_bar_nlo_positive(self):
        assert RHO_BAR_NLO > 0.0

    def test_rho_bar_nlo_pct_err_positive(self):
        assert RHO_BAR_NLO_PCT_ERR > 0.0

    def test_gate_not_passed(self):
        assert GATE_PASSED is False


class TestRbGeometric:
    def test_returns_dict(self):
        assert isinstance(r_b_geometric(), dict)

    def test_vub_positive(self):
        r = r_b_geometric()
        assert r["V_ub_geo"] > 0.0

    def test_a_geo(self):
        r = r_b_geometric()
        assert r["A_geo"] == pytest.approx(math.sqrt(5.0 / 7.0), rel=1e-6)

    def test_r_b_positive(self):
        r = r_b_geometric()
        assert r["R_b"] > 0.0


class TestDeltaCpFunctions:
    def test_leading_72deg(self):
        r = delta_cp_leading()
        assert r["delta_cp_deg"] == pytest.approx(72.0)

    def test_subleading_positive(self):
        r = delta_cp_subleading()
        assert r["delta_cp_deg"] > 0.0

    def test_subleading_lt_72(self):
        r = delta_cp_subleading()
        assert r["delta_cp_deg"] < 72.0

    def test_nlo1_returns_dict(self):
        assert isinstance(delta_cp_nlo1(), dict)

    def test_nlo1_has_correction(self):
        r = delta_cp_nlo1()
        assert r["cross_braid_correction_deg"] > 0.0

    def test_nlo2_returns_dict(self):
        assert isinstance(delta_cp_nlo2(), dict)

    def test_nlo2_loop_factor_positive(self):
        r = delta_cp_nlo2()
        assert r["loop_factor"] > 0.0


class TestRhoBarFromDelta:
    def test_returns_dict(self):
        assert isinstance(rho_bar_from_delta(72.0), dict)

    def test_rho_bar_72_deg(self):
        r = rho_bar_from_delta(72.0)
        assert r["rho_bar"] == pytest.approx(r["R_b"] * math.cos(math.radians(72.0)))

    def test_pct_err_positive(self):
        r = rho_bar_from_delta(72.0)
        assert r["pct_err_vs_pdg"] > 0.0

    def test_pct_err_90deg_large(self):
        r = rho_bar_from_delta(90.0)
        # cos(90°) = 0 → rho = 0 → large error
        assert r["pct_err_vs_pdg"] > 90.0


class TestSensitivityDecomposition:
    def test_returns_dict(self):
        assert isinstance(sensitivity_decomposition(), dict)

    def test_has_nlo_errors(self):
        r = sensitivity_decomposition()
        assert "nlo1_error_pct" in r
        assert "nlo2_error_pct" in r

    def test_improvement_positive(self):
        r = sensitivity_decomposition()
        # NLO corrections should improve (reduce error) vs LO
        assert r["improvement_lo_to_nlo1_pct"] > 0.0

    def test_has_path_to_closure(self):
        r = sensitivity_decomposition()
        assert "7D" in r["path_to_closure"] or "discrete_torsion" in r["path_to_closure"]


class TestDeltaCkmCorrectionArtifact:
    def test_returns_dict(self):
        assert isinstance(delta_ckm_correction_artifact(), dict)

    def test_four_corrections(self):
        r = delta_ckm_correction_artifact()
        assert len(r["corrections"]) == 4

    def test_gate_not_passed(self):
        r = delta_ckm_correction_artifact()
        assert r["gate_lt5pct"] is False

    def test_best_estimate_has_pct_err(self):
        r = delta_ckm_correction_artifact()
        assert "pct_err" in r["best_estimate"]


class TestWscGateReport:
    def test_returns_dict(self):
        assert isinstance(wsc_gate_report(), dict)

    def test_workstream(self):
        assert wsc_gate_report()["workstream"] == "WS-C"

    def test_gate_not_passed(self):
        assert wsc_gate_report()["gate_passed"] is False

    def test_has_all_deliverables(self):
        r = wsc_gate_report()
        assert "deliverable_C1_delta_ckm_artifact" in r
        assert "deliverable_C2_sensitivity_pipeline" in r
        assert "deliverable_C3_gate_report" in r


class TestPillarWscSummary:
    def test_returns_dict(self):
        assert isinstance(pillar_wsc_summary(), dict)

    def test_gate_not_passed(self):
        r = pillar_wsc_summary()
        assert r["gate_passed"] is False

    def test_has_rho_bar_nlo(self):
        r = pillar_wsc_summary()
        assert r["rho_bar_nlo"] > 0.0
