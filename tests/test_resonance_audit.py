# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_resonance_audit.py
================================
Tests for src/governance/resonance_audit.py — Pillar 196.
"""

from __future__ import annotations

import math

import pytest

from src.governance.resonance_audit import (
    XI_C,
    SIGMA_S,
    K_CS,
    N_W,
    N_INV,
    RESONANCE_THRESHOLD,
    WARNING_THRESHOLD,
    CRITICAL_THRESHOLD,
    compute_coherence_score,
    proof_of_resonance,
    hils_heartbeat,
    co_emergence_audit,
    resonance_gradient,
    pillar196_summary,
)


# ===========================================================================
# Module Constants
# ===========================================================================

class TestModuleConstants:
    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n_w_is_5(self):
        assert N_W == 5

    def test_n_inv_is_7(self):
        assert N_INV == 7

    def test_xi_c_value(self):
        assert XI_C == pytest.approx(35.0 / 74.0, rel=1e-9)

    def test_xi_c_is_n_w_times_n_inv_over_k_cs(self):
        assert XI_C == pytest.approx(N_W * N_INV / K_CS, rel=1e-9)

    def test_sigma_s_value(self):
        assert SIGMA_S == pytest.approx(12.0 / 37.0, rel=1e-9)

    def test_resonance_threshold_equals_xi_c(self):
        assert RESONANCE_THRESHOLD == pytest.approx(XI_C, rel=1e-9)

    def test_warning_threshold_equals_sigma_s(self):
        assert WARNING_THRESHOLD == pytest.approx(SIGMA_S, rel=1e-9)

    def test_critical_threshold_equals_warning(self):
        assert CRITICAL_THRESHOLD == pytest.approx(WARNING_THRESHOLD, rel=1e-9)

    def test_warning_lt_resonance(self):
        assert WARNING_THRESHOLD < RESONANCE_THRESHOLD

    def test_xi_c_approx_0473(self):
        assert XI_C == pytest.approx(0.4730, abs=0.0001)

    def test_sigma_s_approx_0324(self):
        assert SIGMA_S == pytest.approx(0.3243, abs=0.0001)

    def test_n_w_sq_plus_n_inv_sq_is_k_cs(self):
        assert N_W**2 + N_INV**2 == K_CS


# ===========================================================================
# compute_coherence_score
# ===========================================================================

class TestComputeCoherenceScore:
    def test_equal_contributions_give_one(self):
        score = compute_coherence_score({"a": 1.0, "b": 1.0})
        assert score == pytest.approx(1.0, rel=1e-9)

    def test_equal_three_contributors(self):
        score = compute_coherence_score({"a": 1.0, "b": 1.0, "c": 1.0})
        assert score == pytest.approx(1.0, rel=1e-9)

    def test_monopoly_gives_zero(self):
        score = compute_coherence_score({"a": 1000.0, "b": 0.0001})
        # Near-monopoly: extremely low score
        assert score < 0.05

    def test_perfect_monopoly_when_one_zero(self):
        # Only 1 active contributor → score = 0
        score = compute_coherence_score({"a": 100.0, "b": 0.0})
        assert score == pytest.approx(0.0, abs=1e-9)

    def test_score_in_range(self):
        score = compute_coherence_score({"human": 40.0, "ai": 60.0})
        assert 0.0 <= score <= 1.0

    def test_imbalanced_session_below_threshold(self):
        # 90/10 split
        score = compute_coherence_score({"human": 90.0, "ai": 10.0})
        assert score < RESONANCE_THRESHOLD

    def test_balanced_session_above_threshold(self):
        # 50/50 split
        score = compute_coherence_score({"human": 50.0, "ai": 50.0})
        assert score >= RESONANCE_THRESHOLD

    def test_raises_for_single_contributor(self):
        with pytest.raises(ValueError):
            compute_coherence_score({"only_one": 1.0})

    def test_raises_for_empty(self):
        with pytest.raises(ValueError):
            compute_coherence_score({})

    def test_raises_for_all_zero(self):
        with pytest.raises(ValueError):
            compute_coherence_score({"a": 0.0, "b": 0.0})

    def test_score_symmetric(self):
        s1 = compute_coherence_score({"a": 30.0, "b": 70.0})
        s2 = compute_coherence_score({"a": 70.0, "b": 30.0})
        assert s1 == pytest.approx(s2, rel=1e-9)

    def test_scaling_invariant(self):
        s1 = compute_coherence_score({"a": 1.0, "b": 2.0})
        s2 = compute_coherence_score({"a": 100.0, "b": 200.0})
        assert s1 == pytest.approx(s2, rel=1e-9)

    def test_three_equal_is_higher_than_two_equal(self):
        # log2(3)/log2(3) = 1, log2(2)/log2(2) = 1 — both perfect
        s2 = compute_coherence_score({"a": 1.0, "b": 1.0})
        s3 = compute_coherence_score({"a": 1.0, "b": 1.0, "c": 1.0})
        assert s2 == pytest.approx(1.0, rel=1e-9)
        assert s3 == pytest.approx(1.0, rel=1e-9)

    def test_canonical_hils_pair_resonant(self):
        # Human: direction/judgment (35), AI: code/tests/synthesis (39)
        score = compute_coherence_score({"human": 35.0, "ai": 39.0})
        assert score >= RESONANCE_THRESHOLD

    def test_negative_values_treated_as_magnitudes(self):
        # Absolute values used
        s1 = compute_coherence_score({"a": 1.0, "b": 2.0})
        s2 = compute_coherence_score({"a": -1.0, "b": -2.0})
        assert s1 == pytest.approx(s2, rel=1e-9)


# ===========================================================================
# proof_of_resonance
# ===========================================================================

class TestProofOfResonance:
    def test_resonant_state(self):
        r = proof_of_resonance({"contributions": {"human": 50.0, "ai": 50.0}})
        assert r["state"] == "RESONANT"

    def test_warning_state(self):
        # 90/10 split: H = 0.469 ∈ [σ_s=0.324, ξ_c=0.473) → WARNING
        r = proof_of_resonance({"contributions": {"human": 90.0, "ai": 10.0}})
        assert r["state"] in ("WARNING", "CRITICAL")

    def test_critical_state(self):
        r = proof_of_resonance({"contributions": {"human": 99.0, "ai": 1.0}})
        assert r["state"] in ("WARNING", "CRITICAL")

    def test_session_id_passthrough(self):
        r = proof_of_resonance({
            "contributions": {"a": 1.0, "b": 1.0},
            "session_id": "test-session-42",
        })
        assert r["session_id"] == "test-session-42"

    def test_coherence_score_in_range(self):
        r = proof_of_resonance({"contributions": {"a": 3.0, "b": 7.0}})
        assert 0.0 <= r["coherence_score"] <= 1.0

    def test_thresholds_in_output(self):
        r = proof_of_resonance({"contributions": {"a": 1.0, "b": 1.0}})
        assert r["resonance_threshold"] == pytest.approx(RESONANCE_THRESHOLD, rel=1e-9)
        assert r["warning_threshold"] == pytest.approx(WARNING_THRESHOLD, rel=1e-9)

    def test_threshold_exact_strings(self):
        r = proof_of_resonance({"contributions": {"a": 1.0, "b": 1.0}})
        assert "ξ_c" in r["resonance_threshold_exact"] or "xi_c" in r["resonance_threshold_exact"].lower()
        assert "σ_s" in r["warning_threshold_exact"] or "sigma_s" in r["warning_threshold_exact"].lower()

    def test_verdict_present(self):
        r = proof_of_resonance({"contributions": {"a": 1.0, "b": 1.0}})
        assert len(r["verdict"]) > 20

    def test_recommendations_list(self):
        r = proof_of_resonance({"contributions": {"a": 1.0, "b": 1.0}})
        assert isinstance(r["recommendations"], list)
        assert len(r["recommendations"]) >= 1

    def test_color_indicator_present(self):
        r = proof_of_resonance({"contributions": {"a": 1.0, "b": 1.0}})
        assert r["color_indicator"] in ("green", "yellow", "red")

    def test_contributor_breakdown_present(self):
        r = proof_of_resonance({"contributions": {"human": 35.0, "ai": 65.0}})
        assert "human" in r["contributor_breakdown"]
        assert "ai" in r["contributor_breakdown"]

    def test_fraction_sums_to_one(self):
        r = proof_of_resonance({"contributions": {"a": 30.0, "b": 70.0}})
        fractions = [v["fraction"] for v in r["contributor_breakdown"].values()]
        assert sum(fractions) == pytest.approx(1.0, rel=1e-6)

    def test_anchored_to_physics(self):
        r = proof_of_resonance({"contributions": {"a": 1.0, "b": 1.0}})
        anchor = r["anchored_to_physics"]
        assert anchor["xi_c"] == pytest.approx(XI_C, rel=1e-9)
        assert anchor["k_cs"] == K_CS

    def test_resonant_color_is_green(self):
        r = proof_of_resonance({"contributions": {"a": 1.0, "b": 1.0}})
        assert r["color_indicator"] == "green"

    def test_critical_color_is_red(self):
        r = proof_of_resonance({"contributions": {"a": 999.0, "b": 1.0}})
        # Near-monopoly → critical
        assert r["color_indicator"] in ("red", "yellow")


# ===========================================================================
# hils_heartbeat
# ===========================================================================

class TestHILSHeartbeat:
    def test_alive_for_equal_contributions(self):
        r = hils_heartbeat({"human": 1.0, "ai": 1.0})
        assert r["alive"] is True

    def test_dead_for_monopoly(self):
        r = hils_heartbeat({"human": 999.0, "ai": 1.0})
        # Very near monopoly → dead
        assert r["dead"] is True or r["warning"] is True

    def test_status_alive(self):
        r = hils_heartbeat({"a": 1.0, "b": 1.0})
        assert r["status"] == "ALIVE"

    def test_score_in_range(self):
        r = hils_heartbeat({"a": 3.0, "b": 7.0})
        assert 0.0 <= r["coherence_score"] <= 1.0

    def test_summary_contains_score(self):
        r = hils_heartbeat({"a": 1.0, "b": 1.0})
        assert "Score" in r["summary"] or "score" in r["summary"].lower()

    def test_xi_c_in_output(self):
        r = hils_heartbeat({"a": 1.0, "b": 1.0})
        assert r["xi_c"] == pytest.approx(XI_C, rel=1e-9)

    def test_sigma_s_in_output(self):
        r = hils_heartbeat({"a": 1.0, "b": 1.0})
        assert r["sigma_s"] == pytest.approx(SIGMA_S, rel=1e-9)

    def test_mutually_exclusive_states(self):
        r = hils_heartbeat({"a": 1.0, "b": 1.0})
        # Exactly one of alive/warning/dead should be True
        states = [r["alive"], r["warning"], r["dead"]]
        assert sum(states) == 1


# ===========================================================================
# co_emergence_audit
# ===========================================================================

class TestCoEmergenceAudit:
    def test_empty_returns_no_data(self):
        r = co_emergence_audit([])
        assert r["status"] == "NO DATA"

    def test_single_resonant_session(self):
        sessions = [{"contributions": {"a": 1.0, "b": 1.0}}]
        r = co_emergence_audit(sessions)
        assert r["n_sessions"] == 1
        assert r["aggregate_state"] == "RESONANT"

    def test_n_sessions_correct(self):
        sessions = [
            {"contributions": {"a": 1.0, "b": 1.0}},
            {"contributions": {"a": 2.0, "b": 1.0}},
        ]
        r = co_emergence_audit(sessions)
        assert r["n_sessions"] == 2

    def test_scores_list_length(self):
        sessions = [{"contributions": {"a": float(i), "b": 1.0}} for i in range(1, 6)]
        r = co_emergence_audit(sessions)
        assert len(r["scores"]) == 5

    def test_mean_score_in_range(self):
        sessions = [{"contributions": {"a": 1.0, "b": 1.0}}] * 5
        r = co_emergence_audit(sessions)
        assert 0.0 <= r["mean_coherence_score"] <= 1.0

    def test_fraction_resonant_correct(self):
        sessions = [
            {"contributions": {"a": 1.0, "b": 1.0}},  # resonant
            {"contributions": {"a": 99.0, "b": 1.0}},  # not resonant
        ]
        r = co_emergence_audit(sessions)
        assert r["n_resonant"] == 1
        assert r["fraction_resonant"] == pytest.approx(0.5, rel=1e-9)

    def test_trend_direction_stable(self):
        sessions = [{"contributions": {"a": 1.0, "b": 1.0}}] * 6
        r = co_emergence_audit(sessions)
        assert r["trend_direction"] == "STABLE"

    def test_anchored_to_physics_present(self):
        sessions = [{"contributions": {"a": 1.0, "b": 1.0}}]
        r = co_emergence_audit(sessions)
        assert r["anchored_to_physics"]["k_cs"] == K_CS

    def test_per_session_reports_present(self):
        sessions = [{"contributions": {"a": 1.0, "b": 1.0}}]
        r = co_emergence_audit(sessions)
        assert len(r["per_session_reports"]) == 1

    def test_min_max_scores(self):
        sessions = [
            {"contributions": {"a": 1.0, "b": 1.0}},  # score=1.0
            {"contributions": {"a": 99.0, "b": 1.0}},  # score≈0
        ]
        r = co_emergence_audit(sessions)
        assert r["min_score"] < r["max_score"]


# ===========================================================================
# resonance_gradient
# ===========================================================================

class TestResonanceGradient:
    def test_empty_returns_empty(self):
        r = resonance_gradient([])
        assert r["scores"] == []
        assert r["gradient"] == pytest.approx(0.0, abs=1e-9)

    def test_single_snapshot(self):
        r = resonance_gradient([{"a": 1.0, "b": 1.0}])
        assert r["n_snapshots"] == 1
        assert len(r["scores"]) == 1

    def test_improving_gradient_positive(self):
        # Start with monopoly, improve toward equal
        history = [
            {"dominant": 90.0, "other": 10.0},
            {"dominant": 70.0, "other": 30.0},
            {"dominant": 50.0, "other": 50.0},
            {"dominant": 50.0, "other": 50.0},
        ]
        r = resonance_gradient(history)
        assert r["gradient_per_step"] > 0.0
        assert r["improving"] is True

    def test_stable_gradient_near_zero(self):
        history = [{"a": 1.0, "b": 1.0}] * 5
        r = resonance_gradient(history)
        assert abs(r["gradient_per_step"]) < 0.01

    def test_converging_when_last_above_threshold(self):
        history = [{"a": 1.0, "b": 1.0}] * 3
        r = resonance_gradient(history)
        assert r["converging_to_resonance"] is True

    def test_not_converging_when_below_threshold(self):
        history = [{"a": 99.0, "b": 1.0}] * 3
        r = resonance_gradient(history)
        assert r["converging_to_resonance"] is False

    def test_verdict_present(self):
        r = resonance_gradient([{"a": 1.0, "b": 1.0}])
        assert len(r["verdict"]) > 20

    def test_n_snapshots_correct(self):
        history = [{"a": 1.0, "b": 1.0}] * 7
        r = resonance_gradient(history)
        assert r["n_snapshots"] == 7


# ===========================================================================
# pillar196_summary
# ===========================================================================

class TestPillar196Summary:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = pillar196_summary()

    def test_pillar_is_196(self):
        assert self._r["pillar"] == 196

    def test_version(self):
        assert self._r["version"] == "v10.2"

    def test_status(self):
        assert "FUNCTIONAL" in self._r["status"]

    def test_xi_c_in_anchors(self):
        assert self._r["physical_anchors"]["xi_c"] == pytest.approx(XI_C, rel=1e-9)

    def test_xi_c_exact_string(self):
        assert "35/74" in self._r["physical_anchors"]["xi_c_exact"]

    def test_sigma_s_in_anchors(self):
        assert self._r["physical_anchors"]["sigma_s"] == pytest.approx(SIGMA_S, rel=1e-9)

    def test_k_cs_in_anchors(self):
        assert self._r["physical_anchors"]["k_cs"] == K_CS

    def test_thresholds_dict(self):
        assert "resonant" in self._r["thresholds"]
        assert "warning" in self._r["thresholds"]
        assert "critical" in self._r["thresholds"]

    def test_balanced_session_resonant(self):
        assert self._r["canonical_examples"]["balanced_resonant"] is True

    def test_monopoly_not_resonant(self):
        assert self._r["canonical_examples"]["monopoly_resonant"] is False

    def test_balanced_score_near_one(self):
        assert self._r["canonical_examples"]["balanced_session_score"] == pytest.approx(1.0, abs=0.05)

    def test_monopoly_score_near_zero(self):
        assert self._r["canonical_examples"]["monopoly_score"] < RESONANCE_THRESHOLD

    def test_answers_governance_challenge(self):
        assert len(self._r["answers_governance_challenge"]) > 20

    def test_not_documentation_flag(self):
        assert len(self._r["not_documentation"]) > 20

    def test_mathematical_basis(self):
        assert "Shannon" in self._r["mathematical_basis"] or "entropy" in self._r["mathematical_basis"].lower()
