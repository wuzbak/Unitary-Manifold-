# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar371_kk_ewpt_baryogenesis.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar371_kk_ewpt_baryogenesis import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    ETA_B_OBSERVED, T_EW_GEV, M_KK_GEV, M_PL_GEV, M_HIGGS_GEV,
    SM_E_CUBIC_COEFFICIENT, FIRST_ORDER_REQUIREMENT, SM_VTC_RATIO,
    separation_guard, kk_contribution_to_veff, sm_ewpt_parameters,
    kk_ewpt_assessment, sphaleron_washout_check,
    baryogenesis_architecture_limit_summary, pillar371_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 371
    def test_status(self): assert PILLAR_STATUS == "ARCHITECTURE_LIMIT_CONFIRMED"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_t_ew(self): assert abs(T_EW_GEV - 100.0) < 1.0
    def test_m_kk(self): assert M_KK_GEV > 1e10
    def test_higgs_mass(self): assert abs(M_HIGGS_GEV - 125.25) < 1.0
    def test_sm_e_cubic(self): assert SM_E_CUBIC_COEFFICIENT > 0
    def test_first_order_req(self): assert FIRST_ORDER_REQUIREMENT == 1.0
    def test_sm_vtc_below_req(self): assert SM_VTC_RATIO < FIRST_ORDER_REQUIREMENT


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_mentions_architecture(self): assert "ARCHITECTURE" in separation_guard()


class TestKkContributionToVeff:
    def test_returns_dict(self): assert isinstance(kk_contribution_to_veff(), dict)
    def test_kk_negligible(self):
        r = kk_contribution_to_veff()
        assert r["kk_contributions_negligible"] is True
    def test_total_cubic_tiny(self):
        r = kk_contribution_to_veff()
        assert r["kk_total_cubic_addition"] < 1e-50
    def test_verdict_negligible(self):
        r = kk_contribution_to_veff()
        assert "NEGLIGIBLE" in r["verdict"].upper()
    def test_modes_list_present(self):
        r = kk_contribution_to_veff()
        assert "modes" in r
    def test_modes_count_matches(self):
        r = kk_contribution_to_veff(n_modes=3)
        assert len(r["modes"]) == 3
    def test_mass_ratio_large(self):
        r = kk_contribution_to_veff()
        for mode in r["modes"]:
            assert mode["m_n_over_T"] > 1e10


class TestSmEwptParameters:
    def test_returns_dict(self): assert isinstance(sm_ewpt_parameters(), dict)
    def test_higgs_mass(self):
        r = sm_ewpt_parameters()
        assert abs(r["m_higgs_gev"] - M_HIGGS_GEV) < 1.0
    def test_not_first_order(self):
        r = sm_ewpt_parameters()
        assert r["is_first_order"] is False
    def test_vtc_below_1(self):
        r = sm_ewpt_parameters()
        assert r["v_tc_ratio_estimate"] < FIRST_ORDER_REQUIREMENT
    def test_verdict_second_order(self):
        r = sm_ewpt_parameters()
        assert "second-order" in r["verdict"].lower()


class TestKkEwptAssessment:
    def test_returns_dict(self): assert isinstance(kk_ewpt_assessment(), dict)
    def test_kk_changes_verdict_false(self):
        r = kk_ewpt_assessment()
        assert r["kk_changes_verdict"] is False
    def test_verdict_ruled_out(self):
        r = kk_ewpt_assessment()
        assert "RULED_OUT" in r["verdict"]
    def test_three_obstructions(self):
        r = kk_ewpt_assessment()
        assert "obstruction_1" in r
        assert "obstruction_2" in r
        assert "obstruction_3" in r
    def test_kk_corrected_vtc_unchanged(self):
        r = kk_ewpt_assessment()
        # KK correction is negligible, so kk_corrected_v_tc_ratio should be
        # < FIRST_ORDER_REQUIREMENT (which is the main physics point)
        assert r["kk_corrected_v_tc_ratio"] < FIRST_ORDER_REQUIREMENT


class TestSphaleronWashoutCheck:
    def test_returns_dict(self): assert isinstance(sphaleron_washout_check(), dict)
    def test_condition_not_met(self):
        r = sphaleron_washout_check()
        assert r["condition_met"] is False
    def test_washout_not_suppressed_sm(self):
        r = sphaleron_washout_check()
        assert r["washout_suppressed_sm"] is False
    def test_washout_not_suppressed_kk(self):
        r = sphaleron_washout_check()
        assert r["washout_suppressed_kk"] is False
    def test_verdict_present(self):
        r = sphaleron_washout_check()
        assert "verdict" in r
    def test_vtc_sm_present(self):
        r = sphaleron_washout_check()
        assert "v_tc_sm" in r


class TestBaryogenesisArchitectureLimitSummary:
    def test_returns_dict(self): assert isinstance(baryogenesis_architecture_limit_summary(), dict)
    def test_three_pillars_present(self):
        r = baryogenesis_architecture_limit_summary()
        assert "pillar_365_minimal_kk" in r
        assert "pillar_370_ad_mechanism" in r
        assert "pillar_371_kk_ewpt" in r
    def test_overall_verdict_present(self):
        r = baryogenesis_architecture_limit_summary()
        assert "overall_verdict" in r
    def test_paths_forward(self):
        r = baryogenesis_architecture_limit_summary()
        assert len(r["paths_forward"]) >= 3
    def test_all_architecture_limit(self):
        r = baryogenesis_architecture_limit_summary()
        assert "ARCHITECTURE_LIMIT" in r["pillar_365_minimal_kk"]["status"]
        assert "ARCHITECTURE_LIMIT" in r["pillar_370_ad_mechanism"]["status"]
        assert "ARCHITECTURE_LIMIT" in r["pillar_371_kk_ewpt"]["status"]


class TestPillar371Summary:
    def test_pillar(self): assert pillar371_summary()["pillar"] == 371
    def test_status(self): assert pillar371_summary()["status"] == "ARCHITECTURE_LIMIT_CONFIRMED"
    def test_kk_ewpt_not_viable(self): assert pillar371_summary()["kk_ewpt_viable"] is False
    def test_obstruction_primary_present(self): assert "obstruction_primary" in pillar371_summary()
