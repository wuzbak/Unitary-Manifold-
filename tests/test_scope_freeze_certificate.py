# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/scope_freeze_certificate.py — ET-6 Scope Freeze Certificate."""
from __future__ import annotations

import pytest

from src.core.scope_freeze_certificate import (
    ARCHITECTURE_LIMITS,
    DBP_LADDER_STATUS,
    EXTENSION_TRACK_STATUS,
    FREEZE_DATE,
    MAS_REOPEN_ALLOWED,
    MAS_STATUS,
    PARAMETER_TERMINAL_STATUS,
    ROBUSTNESS_TRACK_STATUS,
    SCOPE_VERSION,
    TOE_SCORE,
    TOE_SCORE_MAX,
    TOE_SCORE_PCT,
    WS_EXECUTION_PROGRAMME_STATUS,
    get_dbp_rung_status,
    get_parameter_status,
    is_scope_frozen,
    list_open_architecture_limits,
    scope_freeze_summary,
)


class TestProgrammeMetadata:
    def test_freeze_date(self):
        assert FREEZE_DATE == "2026-05-08"

    def test_scope_version(self):
        assert SCOPE_VERSION == "v10.14"

    def test_mas_status_complete(self):
        assert MAS_STATUS == "COMPLETE"

    def test_mas_reopen_not_allowed(self):
        assert MAS_REOPEN_ALLOWED is False

    def test_toe_score_raw(self):
        assert TOE_SCORE == pytest.approx(14.2, abs=0.01)

    def test_toe_score_max(self):
        assert TOE_SCORE_MAX == pytest.approx(28.0, abs=0.01)

    def test_toe_score_pct(self):
        assert TOE_SCORE_PCT == pytest.approx(TOE_SCORE / TOE_SCORE_MAX, rel=1e-6)
        assert 0.45 < TOE_SCORE_PCT < 0.60  # ~51%


class TestParameterTerminalStatus:
    def test_has_required_parameters(self):
        required = {"P3", "P5", "P6", "P7", "P8", "P14", "P15", "P16",
                    "P19", "P20", "P21", "P26", "P27"}
        assert required <= set(PARAMETER_TERMINAL_STATUS.keys())

    def test_all_entries_have_required_keys(self):
        required_keys = {"name", "terminal_status", "terminal_wave", "score"}
        for pid, entry in PARAMETER_TERMINAL_STATUS.items():
            assert required_keys <= set(entry.keys()), f"Missing keys in {pid}"

    def test_p3_architecture_limit_10d(self):
        p = PARAMETER_TERMINAL_STATUS["P3"]
        assert "ARCHITECTURE_LIMIT" in p["terminal_status"]
        assert "10D" in p["terminal_status"]
        assert p["score"] == pytest.approx(0.1, abs=1e-6)

    def test_p5_architecture_limit_6d(self):
        p = PARAMETER_TERMINAL_STATUS["P5"]
        assert "ARCHITECTURE_LIMIT" in p["terminal_status"]
        assert "6D" in p["terminal_status"]
        assert p["score"] == pytest.approx(0.1, abs=1e-6)

    def test_p14_best_evidence_constrained(self):
        p = PARAMETER_TERMINAL_STATUS["P14"]
        assert "BEST_EVIDENCE" in p["terminal_status"] or "CONSTRAINED" in p["terminal_status"]
        assert p["score"] == pytest.approx(0.5, abs=1e-6)

    def test_p15_best_evidence_constrained(self):
        p = PARAMETER_TERMINAL_STATUS["P15"]
        assert "CONSTRAINED" in p["terminal_status"]
        assert p["score"] == pytest.approx(0.5, abs=1e-6)
        assert "ET-2" in p.get("extension_track", "")

    def test_p19_p20_p21_geometric_estimate(self):
        for pid in ("P19", "P20", "P21"):
            p = PARAMETER_TERMINAL_STATUS[pid]
            assert "GEOMETRIC_ESTIMATE" in p["terminal_status"]
            assert p["score"] == pytest.approx(0.3, abs=1e-6)

    def test_p26_architecture_limit_7d_8d(self):
        p = PARAMETER_TERMINAL_STATUS["P26"]
        assert "ARCHITECTURE_LIMIT" in p["terminal_status"]
        assert p["score"] == pytest.approx(0.1, abs=1e-6)

    def test_all_scores_valid(self):
        valid_scores = {0.0, 0.1, 0.3, 0.5, 0.8, 1.0}
        for pid, entry in PARAMETER_TERMINAL_STATUS.items():
            assert entry["score"] in valid_scores, f"Invalid score for {pid}: {entry['score']}"


class TestDBPLadderStatus:
    def test_has_six_rungs(self):
        assert len(DBP_LADDER_STATUS) == 6

    def test_all_rungs_present(self):
        for rung_id in ("rung1", "rung2", "rung3", "rung4", "rung5", "rung6"):
            assert rung_id in DBP_LADDER_STATUS

    def test_all_rungs_solid_or_certified(self):
        for rung_id, rung in DBP_LADDER_STATUS.items():
            status = rung["status"]
            assert "SOLID" in status or "CERTIFIED" in status, (
                f"Rung {rung_id} has unexpected status: {status}"
            )

    def test_rung5_architecture_certified(self):
        rung5 = DBP_LADDER_STATUS["rung5"]
        assert "ARCHITECTURE_CERTIFIED" in rung5["status"]
        assert rung5.get("architecture_limit") is True

    def test_rung6_rung_solid(self):
        rung6 = DBP_LADDER_STATUS["rung6"]
        assert "SOLID" in rung6["status"]
        assert rung6.get("hard_gate_pass") is True


class TestRobustnessTrackStatus:
    def test_t1_t2_t3_pass(self):
        for tid in ("T1", "T2", "T3"):
            assert ROBUSTNESS_TRACK_STATUS[tid]["status"] == "PASS"

    def test_t4_optional_not_activated(self):
        t4 = ROBUSTNESS_TRACK_STATUS["T4"]
        assert t4["status"] == "OPTIONAL_NOT_ACTIVATED"

    def test_all_required_tracks_present(self):
        for tid in ("T1", "T2", "T3", "T4"):
            assert tid in ROBUSTNESS_TRACK_STATUS


class TestExtensionTrackStatus:
    def test_et1_to_et4_delivered(self):
        for tid in ("ET-1", "ET-2", "ET-3", "ET-4"):
            assert EXTENSION_TRACK_STATUS[tid]["status"] == "DELIVERED"

    def test_et5_et6_delivered(self):
        for tid in ("ET-5", "ET-6"):
            assert EXTENSION_TRACK_STATUS[tid]["status"] == "DELIVERED"

    def test_all_tracks_have_artifact(self):
        for tid, entry in EXTENSION_TRACK_STATUS.items():
            assert "artifact" in entry, f"Missing artifact in {tid}"

    def test_et1_p5(self):
        assert "P5" in EXTENSION_TRACK_STATUS["ET-1"]["parameter"]

    def test_et2_p14_p15(self):
        et2 = EXTENSION_TRACK_STATUS["ET-2"]
        assert "P14" in et2["parameter"] or "P15" in et2["parameter"]

    def test_et3_p19_p20_p21(self):
        et3 = EXTENSION_TRACK_STATUS["ET-3"]
        assert "P19" in et3["parameter"]

    def test_et4_p3(self):
        assert "P3" in EXTENSION_TRACK_STATUS["ET-4"]["parameter"]


class TestArchitectureLimits:
    def test_has_five_limits(self):
        assert len(ARCHITECTURE_LIMITS) == 5

    def test_all_limits_have_required_keys(self):
        required = {"parameter", "dimension_needed", "description", "current_best"}
        for lid, entry in ARCHITECTURE_LIMITS.items():
            assert required <= set(entry.keys()), f"Missing keys in {lid}"

    def test_p3_limit_10d(self):
        assert "10D" in ARCHITECTURE_LIMITS["A-P3"]["dimension_needed"]

    def test_p5_limit_6d(self):
        assert "6D" in ARCHITECTURE_LIMITS["A-P5"]["dimension_needed"]

    def test_p14_limit_9d(self):
        assert "9D" in ARCHITECTURE_LIMITS["A-P14"]["dimension_needed"]

    def test_p19_p21_limit_6d(self):
        assert "6D" in ARCHITECTURE_LIMITS["A-P19-P21"]["dimension_needed"]


class TestWSExecutionProgrammeStatus:
    def test_has_four_workstreams(self):
        assert set(WS_EXECUTION_PROGRAMME_STATUS.keys()) == {
            "WS-I", "WS-II", "WS-III", "WS-IV"
        }

    def test_ws2_pass_freeze(self):
        assert WS_EXECUTION_PROGRAMME_STATUS["WS-II"]["status"] == "PASS_FREEZE"

    def test_others_targeted_follow_up_freeze(self):
        for ws_id in ("WS-I", "WS-III", "WS-IV"):
            assert WS_EXECUTION_PROGRAMME_STATUS[ws_id]["status"] == "TARGETED_FOLLOW_UP_FREEZE"

    def test_no_recycle_into_mas(self):
        assert all(
            not v["recycle_into_mas"] for v in WS_EXECUTION_PROGRAMME_STATUS.values()
        )


class TestGetParameterStatus:
    def test_returns_dict(self):
        result = get_parameter_status("P3")
        assert isinstance(result, dict)

    def test_returns_copy(self):
        r1 = get_parameter_status("P3")
        r2 = get_parameter_status("P3")
        r1["score"] = 999.0
        assert r2["score"] == pytest.approx(0.1, abs=1e-6)

    def test_unknown_raises_key_error(self):
        with pytest.raises(KeyError, match="P999"):
            get_parameter_status("P999")

    def test_all_tracked_parameters_accessible(self):
        for pid in PARAMETER_TERMINAL_STATUS:
            d = get_parameter_status(pid)
            assert "terminal_status" in d


class TestGetDBPRungStatus:
    def test_returns_dict(self):
        result = get_dbp_rung_status("rung1")
        assert isinstance(result, dict)

    def test_returns_copy(self):
        r1 = get_dbp_rung_status("rung1")
        r1["status"] = "MUTATED"
        r2 = get_dbp_rung_status("rung1")
        assert r2["status"] == "SOLID"

    def test_unknown_raises_key_error(self):
        with pytest.raises(KeyError, match="rung99"):
            get_dbp_rung_status("rung99")


class TestListOpenArchitectureLimits:
    def test_returns_list(self):
        result = list_open_architecture_limits()
        assert isinstance(result, list)

    def test_sorted(self):
        result = list_open_architecture_limits()
        assert result == sorted(result)

    def test_contains_expected_keys(self):
        result = list_open_architecture_limits()
        for key in ("A-P3", "A-P5", "A-P14"):
            assert key in result


class TestIsScopeFrozen:
    def test_always_true(self):
        assert is_scope_frozen() is True

    def test_called_multiple_times(self):
        for _ in range(5):
            assert is_scope_frozen() is True


class TestScopeFreezeSummary:
    def test_returns_dict(self):
        s = scope_freeze_summary()
        assert isinstance(s, dict)

    def test_required_keys(self):
        s = scope_freeze_summary()
        required = {
            "scope_version", "freeze_date", "mas_status", "mas_reopen_allowed",
            "toe_score_raw", "toe_score_max", "toe_score_pct",
            "parameter_count_tracked", "parameter_status_counts",
            "dbp_ladder_rungs", "dbp_all_solid_or_certified",
            "robustness_tracks_complete", "extension_tracks_complete",
            "architecture_limits_count", "scope_frozen", "terminal_verdict",
        }
        assert required <= set(s.keys())

    def test_mas_complete(self):
        s = scope_freeze_summary()
        assert s["mas_status"] == "COMPLETE"
        assert s["mas_reopen_allowed"] is False

    def test_scope_frozen_true(self):
        s = scope_freeze_summary()
        assert s["scope_frozen"] is True

    def test_dbp_all_solid(self):
        s = scope_freeze_summary()
        assert s["dbp_all_solid_or_certified"] is True

    def test_robustness_complete(self):
        s = scope_freeze_summary()
        assert s["robustness_tracks_complete"] is True

    def test_extension_complete(self):
        s = scope_freeze_summary()
        assert s["extension_tracks_complete"] is True

    def test_toe_score_pct_range(self):
        s = scope_freeze_summary()
        assert 0.45 < s["toe_score_pct"] < 0.60

    def test_six_dbp_rungs(self):
        s = scope_freeze_summary()
        assert s["dbp_ladder_rungs"] == 6

    def test_architecture_limits_count(self):
        s = scope_freeze_summary()
        assert s["architecture_limits_count"] == 5

    def test_parameter_status_counts_sum_to_tracked(self):
        s = scope_freeze_summary()
        total = sum(s["parameter_status_counts"].values())
        assert total == s["parameter_count_tracked"]

    def test_terminal_verdict_contains_complete(self):
        s = scope_freeze_summary()
        assert "complete" in s["terminal_verdict"].lower() or "complete" in s["terminal_verdict"]

    def test_primary_falsifier_mentioned(self):
        s = scope_freeze_summary()
        assert "LiteBIRD" in s["primary_falsifier"]
        assert "0.273" in s["primary_falsifier"] or "birefringence" in s["primary_falsifier"].lower()

    def test_ws_execution_programme_summary_counts(self):
        s = scope_freeze_summary()
        assert s["ws_execution_programme_count"] == 4
        assert s["ws_execution_pass_freeze_count"] == 1
        assert s["ws_execution_targeted_follow_up_freeze_count"] == 3
        assert s["ws_execution_no_mas_recycle"] is True
