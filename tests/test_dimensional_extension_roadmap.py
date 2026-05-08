# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/dimensional_extension_roadmap.py — ET-6 Dimensional Extension Roadmap."""
from __future__ import annotations

import pytest

from src.core.dimensional_extension_roadmap import (
    WORKSTREAM_CATALOGUE,
    execution_freeze_status,
    get_workstream,
    list_workstreams,
    readiness_check,
    roadmap_summary,
)


class TestWorkstreamCatalogue:
    def test_has_four_workstreams(self):
        assert len(WORKSTREAM_CATALOGUE) == 4

    def test_workstream_ids_present(self):
        for ws_id in ("WS-I", "WS-II", "WS-III", "WS-IV"):
            assert ws_id in WORKSTREAM_CATALOGUE

    def test_all_required_keys(self):
        required = {
            "title", "dimension_target", "parameter_target", "current_status",
            "current_best_artifact", "current_residual", "goal", "prerequisites",
            "key_calculation", "expected_outcome", "readiness_criteria",
            "estimated_dimension_reach", "falsification_link",
        }
        for ws_id, ws in WORKSTREAM_CATALOGUE.items():
            assert required <= set(ws.keys()), f"Missing keys in {ws_id}"

    def test_prerequisites_are_lists(self):
        for ws_id, ws in WORKSTREAM_CATALOGUE.items():
            assert isinstance(ws["prerequisites"], list), f"{ws_id}: prerequisites not a list"
            assert len(ws["prerequisites"]) > 0, f"{ws_id}: prerequisites is empty"

    def test_readiness_criteria_are_dicts(self):
        for ws_id, ws in WORKSTREAM_CATALOGUE.items():
            assert isinstance(ws["readiness_criteria"], dict), \
                f"{ws_id}: readiness_criteria not a dict"


class TestWorkstreamContents:
    def test_ws1_p5_6d(self):
        ws = WORKSTREAM_CATALOGUE["WS-I"]
        assert "P5" in ws["parameter_target"]
        assert "6D" in ws["dimension_target"]
        assert "ET_1_baseline" in ws["readiness_criteria"]
        assert ws["readiness_criteria"]["ET_1_baseline"] is True

    def test_ws2_p14_p15_9d(self):
        ws = WORKSTREAM_CATALOGUE["WS-II"]
        assert "P14" in ws["parameter_target"] or "P15" in ws["parameter_target"]
        assert "9D" in ws["dimension_target"]
        assert "ET_2_baseline" in ws["readiness_criteria"]
        assert ws["readiness_criteria"]["ET_2_baseline"] is True

    def test_ws3_p19_p21_6d(self):
        ws = WORKSTREAM_CATALOGUE["WS-III"]
        assert "P19" in ws["parameter_target"]
        assert "6D" in ws["dimension_target"]
        assert "ET_3_baseline" in ws["readiness_criteria"]
        assert ws["readiness_criteria"]["ET_3_baseline"] is True

    def test_ws4_p3_10d(self):
        ws = WORKSTREAM_CATALOGUE["WS-IV"]
        assert "P3" in ws["parameter_target"]
        assert "10D" in ws["dimension_target"]
        assert "ET_4_baseline" in ws["readiness_criteria"]
        assert ws["readiness_criteria"]["ET_4_baseline"] is True

    def test_ws1_current_status_architecture_limit(self):
        ws = WORKSTREAM_CATALOGUE["WS-I"]
        assert "ARCHITECTURE_LIMIT" in ws["current_status"]

    def test_ws2_current_status_best_evidence(self):
        ws = WORKSTREAM_CATALOGUE["WS-II"]
        assert "BEST_EVIDENCE" in ws["current_status"] or "CONSTRAINED" in ws["current_status"]

    def test_ws3_current_status_geometric_estimate(self):
        ws = WORKSTREAM_CATALOGUE["WS-III"]
        assert "GEOMETRIC_ESTIMATE" in ws["current_status"]

    def test_ws4_current_status_architecture_limit_10d(self):
        ws = WORKSTREAM_CATALOGUE["WS-IV"]
        assert "ARCHITECTURE_LIMIT" in ws["current_status"]
        assert "10D" in ws["current_status"]

    def test_all_falsification_links_nonempty(self):
        for ws_id, ws in WORKSTREAM_CATALOGUE.items():
            assert isinstance(ws["falsification_link"], str)
            assert len(ws["falsification_link"]) > 20, f"{ws_id}: falsification link too short"

    def test_all_current_best_artifacts_point_to_src(self):
        for ws_id, ws in WORKSTREAM_CATALOGUE.items():
            assert ws["current_best_artifact"].startswith("src/"), \
                f"{ws_id}: artifact path doesn't start with 'src/'"


class TestGetWorkstream:
    def test_returns_dict(self):
        ws = get_workstream("WS-I")
        assert isinstance(ws, dict)

    def test_returns_copy(self):
        ws1 = get_workstream("WS-I")
        ws2 = get_workstream("WS-I")
        ws1["title"] = "MUTATED"
        assert ws2["title"] != "MUTATED"

    def test_unknown_raises_key_error(self):
        with pytest.raises(KeyError, match="WS-UNKNOWN"):
            get_workstream("WS-UNKNOWN")

    def test_all_ids_valid(self):
        for ws_id in list_workstreams():
            d = get_workstream(ws_id)
            assert "dimension_target" in d


class TestListWorkstreams:
    def test_returns_list(self):
        result = list_workstreams()
        assert isinstance(result, list)

    def test_sorted(self):
        result = list_workstreams()
        assert result == sorted(result)

    def test_length_four(self):
        assert len(list_workstreams()) == 4

    def test_contains_all_ids(self):
        ids = list_workstreams()
        for ws_id in ("WS-I", "WS-II", "WS-III", "WS-IV"):
            assert ws_id in ids


class TestReadinessCheck:
    def test_returns_dict(self):
        result = readiness_check()
        assert isinstance(result, dict)

    def test_has_all_workstreams(self):
        result = readiness_check()
        for ws_id in list_workstreams():
            assert ws_id in result

    def test_each_entry_has_required_keys(self):
        result = readiness_check()
        required = {
            "title", "criteria_passed", "criteria_total",
            "readiness_fraction", "baseline_delivered",
            "current_status", "dimension_target",
        }
        for ws_id, entry in result.items():
            assert required <= set(entry.keys()), f"Missing keys for {ws_id}"

    def test_all_baselines_delivered(self):
        result = readiness_check()
        for ws_id, entry in result.items():
            assert entry["baseline_delivered"] is True, \
                f"{ws_id}: baseline not marked as delivered"

    def test_readiness_fraction_in_range(self):
        result = readiness_check()
        for ws_id, entry in result.items():
            assert 0.0 <= entry["readiness_fraction"] <= 1.0, \
                f"{ws_id}: readiness fraction out of range"

    def test_criteria_passed_le_total(self):
        result = readiness_check()
        for ws_id, entry in result.items():
            assert entry["criteria_passed"] <= entry["criteria_total"], \
                f"{ws_id}: more passed than total"

    def test_at_least_one_criterion_passed_per_workstream(self):
        result = readiness_check()
        for ws_id, entry in result.items():
            assert entry["criteria_passed"] >= 1, \
                f"{ws_id}: no criteria passed (at least ET baseline should pass)"


class TestRoadmapSummary:
    def test_returns_dict(self):
        s = roadmap_summary()
        assert isinstance(s, dict)

    def test_required_keys(self):
        s = roadmap_summary()
        required = {
            "workstream_count", "workstream_ids", "dimension_targets",
            "parameter_targets", "readiness", "total_baselines_delivered",
            "falsification_links", "governance", "note",
        }
        assert required <= set(s.keys())

    def test_workstream_count_four(self):
        s = roadmap_summary()
        assert s["workstream_count"] == 4

    def test_all_four_baselines_delivered(self):
        s = roadmap_summary()
        assert s["total_baselines_delivered"] == 4

    def test_governance_mas_reopen_false(self):
        s = roadmap_summary()
        assert s["governance"]["mas_reopen_allowed"] is False

    def test_dimension_targets_all_present(self):
        s = roadmap_summary()
        for ws_id in list_workstreams():
            assert ws_id in s["dimension_targets"]

    def test_parameter_targets_all_present(self):
        s = roadmap_summary()
        for ws_id in list_workstreams():
            assert ws_id in s["parameter_targets"]

    def test_falsification_links_all_present(self):
        s = roadmap_summary()
        for ws_id in list_workstreams():
            assert ws_id in s["falsification_links"]

    def test_dimension_targets_include_6d_9d_10d(self):
        s = roadmap_summary()
        targets = set(s["dimension_targets"].values())
        assert any("6D" in t for t in targets)
        assert any("9D" in t for t in targets)
        assert any("10D" in t for t in targets)

    def test_note_mentions_architecture_limited(self):
        s = roadmap_summary()
        assert "architecture" in s["note"].lower() or "architecture-limited" in s["note"].lower()

    def test_workstream_ids_sorted(self):
        s = roadmap_summary()
        assert s["workstream_ids"] == sorted(s["workstream_ids"])


class TestExecutionFreezeStatus:
    def test_returns_all_workstreams(self):
        statuses = execution_freeze_status()
        assert set(statuses.keys()) == {"WS-I", "WS-II", "WS-III", "WS-IV"}

    def test_ws2_pass_freeze(self):
        statuses = execution_freeze_status()
        assert statuses["WS-II"]["status"] == "PASS_FREEZE"

    def test_other_workstreams_pass_freeze(self):
        statuses = execution_freeze_status()
        for ws_id in ("WS-I", "WS-III", "WS-IV"):
            assert statuses[ws_id]["status"] == "PASS_FREEZE"

    def test_post_freeze_actions_valid(self):
        statuses = execution_freeze_status()
        valid = {"frozen"}
        for entry in statuses.values():
            assert entry["post_freeze_action"] in valid
