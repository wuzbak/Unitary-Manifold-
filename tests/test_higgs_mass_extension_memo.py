# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-F: src/core/higgs_mass_extension_memo.py"""

from __future__ import annotations

import math
import pytest

from src.core.higgs_mass_extension_memo import (
    N_W, K_CS, PI_KR,
    M_H_PDG_GEV, V_HIGGS_GEV, LAMBDA_H_PDG, M_KK_GEV,
    LAMBDA_H_GHU_EST, LAMBDA_H_GHU_PDG_RATIO,
    WSF_STATUS,
    higgs_mass_from_quartic,
    option_ghu,
    option_gw_cw,
    option_dilaton_portal,
    theorem_wsf_1,
    theorem_wsf_2,
    theorem_wsf_3,
    selected_extension_branch,
    wsf_gate_report,
    pillar_wsf_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_m_h_pdg(self):
        assert M_H_PDG_GEV == pytest.approx(125.25, rel=0.01)

    def test_v_higgs(self):
        assert V_HIGGS_GEV == pytest.approx(246.22, rel=0.01)

    def test_lambda_h_pdg(self):
        # λ_H = m_H² / (2v²)
        expected = 125.25 ** 2 / (2 * 246.22 ** 2)
        assert LAMBDA_H_PDG == pytest.approx(expected, rel=1e-4)

    def test_m_kk_gev_positive(self):
        assert M_KK_GEV > 0.0

    def test_lambda_h_ghu_tiny(self):
        # GHU coupling should be extremely small
        assert LAMBDA_H_GHU_EST < 1e-10

    def test_ghu_ratio_extremely_small(self):
        assert LAMBDA_H_GHU_PDG_RATIO < 1e-10

    def test_status_contains_open(self):
        assert "OPEN" in WSF_STATUS or "ARCHITECTURE" in WSF_STATUS


class TestHiggsMassFromQuartic:
    def test_pdg_roundtrip(self):
        r = higgs_mass_from_quartic(LAMBDA_H_PDG)
        assert r["m_h_gev"] == pytest.approx(M_H_PDG_GEV, rel=1e-4)

    def test_pct_err_zero_for_pdg(self):
        r = higgs_mass_from_quartic(LAMBDA_H_PDG)
        assert r["pct_err"] == pytest.approx(0.0, abs=0.01)

    def test_larger_coupling_larger_mass(self):
        r1 = higgs_mass_from_quartic(0.1)
        r2 = higgs_mass_from_quartic(0.2)
        assert r2["m_h_gev"] > r1["m_h_gev"]


class TestOptionGhu:
    def test_returns_dict(self):
        assert isinstance(option_ghu(), dict)

    def test_verdict_is_no_go(self):
        r = option_ghu()
        assert r["verdict"] == "NO-GO"

    def test_kill_switch_triggered(self):
        r = option_ghu()
        assert r["kill_switch_triggered"] is True

    def test_lambda_h_tiny(self):
        r = option_ghu()
        assert r["lambda_h_ghu"] < 1e-10

    def test_ratio_extremely_small(self):
        r = option_ghu()
        assert r["ratio"] < 1e-10


class TestOptionGwCw:
    def test_returns_dict(self):
        assert isinstance(option_gw_cw(), dict)

    def test_verdict_conditional_go(self):
        r = option_gw_cw()
        assert "GO" in r["verdict"]

    def test_one_free_parameter(self):
        r = option_gw_cw()
        assert r["free_parameters_remaining"] == 1

    def test_theta_hr_in_result(self):
        r = option_gw_cw()
        assert "theta_hr" in r["free_parameter_name"].lower() or "θ_HR" in r["free_parameter_name"]


class TestOptionDilatonPortal:
    def test_returns_dict(self):
        assert isinstance(option_dilaton_portal(), dict)

    def test_conditional_go(self):
        r = option_dilaton_portal()
        assert "GO" in r["verdict"]

    def test_two_free_parameters(self):
        r = option_dilaton_portal()
        assert r["free_parameters_remaining"] == 2


class TestTheoremWsf1:
    def test_returns_dict(self):
        assert isinstance(theorem_wsf_1(), dict)

    def test_theorem_id(self):
        r = theorem_wsf_1()
        assert r["theorem_id"] == "WSF-1"

    def test_verdict_no_go(self):
        r = theorem_wsf_1()
        assert r["verdict"] == "NO-GO"


class TestTheoremWsf2:
    def test_returns_dict(self):
        assert isinstance(theorem_wsf_2(), dict)

    def test_theorem_id(self):
        r = theorem_wsf_2()
        assert r["theorem_id"] == "WSF-2"

    def test_conditional_go(self):
        r = theorem_wsf_2()
        assert "GO" in r["verdict"]


class TestTheoremWsf3:
    def test_returns_dict(self):
        assert isinstance(theorem_wsf_3(), dict)

    def test_theorem_id(self):
        r = theorem_wsf_3()
        assert r["theorem_id"] == "WSF-3"

    def test_conditional_go(self):
        r = theorem_wsf_3()
        assert "GO" in r["verdict"]


class TestSelectedExtensionBranch:
    def test_returns_dict(self):
        assert isinstance(selected_extension_branch(), dict)

    def test_gw_cw_selected(self):
        r = selected_extension_branch()
        assert "GW" in r["selected_option"] or "Coleman" in r["selected_option"]

    def test_open_parameter_is_theta_hr(self):
        r = selected_extension_branch()
        assert "θ_HR" in r["open_parameter"] or "theta_HR" in r["open_parameter"].lower()

    def test_has_kill_switches(self):
        r = selected_extension_branch()
        assert len(r["kill_switches"]) >= 2

    def test_gate_passed_for_memo(self):
        r = selected_extension_branch()
        assert r["gate_passed"] is True


class TestWsfGateReport:
    def test_returns_dict(self):
        assert isinstance(wsf_gate_report(), dict)

    def test_workstream(self):
        assert wsf_gate_report()["workstream"] == "WS-F"

    def test_gate_passed_for_memos(self):
        assert wsf_gate_report()["gate_passed"] is True

    def test_status_unchanged(self):
        r = wsf_gate_report()
        assert "NONE" in r["status_change"] or "OPEN" in r["status_change"]

    def test_has_all_deliverables(self):
        r = wsf_gate_report()
        assert "deliverable_F1_extension_design_memo" in r
        assert "deliverable_F2_go_no_go_theorems" in r
        assert "deliverable_F3_selected_branch" in r


class TestPillarWsfSummary:
    def test_returns_dict(self):
        assert isinstance(pillar_wsf_summary(), dict)

    def test_ghu_killed(self):
        r = pillar_wsf_summary()
        assert r["ghu_killed"] is True

    def test_selected_branch(self):
        r = pillar_wsf_summary()
        assert "GW" in r["selected_branch"] or "Coleman" in r["selected_branch"]
