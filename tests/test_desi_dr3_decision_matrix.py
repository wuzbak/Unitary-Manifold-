# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_desi_dr3_decision_matrix.py
========================================
Test suite for src/core/desi_dr3_decision_matrix.py (~20 tests).

Covers:
  - SUBMISSION_STRATEGY_PRE_DR3 returns strategy='SUBMIT_BEFORE_DR3'
  - modification_roadmap_if_falsified has 'new_sector_required' key
  - modification_roadmap_if_tension_increases has monitoring and retraction criteria
  - modification_roadmap_if_consistent has correct claim updates
  - release_day_action_protocol with falsifying input returns 'INITIATE_FALSIFICATION_PROTOCOL'
  - desi_dr3_strategic_summary returns complete dict with all expected keys
"""
from __future__ import annotations

import pytest

from src.core.desi_dr3_decision_matrix import (
    SUBMISSION_STRATEGY_PRE_DR3,
    modification_roadmap_if_falsified,
    modification_roadmap_if_tension_increases,
    modification_roadmap_if_consistent,
    release_day_action_protocol,
    desi_dr3_strategic_summary,
)


# ---------------------------------------------------------------------------
# SUBMISSION_STRATEGY_PRE_DR3
# ---------------------------------------------------------------------------

class TestSubmissionStrategyPreDr3:
    def test_strategy_is_submit_before_dr3(self):
        """SUBMISSION_STRATEGY_PRE_DR3 must return strategy='SUBMIT_BEFORE_DR3'."""
        result = SUBMISSION_STRATEGY_PRE_DR3()
        assert result["strategy"] == "SUBMIT_BEFORE_DR3"

    def test_recommendation_is_to_submit(self):
        """Recommendation must indicate submission."""
        result = SUBMISSION_STRATEGY_PRE_DR3()
        assert "SUBMIT" in result["recommendation"].upper()

    def test_is_not_falsified(self):
        """Current DR2 tension must not be classified as falsified."""
        result = SUBMISSION_STRATEGY_PRE_DR3()
        assert result["is_falsified"] is False

    def test_is_tension_publishable(self):
        """Current tension must be publishable (< 3σ)."""
        result = SUBMISSION_STRATEGY_PRE_DR3()
        assert result["is_tension_publishable"] is True

    def test_rationale_nonempty(self):
        """Rationale must be a non-empty string."""
        result = SUBMISSION_STRATEGY_PRE_DR3()
        assert isinstance(result["rationale"], str)
        assert len(result["rationale"]) > 50

    def test_required_manuscript_statements_present(self):
        """Must include required manuscript statements list."""
        result = SUBMISSION_STRATEGY_PRE_DR3()
        assert "required_manuscript_statements" in result
        assert len(result["required_manuscript_statements"]) >= 1

    def test_current_wa_tension_sigma_approx_2sigma(self):
        """Current wₐ tension must be approximately 2.07σ."""
        result = SUBMISSION_STRATEGY_PRE_DR3()
        assert abs(result["current_wa_tension_sigma"] - (0.62 / 0.30)) < 0.01


# ---------------------------------------------------------------------------
# modification_roadmap_if_falsified
# ---------------------------------------------------------------------------

class TestModificationRoadmapIfFalsified:
    def test_new_sector_required_is_true(self):
        """modification_roadmap_if_falsified must have new_sector_required=True."""
        result = modification_roadmap_if_falsified()
        assert result["new_sector_required"] is True

    def test_has_new_sector_required_key(self):
        """Dict must contain 'new_sector_required' key."""
        result = modification_roadmap_if_falsified()
        assert "new_sector_required" in result

    def test_pillars_to_open_nonempty(self):
        """pillars_to_open must be a non-empty dict."""
        result = modification_roadmap_if_falsified()
        assert "pillars_to_open" in result
        assert len(result["pillars_to_open"]) >= 1

    def test_pillar_155_in_roadmap(self):
        """Pillar 155 must appear in the modification roadmap."""
        result = modification_roadmap_if_falsified()
        keys_str = str(result)
        assert "155" in keys_str or "kk_de_wa_cpl" in keys_str

    def test_observational_constraints_present(self):
        """existing_observational_constraints_on_new_bulk_fields must be present."""
        result = modification_roadmap_if_falsified()
        assert "existing_observational_constraints_on_new_bulk_fields" in result

    def test_timeline_present(self):
        """timeline_for_modification must be present."""
        result = modification_roadmap_if_falsified()
        assert "timeline_for_modification" in result

    def test_conclusion_nonempty(self):
        """conclusion must be a non-empty string."""
        result = modification_roadmap_if_falsified()
        assert isinstance(result["conclusion"], str)
        assert len(result["conclusion"]) > 20


# ---------------------------------------------------------------------------
# modification_roadmap_if_tension_increases
# ---------------------------------------------------------------------------

class TestModificationRoadmapIfTensionIncreases:
    def test_monitoring_required_nonempty(self):
        """monitoring_required must be a non-empty list."""
        result = modification_roadmap_if_tension_increases()
        assert "monitoring_required" in result
        assert len(result["monitoring_required"]) >= 1

    def test_retraction_criteria_present(self):
        """retraction_criteria must be present."""
        result = modification_roadmap_if_tension_increases()
        assert "retraction_criteria" in result

    def test_retraction_threshold_is_3sigma(self):
        """Retraction threshold must mention 3σ or 3.0σ."""
        result = modification_roadmap_if_tension_increases()
        threshold = str(result["retraction_criteria"].get("threshold_for_retraction", ""))
        assert "3" in threshold


# ---------------------------------------------------------------------------
# modification_roadmap_if_consistent
# ---------------------------------------------------------------------------

class TestModificationRoadmapIfConsistent:
    def test_claim_updates_present(self):
        """claim_updates must be present."""
        result = modification_roadmap_if_consistent()
        assert "claim_updates" in result

    def test_can_claim_confirmed_is_false(self):
        """A <2σ consistency does not confirm — can_claim_confirmed must be False."""
        result = modification_roadmap_if_consistent()
        promotion = result.get("promotion_of_wa_claim", {})
        assert promotion.get("can_claim_confirmed") is False

    def test_wording_for_preprint_present(self):
        """wording_for_preprint_update must be present and non-empty."""
        result = modification_roadmap_if_consistent()
        assert "wording_for_preprint_update" in result
        assert len(result["wording_for_preprint_update"]) > 20


# ---------------------------------------------------------------------------
# release_day_action_protocol
# ---------------------------------------------------------------------------

class TestReleaseDayActionProtocol:
    def test_falsifying_wa_returns_falsification_protocol(self):
        """Clearly falsifying wa=-1.5, sigma=0.1 → action='INITIATE_FALSIFICATION_PROTOCOL'."""
        result = release_day_action_protocol(-1.5, 0.1)
        assert result["action"] == "INITIATE_FALSIFICATION_PROTOCOL"

    def test_consistent_wa_returns_document_consistency(self):
        """wa=0.05, sigma=0.30 → action should be DOCUMENT_CONSISTENCY."""
        result = release_day_action_protocol(0.05, 0.30)
        assert result["action"] == "DOCUMENT_CONSISTENCY"

    def test_steps_nonempty(self):
        """steps must be a non-empty list."""
        result = release_day_action_protocol(-0.62, 0.30)
        assert isinstance(result["steps"], list)
        assert len(result["steps"]) >= 1

    def test_files_to_update_immediately_nonempty(self):
        """files_to_update_immediately must be non-empty."""
        result = release_day_action_protocol(-0.62, 0.30)
        assert len(result["files_to_update_immediately"]) >= 1

    def test_verdict_dict_present(self):
        """verdict must be a dict from falsification_verdict."""
        result = release_day_action_protocol(-0.62, 0.30)
        assert isinstance(result["verdict"], dict)
        assert "verdict" in result["verdict"]

    def test_tension_sigma_correct(self):
        """tension_sigma in result must match expected value."""
        result = release_day_action_protocol(-0.90, 0.10)
        # tension = 0.90 / 0.10 = 9.0σ → FALSIFIED
        assert result["tension_sigma"] == pytest.approx(9.0, rel=1e-6)
        assert result["action"] == "INITIATE_FALSIFICATION_PROTOCOL"

    def test_dr2_like_input_gives_tension_protocol(self):
        """DR2-like input gives DOCUMENT_TENSION or HIGH_TENSION, not FALSIFIED."""
        result = release_day_action_protocol(-0.62, 0.30)
        assert result["action"] in ("DOCUMENT_TENSION", "INITIATE_HIGH_TENSION_PROTOCOL")


# ---------------------------------------------------------------------------
# desi_dr3_strategic_summary
# ---------------------------------------------------------------------------

class TestDesiDr3StrategicSummary:
    def test_returns_dict(self):
        """desi_dr3_strategic_summary must return a dict."""
        result = desi_dr3_strategic_summary()
        assert isinstance(result, dict)

    def test_required_top_level_keys(self):
        """Must contain all expected top-level keys."""
        result = desi_dr3_strategic_summary()
        for key in ["title", "current_status", "um_mechanism", "dr3_projection",
                    "submission_strategy", "falsification_conditions",
                    "scenario_responses", "key_files", "immediate_action"]:
            assert key in result, f"Missing key: {key}"

    def test_submission_strategy_is_submit(self):
        """submission_strategy must be 'SUBMIT_BEFORE_DR3'."""
        result = desi_dr3_strategic_summary()
        assert result["submission_strategy"] == "SUBMIT_BEFORE_DR3"

    def test_current_status_has_tension(self):
        """current_status must contain tension information."""
        result = desi_dr3_strategic_summary()
        cs = result["current_status"]
        assert "current_tension_sigma" in cs
        assert cs["current_tension_sigma"] > 1.0

    def test_falsification_conditions_has_threshold(self):
        """falsification_conditions must have threshold_sigma = 3.0."""
        result = desi_dr3_strategic_summary()
        fc = result["falsification_conditions"]
        assert fc.get("threshold_sigma") == pytest.approx(3.0)

    def test_key_files_has_expected_entries(self):
        """key_files must reference analysis, decisions, and tracker."""
        result = desi_dr3_strategic_summary()
        kf = result["key_files"]
        assert "analysis" in kf
        assert "decisions" in kf
        assert "tracker" in kf

    def test_scenario_responses_has_all_verdicts(self):
        """scenario_responses must cover FALSIFIED, TENSION, and CONSISTENT."""
        result = desi_dr3_strategic_summary()
        sr = result["scenario_responses"]
        keys_str = str(sr)
        assert "FALSIFIED" in keys_str
        assert "TENSION" in keys_str
        assert "CONSISTENT" in keys_str

    def test_immediate_action_nonempty(self):
        """immediate_action must be a non-empty string."""
        result = desi_dr3_strategic_summary()
        assert isinstance(result["immediate_action"], str)
        assert len(result["immediate_action"]) > 20
