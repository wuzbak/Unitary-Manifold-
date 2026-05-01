# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cold_fusion_falsification_protocol.py
=================================================
Tests for Pillar 15-F — Cold Fusion Falsification Protocol.
(src/cold_fusion/falsification_protocol.py)

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.cold_fusion.falsification_protocol import (
    # Constants
    Z_D,
    ALPHA_EM,
    C_S_CANONICAL,
    V_REL_DD_THERMAL,
    PHI_LOCAL_CANONICAL,
    PHI_VACUUM,
    LOADING_RATIO_THRESHOLD,
    N_COHERENCE_CANONICAL,
    CALORIMETRY_SENSITIVITY,
    # Functions
    gamow_enhancement_prediction,
    cop_prediction_range,
    null_result_comparison,
    falsification_criteria,
    cold_fusion_falsification_protocol,
)


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_z_d(self):
        assert Z_D == 1

    def test_alpha_em(self):
        assert abs(ALPHA_EM - 1.0 / 137.036) < 1e-6

    def test_cs_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-10

    def test_v_rel_dd_thermal(self):
        # 300K D-D thermal velocity in units of c is ~5e-6
        assert 1e-7 < V_REL_DD_THERMAL < 1e-4

    def test_phi_local_canonical(self):
        assert PHI_LOCAL_CANONICAL == 2.0

    def test_phi_vacuum(self):
        assert PHI_VACUUM == 1.0

    def test_loading_ratio(self):
        assert LOADING_RATIO_THRESHOLD > 0.8

    def test_n_coherence_positive(self):
        assert N_COHERENCE_CANONICAL > 1000

    def test_calorimetry_sensitivity_small(self):
        assert 0 < CALORIMETRY_SENSITIVITY < 0.01


# ===========================================================================
# gamow_enhancement_prediction
# ===========================================================================

class TestGamowEnhancementPrediction:
    def test_returns_dict(self):
        r = gamow_enhancement_prediction()
        assert isinstance(r, dict)

    def test_phi_stored(self):
        r = gamow_enhancement_prediction(phi_local=2.0)
        assert r["phi_local"] == 2.0

    def test_v_rel_stored(self):
        r = gamow_enhancement_prediction(v_rel=V_REL_DD_THERMAL)
        assert abs(r["v_rel"] - V_REL_DD_THERMAL) < 1e-10

    def test_eta_positive(self):
        r = gamow_enhancement_prediction()
        assert r["eta"] > 0

    def test_g_vacuum_non_negative(self):
        r = gamow_enhancement_prediction()
        assert r["G_vacuum"] >= 0  # may be 0.0 due to underflow at cold conditions

    def test_g_eff_non_negative(self):
        r = gamow_enhancement_prediction()
        assert r["G_eff"] >= 0  # may be 0.0 due to underflow at cold conditions

    def test_log10_R_captures_enhancement(self):
        # The log-space ratio is the physically meaningful quantity at cold conditions
        r = gamow_enhancement_prediction(phi_local=2.0)
        assert r["log10_R"] > 100  # enormous enhancement at room temperature

    def test_phi_one_no_enhancement(self):
        # phi = 1 means no enhancement
        r = gamow_enhancement_prediction(phi_local=1.0)
        assert abs(r["log10_R"]) < 1e-8

    def test_log10_R_positive_for_phi_gt_1(self):
        r = gamow_enhancement_prediction(phi_local=2.0)
        assert r["log10_R"] > 0

    def test_log10_R_large(self):
        # At canonical phi=2, enhancement should be >> 10^10
        r = gamow_enhancement_prediction(phi_local=2.0)
        assert r["log10_R"] > 10.0

    def test_exponent_gain_positive(self):
        r = gamow_enhancement_prediction(phi_local=2.0)
        assert r["exponent_gain"] > 0

    def test_status_says_unverified(self):
        r = gamow_enhancement_prediction()
        assert "unverified" in r["status"].lower() or "PREDICTION" in r["status"]

    def test_r_enhancement_string(self):
        r = gamow_enhancement_prediction()
        assert "10^" in r["R_enhancement"]

    def test_larger_phi_gives_more_enhancement(self):
        r1 = gamow_enhancement_prediction(phi_local=2.0)
        r2 = gamow_enhancement_prediction(phi_local=3.0)
        assert r2["log10_R"] > r1["log10_R"]

    def test_smaller_v_rel_gives_more_suppression(self):
        # Lower v_rel → larger η → more suppression in vacuum, more enhancement
        r1 = gamow_enhancement_prediction(phi_local=2.0, v_rel=0.1)
        r2 = gamow_enhancement_prediction(phi_local=2.0, v_rel=0.5)
        # At lower v_rel, η is larger, so the enhancement is larger
        assert r1["log10_R"] > r2["log10_R"]


# ===========================================================================
# cop_prediction_range
# ===========================================================================

class TestCopPredictionRange:
    def test_returns_dict(self):
        r = cop_prediction_range()
        assert isinstance(r, dict)

    def test_phi_values_present(self):
        r = cop_prediction_range(phi_min=1.1, phi_max=2.0, n_steps=5)
        assert len(r["phi_values"]) == 5

    def test_log10_R_values_present(self):
        r = cop_prediction_range(n_steps=5)
        assert len(r["log10_R_values"]) == 5

    def test_log10_R_increases_with_phi(self):
        r = cop_prediction_range(phi_min=1.1, phi_max=3.0, n_steps=10)
        log10_R = r["log10_R_values"]
        assert all(log10_R[i] < log10_R[i + 1] for i in range(len(log10_R) - 1))

    def test_canonical_phi_in_result(self):
        r = cop_prediction_range()
        assert r["phi_canonical"] == PHI_LOCAL_CANONICAL

    def test_note_mentions_cop(self):
        r = cop_prediction_range()
        assert "COP" in r["note"]

    def test_note_mentions_dual_use(self):
        r = cop_prediction_range()
        assert "dual-use" in r["note"].lower() or "DUAL_USE" in r["note"]


# ===========================================================================
# null_result_comparison
# ===========================================================================

class TestNullResultComparison:
    def test_returns_dict(self):
        r = null_result_comparison()
        assert isinstance(r, dict)

    def test_has_um_predicted(self):
        r = null_result_comparison()
        assert "um_predicted_log10_R" in r

    def test_um_predicted_positive(self):
        r = null_result_comparison(phi_local=2.0)
        assert r["um_predicted_log10_R"] > 0

    def test_published_bounds_list(self):
        r = null_result_comparison()
        assert isinstance(r["published_upper_bounds"], list)
        assert len(r["published_upper_bounds"]) >= 3

    def test_each_bound_has_source(self):
        r = null_result_comparison()
        for bound in r["published_upper_bounds"]:
            assert "source" in bound

    def test_each_bound_has_verdict(self):
        r = null_result_comparison()
        for bound in r["published_upper_bounds"]:
            assert "note" in bound

    def test_shanahan_in_sources(self):
        r = null_result_comparison()
        sources = [b["source"] for b in r["published_upper_bounds"]]
        assert any("Shanahan" in s for s in sources)

    def test_knies_in_sources(self):
        r = null_result_comparison()
        sources = [b["source"] for b in r["published_upper_bounds"]]
        assert any("Knies" in s for s in sources)

    def test_consistent_with_null_bool(self):
        r = null_result_comparison()
        assert isinstance(r["consistent_with_null"], bool)

    def test_consistent_with_null_true(self):
        r = null_result_comparison()
        assert r["consistent_with_null"] is True

    def test_conclusion_string(self):
        r = null_result_comparison()
        assert isinstance(r["conclusion"], str)
        assert len(r["conclusion"]) > 30

    def test_conclusion_honest(self):
        r = null_result_comparison()
        text = r["conclusion"].lower()
        assert "not" in text or "unconfirmed" in text


# ===========================================================================
# falsification_criteria
# ===========================================================================

class TestFalsificationCriteria:
    def test_returns_dict(self):
        r = falsification_criteria()
        assert isinstance(r, dict)

    def test_has_three_criteria(self):
        r = falsification_criteria()
        assert len(r["criteria"]) == 3

    def test_criteria_have_labels(self):
        r = falsification_criteria()
        labels = [c["label"] for c in r["criteria"]]
        assert any("F1" in l for l in labels)
        assert any("F2" in l for l in labels)
        assert any("F3" in l for l in labels)

    def test_each_criterion_has_description(self):
        r = falsification_criteria()
        for c in r["criteria"]:
            assert "description" in c
            assert len(c["description"]) > 10

    def test_each_criterion_has_required_conditions(self):
        r = falsification_criteria()
        for c in r["criteria"]:
            assert "required_conditions" in c

    def test_each_criterion_has_verdict(self):
        r = falsification_criteria()
        for c in r["criteria"]:
            assert "verdict_if_met" in c
            assert "FALSIFIED" in c["verdict_if_met"]

    def test_f1_mentions_calorimetry(self):
        r = falsification_criteria()
        f1 = next(c for c in r["criteria"] if "F1" in c["label"])
        assert "calorimetry" in f1["description"].lower() or "COP" in f1["verdict_if_met"]

    def test_f3_mentions_dft(self):
        r = falsification_criteria()
        f3 = next(c for c in r["criteria"] if "F3" in c["label"])
        assert "DFT" in f3["description"]

    def test_note_says_conditions_required(self):
        r = falsification_criteria()
        assert "required conditions" in r["note"].lower() or "required" in r["note"]


# ===========================================================================
# cold_fusion_falsification_protocol
# ===========================================================================

class TestColdFusionFalsificationProtocol:
    def test_returns_dict(self):
        r = cold_fusion_falsification_protocol()
        assert isinstance(r, dict)

    def test_pillar_label(self):
        r = cold_fusion_falsification_protocol()
        assert r["pillar"] == "15-F"

    def test_epistemic_status_present(self):
        r = cold_fusion_falsification_protocol()
        assert "FALSIFIABLE PREDICTION" in r["epistemic_status"]

    def test_epistemic_status_honest(self):
        r = cold_fusion_falsification_protocol()
        assert "not confirmed" in r["epistemic_status"].lower() or "unverified" in r["epistemic_status"].lower()

    def test_prediction_dict_present(self):
        r = cold_fusion_falsification_protocol()
        assert "prediction" in r
        assert r["prediction"]["phi_local"] == PHI_LOCAL_CANONICAL

    def test_cop_range_dict_present(self):
        r = cold_fusion_falsification_protocol()
        assert "cop_range" in r

    def test_null_comparison_present(self):
        r = cold_fusion_falsification_protocol()
        assert "null_comparison" in r
        assert r["null_comparison"]["consistent_with_null"] is True

    def test_criteria_present(self):
        r = cold_fusion_falsification_protocol()
        assert "falsification_criteria" in r
        assert len(r["falsification_criteria"]["criteria"]) == 3

    def test_dual_use_notice(self):
        r = cold_fusion_falsification_protocol()
        assert "dual_use_notice" in r
        assert "DUAL_USE_NOTICE" in r["dual_use_notice"] or "dual-use" in r["dual_use_notice"].lower()

    def test_summary_present(self):
        r = cold_fusion_falsification_protocol()
        assert len(r["summary"]) > 50

    def test_summary_mentions_not_confirmed(self):
        r = cold_fusion_falsification_protocol()
        assert "NOT been" in r["summary"] or "not confirmed" in r["summary"].lower()

    def test_custom_phi_local(self):
        r = cold_fusion_falsification_protocol(phi_local=3.0)
        assert r["prediction"]["phi_local"] == 3.0
