# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ckm_scaffold_analysis.py
======================================
Tests for Pillar 188 — CKM Scaffold Analysis (src/core/ckm_scaffold_analysis.py).

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.ckm_scaffold_analysis import (
    N_W, N1, N2, K_CS, DELTA_GEO_DEG, DELTA_SUB_DEG, DELTA_PDG_DEG,
    RHO_BAR_PDG, ETA_BAR_PDG, RHO_BAR_GEO, J_PDG,
    topological_vs_geometric_classification,
    jarlskog_inconsistency_diagnosis,
    consistent_geometric_ckm_params,
    j_with_consistent_geometry,
    mixing_angle_topological_barrier,
    sm_comparison,
    scaffold_verdict,
    pillar188_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n1(self):
        assert N1 == 5

    def test_n2(self):
        assert N2 == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_delta_geo_deg(self):
        assert DELTA_GEO_DEG == pytest.approx(72.0, rel=1e-9)

    def test_delta_sub_deg(self):
        assert DELTA_SUB_DEG == pytest.approx(71.07, abs=0.05)

    def test_delta_pdg_deg(self):
        assert DELTA_PDG_DEG == pytest.approx(68.5, rel=1e-6)

    def test_delta_sub_from_n1_n2(self):
        expected = math.degrees(2.0 * math.atan2(5, 7))
        assert DELTA_SUB_DEG == pytest.approx(expected, rel=1e-9)

    def test_rho_bar_pdg(self):
        assert RHO_BAR_PDG == pytest.approx(0.159, rel=1e-6)

    def test_eta_bar_pdg(self):
        assert ETA_BAR_PDG == pytest.approx(0.348, rel=1e-6)

    def test_rho_bar_geo_less_than_pdg(self):
        # Geometric estimate is ~25% below PDG
        assert RHO_BAR_GEO < RHO_BAR_PDG

    def test_rho_bar_geo_approx_25pct_below(self):
        pct_diff = abs(RHO_BAR_GEO - RHO_BAR_PDG) / RHO_BAR_PDG * 100
        assert 20 < pct_diff < 32


class TestTopologicalVsGeometricClassification:
    def setup_method(self):
        self.r = topological_vs_geometric_classification()

    def test_has_parameters(self):
        assert "parameters" in self.r

    def test_delta_topological(self):
        assert self.r["parameters"]["delta_cp"]["origin"] == "TOPOLOGICAL"

    def test_delta_zero_free_params(self):
        assert self.r["parameters"]["delta_cp"]["free_parameters"] == 0

    def test_theta_12_geometric(self):
        assert "GEOMETRIC" in self.r["parameters"]["theta_12"]["origin"]

    def test_theta_13_geometric(self):
        assert "GEOMETRIC" in self.r["parameters"]["theta_13"]["origin"]

    def test_theta_23_geometric(self):
        assert "GEOMETRIC" in self.r["parameters"]["theta_23"]["origin"]

    def test_rho_bar_geometric_estimate(self):
        assert "GEOMETRIC" in self.r["parameters"]["rho_bar"]["origin"]

    def test_delta_status_derived(self):
        assert "DERIVED" in self.r["parameters"]["delta_cp"]["status"]

    def test_topological_sector_list(self):
        topo = self.r["sector_summary"]["topological"]
        assert len(topo) > 0
        # delta should be in topological
        combined = " ".join(topo)
        assert "δ" in combined or "delta" in combined.lower()

    def test_geometric_sector_list(self):
        geo = self.r["sector_summary"]["geometric"]
        assert len(geo) > 0

    def test_delta_mechanism_mentions_winding(self):
        mech = self.r["parameters"]["delta_cp"]["mechanism"]
        assert "winding" in mech.lower() or "CS" in mech or "topolog" in mech.lower()

    def test_theta_mechanism_mentions_cl(self):
        mech = self.r["parameters"]["theta_12"]["mechanism"]
        assert "c_L" in mech or "continuous" in mech.lower()


class TestJarlskogInconsistencyDiagnosis:
    def setup_method(self):
        self.r = jarlskog_inconsistency_diagnosis()

    def test_layer1_uses_pdg_rho(self):
        assert self.r["layer_1_inconsistent_hybrid"]["rho_bar_used"] == pytest.approx(RHO_BAR_PDG, rel=1e-6)

    def test_layer1_eta_inflated(self):
        # eta_bar from hybrid should be > PDG
        eta_hybrid = self.r["layer_1_inconsistent_hybrid"]["eta_bar_implied"]
        assert eta_hybrid > ETA_BAR_PDG

    def test_layer1_j_ratio_above_1(self):
        assert self.r["layer_1_inconsistent_hybrid"]["J_ratio_to_pdg"] > 1.0

    def test_layer2_consistent_geo_lower_ratio(self):
        # Consistent geometry gives lower J ratio than hybrid
        ratio_hybrid = self.r["layer_1_inconsistent_hybrid"]["J_ratio_to_pdg"]
        ratio_consistent = self.r["layer_2_consistent_geometry"]["J_ratio_to_pdg"]
        assert ratio_consistent < ratio_hybrid

    def test_layer2_uses_geo_rho(self):
        assert self.r["layer_2_consistent_geometry"]["rho_bar_used"] == pytest.approx(RHO_BAR_GEO, rel=1e-6)

    def test_net_diagnosis_two_layers(self):
        diag = self.r["net_diagnosis"]
        assert "Layer 1" in diag or "layer 1" in diag.lower()
        assert "Layer 2" in diag or "layer 2" in diag.lower()

    def test_layer1b_subleading_present(self):
        assert "layer_1b_subleading_hybrid" in self.r

    def test_layer1b_j_ratio(self):
        # Subleading hybrid (72° -> 71°) slightly reduces gap
        r1 = self.r["layer_1_inconsistent_hybrid"]["J_ratio_to_pdg"]
        r1b = self.r["layer_1b_subleading_hybrid"]["J_ratio"]
        # Both should be above 1, 1b slightly less than 1
        assert r1 > 1.0
        assert r1b > 1.0


class TestConsistentGeometricCKMParams:
    def setup_method(self):
        self.r = consistent_geometric_ckm_params()

    def test_delta_sub_deg(self):
        assert self.r["delta_sub_deg"] == pytest.approx(DELTA_SUB_DEG, rel=1e-6)

    def test_rho_bar_geo(self):
        assert self.r["rho_bar_geo"] == pytest.approx(RHO_BAR_GEO, rel=1e-6)

    def test_j_ratio_closer_to_1_than_hybrid(self):
        # Should be closer to 1.0 than the hybrid
        diagnosis = jarlskog_inconsistency_diagnosis()
        hybrid_distance = abs(diagnosis["layer_1b_subleading_hybrid"]["J_ratio"] - 1.0)
        consistent_distance = abs(self.r["J_ratio"] - 1.0)
        assert consistent_distance < hybrid_distance

    def test_j_ratio_positive(self):
        assert self.r["J_ratio"] > 0

    def test_v_ub_error_reduced(self):
        # V_ub error with consistent geo should be < 34% (the hybrid error)
        assert self.r["V_ub_pct_error"] < 34.0

    def test_eta_bar_pct_error_reasonable(self):
        assert 0 < self.r["eta_bar_pct_error"] < 30

    def test_j_pdg_matches_module_constant(self):
        assert self.r["J_pdg"] == pytest.approx(J_PDG, rel=1e-9)

    def test_note_mentions_residual(self):
        assert "15%" in self.r["note"] or "residual" in self.r["note"].lower()


class TestJWithConsistentGeometry:
    def setup_method(self):
        self.r = j_with_consistent_geometry()

    def test_j_pdg(self):
        assert self.r["J_pdg"] == pytest.approx(J_PDG, rel=1e-9)

    def test_improvement_positive(self):
        assert self.r["improvement_from_consistency"] > 0

    def test_residual_gap_pct_positive(self):
        assert self.r["residual_gap_pct"] > 0

    def test_residual_gap_origin_metric(self):
        assert "metric" in self.r["residual_gap_origin"].lower() or "θ" in self.r["residual_gap_origin"]

    def test_summary_present(self):
        assert len(self.r["summary"]) > 50


class TestMixingAngleTopologicalBarrier:
    def setup_method(self):
        self.r = mixing_angle_topological_barrier()

    def test_question_present(self):
        assert "θ" in self.r["question"] or "theta" in self.r["question"].lower()

    def test_delta_derivable_reason(self):
        reason = self.r["answer"]["delta_derivable"]["reason"]
        assert "winding" in reason.lower() or "topolog" in reason.lower()

    def test_theta_not_derivable_reason(self):
        reason = self.r["answer"]["theta_not_derivable"]["reason"]
        assert "continuous" in reason.lower() or "c_L" in reason

    def test_what_would_close_it(self):
        close = self.r["answer"]["theta_not_derivable"]["what_would_close_it"]
        assert "flavor" in close.lower() or "symmetry" in close.lower()

    def test_formal_statement_present(self):
        assert "THEOREM" in self.r["formal_statement"]

    def test_analogies_present(self):
        assert "analogy" in self.r
        assert len(self.r["analogy"]) > 0

    def test_sm_analogy(self):
        sm_analogy = self.r["analogy"].get("Standard_Model", "")
        assert "SM" in sm_analogy or "Standard" in sm_analogy


class TestSMComparison:
    def setup_method(self):
        self.r = sm_comparison()

    def test_sm_has_4_free_params(self):
        assert self.r["sm_ckm_free_parameters"] == 4

    def test_um_derives_one_beyond_sm(self):
        assert self.r["um_derives_beyond_sm"] == 1

    def test_um_remaining_free_3(self):
        assert self.r["um_remaining_ckm_free"] == 3

    def test_improvement_mentions_delta(self):
        assert "δ" in self.r["improvement"] or "delta" in self.r["improvement"].lower()

    def test_fair_verdict_discovery(self):
        assert "DISCOVERY" in self.r["fair_verdict"]

    def test_fair_verdict_not_more_spreadsheet(self):
        assert "not" in self.r["fair_verdict"].lower() or "NOT" in self.r["fair_verdict"]


class TestScaffoldVerdict:
    def setup_method(self):
        self.v = scaffold_verdict()

    def test_question_present(self):
        assert "spreadsheet" in self.v["question"].lower() or "discovery" in self.v["question"].lower()

    def test_answer_both(self):
        assert "BOTH" in self.v["answer"]

    def test_topological_verdict_discovery(self):
        assert "DISCOVERY" in self.v["topological_sector"]["verdict"]

    def test_metric_verdict_spreadsheet(self):
        assert "SPREADSHEET" in self.v["metric_sector"]["verdict"]

    def test_derived_quantities_includes_delta(self):
        derived = " ".join(self.v["topological_sector"]["derived_quantities"])
        assert "δ" in derived or "CP phase" in derived

    def test_jarlskog_layers_present(self):
        assert "layer_1_fixable" in self.v["jarlskog_gap_layers"]
        assert "layer_2_structural" in self.v["jarlskog_gap_layers"]

    def test_path_to_closure_mentions_flavor(self):
        assert "flavor" in self.v["path_to_closure"].lower()

    def test_honest_conclusion_sm_comparison(self):
        assert "SM" in self.v["honest_conclusion"] or "Standard Model" in self.v["honest_conclusion"]

    def test_honest_conclusion_not_more_spreadsheet(self):
        conclusion = self.v["honest_conclusion"]
        assert "condemn" in conclusion.lower() or "not MORE" in conclusion or "not more" in conclusion.lower()


class TestPillar188Summary:
    def setup_method(self):
        self.s = pillar188_summary()

    def test_pillar_number(self):
        assert self.s["pillar"] == 188

    def test_topological_verdict_discovery(self):
        assert "DISCOVERY" in self.s["topological_sector_verdict"]

    def test_metric_verdict_spreadsheet(self):
        assert "SPREADSHEET" in self.s["metric_sector_verdict"]

    def test_um_derives_beyond_sm(self):
        assert self.s["um_derives_beyond_sm_count"] == 1

    def test_layer_1_fixable(self):
        assert self.s["jarlskog_gap_layer_1_fixable"] is True

    def test_flavor_symmetry_needed(self):
        assert self.s["flavor_symmetry_needed_to_close"] is True

    def test_j_consistent_ratio_closer_to_1(self):
        # Should be < 1.37 (the hybrid value)
        assert self.s["jarlskog_consistent_geo_ratio"] < 1.37

    def test_sources_present(self):
        assert len(self.s["sources"]) >= 4

    def test_status_contains_closed(self):
        assert "CLOSED" in self.s["status"]

    def test_version_v9_39(self):
        assert "9.39" in self.s["version"]

    def test_honest_conclusion_present(self):
        assert len(self.s["honest_conclusion"]) > 100
