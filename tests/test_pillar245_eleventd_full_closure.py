# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 245 — 11D / Terminal Full-Closure Engine."""

from __future__ import annotations

import pytest

from src.core.pillar245_eleventd_full_closure import (
    ADJACENCY_TRACK_LABEL,
    BRAID_PAIR,
    ETA_BAR,
    ELEVENTD_CLOSURE_TRACK_LABEL,
    K_CS,
    LANE_ORDER,
    N_LANES,
    N_W,
    PI_KR,
    __provenance__,
    eleventd_closure_summary,
    eleventd_lane_reports,
    pillar245_eleventd_full_closure_report,
    separation_guard,
    terminal_closure_certificate,
    terminal_runtime_seed,
)

# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 245


def test_provenance_title_contains_11d():
    assert "11D" in __provenance__["title"]


def test_provenance_adjacent_track_label_in_status():
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]


def test_provenance_license():
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_provenance_fingerprint():
    assert __provenance__["fingerprint"] == "(5, 7, 74)"


# ---------------------------------------------------------------------------
# Runtime seed constants
# ---------------------------------------------------------------------------

def test_n_w_is_five():
    assert N_W == 5


def test_k_cs_is_74():
    assert K_CS == 74


def test_braid_pair():
    assert BRAID_PAIR == (5, 7)


def test_eta_bar():
    assert ETA_BAR == pytest.approx(0.5)


def test_pi_kr():
    assert PI_KR == pytest.approx(37.0)


# ---------------------------------------------------------------------------
# Track labels and lane structure
# ---------------------------------------------------------------------------

def test_adjacency_track_label():
    assert ADJACENCY_TRACK_LABEL == "ADJACENT_TRACK_NON_HARDGATE"


def test_closure_track_label():
    assert ELEVENTD_CLOSURE_TRACK_LABEL == "ELEVENTD_FULL_CLOSURE_TRACK"


def test_lane_order_length():
    assert len(LANE_ORDER) == 5


def test_n_lanes_matches_lane_order():
    assert N_LANES == len(LANE_ORDER)


def test_lane_names_present():
    assert "hw_kickoff_scaffold" in LANE_ORDER
    assert "hw_hard_gate" in LANE_ORDER
    assert "g4_flux_vacuum_link" in LANE_ORDER
    assert "uv_vacuum_selection" in LANE_ORDER
    assert "bridge_burn_5d" in LANE_ORDER


# ---------------------------------------------------------------------------
# Separation guard
# ---------------------------------------------------------------------------

def test_separation_guard_label():
    guard = separation_guard()
    assert guard["label"] == ADJACENCY_TRACK_LABEL


def test_separation_guard_track():
    guard = separation_guard()
    assert guard["track"] == ELEVENTD_CLOSURE_TRACK_LABEL


def test_separation_guard_hardgate_isolation():
    guard = separation_guard()
    assert guard["hardgate_isolation"] is True


def test_separation_guard_no_toe_score_delta():
    guard = separation_guard()
    assert guard["toe_score_delta_allowed"] is False


def test_separation_guard_no_physics_promotion():
    guard = separation_guard()
    assert guard["physics_claim_promotion_allowed"] is False


# ---------------------------------------------------------------------------
# Terminal runtime seed
# ---------------------------------------------------------------------------

def test_terminal_runtime_seed_n_w():
    seed = terminal_runtime_seed()
    assert seed["n_w"] == 5


def test_terminal_runtime_seed_k_cs():
    seed = terminal_runtime_seed()
    assert seed["k_cs"] == 74


def test_terminal_runtime_seed_braid_pair():
    seed = terminal_runtime_seed()
    assert tuple(seed["braid_pair"]) == (5, 7)


def test_terminal_runtime_seed_eta_bar():
    seed = terminal_runtime_seed()
    assert seed["eta_bar"] == pytest.approx(0.5)


def test_terminal_runtime_seed_pi_kr():
    seed = terminal_runtime_seed()
    assert seed["pi_kR"] == pytest.approx(37.0)


def test_terminal_runtime_seed_bridge_burned():
    seed = terminal_runtime_seed()
    assert seed["bridge_burned"] is True


def test_terminal_runtime_seed_locked():
    seed = terminal_runtime_seed()
    assert seed["seed_locked"] is True


def test_terminal_runtime_seed_status():
    seed = terminal_runtime_seed()
    assert seed["status"] == "RUNTIME_SEED_LOCKED"


# ---------------------------------------------------------------------------
# Lane reports structure
# ---------------------------------------------------------------------------

def test_lane_reports_keys_match_lane_order():
    reports = eleventd_lane_reports()
    assert tuple(reports.keys()) == LANE_ORDER


def test_lane_reports_have_artifact_paths():
    reports = eleventd_lane_reports()
    for lane in LANE_ORDER:
        assert reports[lane]["artifact"].startswith("src/")


def test_all_lanes_have_pass_field():
    reports = eleventd_lane_reports()
    for lane in LANE_ORDER:
        assert isinstance(reports[lane]["pass"], bool)


def test_all_lanes_have_status_field():
    reports = eleventd_lane_reports()
    for lane in LANE_ORDER:
        assert isinstance(reports[lane]["status"], str)


def test_all_lanes_pass():
    reports = eleventd_lane_reports()
    for lane in LANE_ORDER:
        assert reports[lane]["pass"] is True, f"Lane '{lane}' did not pass."


# ---------------------------------------------------------------------------
# Individual lane evidence
# ---------------------------------------------------------------------------

def test_hw_kickoff_scaffold_status():
    lane = eleventd_lane_reports()["hw_kickoff_scaffold"]
    assert lane["status"] == "KICKOFF_IMPLEMENTED"


def test_hw_kickoff_scaffold_kill_switch():
    lane = eleventd_lane_reports()["hw_kickoff_scaffold"]
    assert lane["evidence"]["kill_switch_pass"] is True


def test_hw_kickoff_scaffold_gate_count():
    lane = eleventd_lane_reports()["hw_kickoff_scaffold"]
    assert lane["evidence"]["gate_count"] == 4


def test_hw_hard_gate_status():
    lane = eleventd_lane_reports()["hw_hard_gate"]
    assert lane["status"] == "RUNG_SOLID"


def test_hw_hard_gate_pass():
    lane = eleventd_lane_reports()["hw_hard_gate"]
    assert lane["evidence"]["hard_gate_pass"] is True


def test_hw_hard_gate_supercharges_4d():
    lane = eleventd_lane_reports()["hw_hard_gate"]
    assert lane["evidence"]["n_supercharges_4d"] == 4


def test_hw_hard_gate_dim_e8xe8():
    lane = eleventd_lane_reports()["hw_hard_gate"]
    assert lane["evidence"]["dim_e8xe8"] == 496


def test_hw_hard_gate_n_boundaries():
    lane = eleventd_lane_reports()["hw_hard_gate"]
    assert lane["evidence"]["n_boundaries_s1z2"] == 2


def test_g4_flux_status():
    lane = eleventd_lane_reports()["g4_flux_vacuum_link"]
    assert lane["status"] == "UNIQUE_UV_FLUX_SELECTION"


def test_g4_flux_unique_selected_n_w():
    lane = eleventd_lane_reports()["g4_flux_vacuum_link"]
    assert lane["evidence"]["unique_flux_selected_n_w"] == 5


def test_g4_flux_surviving_candidates():
    lane = eleventd_lane_reports()["g4_flux_vacuum_link"]
    assert lane["evidence"]["surviving_candidates"] == [5]


def test_g4_flux_no_score_inflation():
    lane = eleventd_lane_reports()["g4_flux_vacuum_link"]
    assert lane["evidence"]["no_score_inflation"] is True


def test_uv_vacuum_selection_status():
    lane = eleventd_lane_reports()["uv_vacuum_selection"]
    assert lane["status"] == "CANONICAL_UV_VACUUM_FIXED"


def test_uv_vacuum_selection_n_w():
    lane = eleventd_lane_reports()["uv_vacuum_selection"]
    assert lane["evidence"]["selected_n_w"] == 5


def test_uv_vacuum_unique_selection():
    lane = eleventd_lane_reports()["uv_vacuum_selection"]
    assert lane["evidence"]["unique_selection"] is True


def test_bridge_burn_status():
    lane = eleventd_lane_reports()["bridge_burn_5d"]
    assert lane["status"] == "BRIDGE_BURNED_RUNTIME_REDUCED"


def test_bridge_burn_burned():
    lane = eleventd_lane_reports()["bridge_burn_5d"]
    assert lane["evidence"]["bridge_burned"] is True


def test_bridge_burn_runtime_policy():
    lane = eleventd_lane_reports()["bridge_burn_5d"]
    assert lane["evidence"]["runtime_policy"] == "5D_RUNTIME_ONLY"


# ---------------------------------------------------------------------------
# Closure summary
# ---------------------------------------------------------------------------

def test_closure_summary_track():
    summary = eleventd_closure_summary()
    assert summary["track"] == ELEVENTD_CLOSURE_TRACK_LABEL


def test_closure_summary_all_lanes_passed():
    summary = eleventd_closure_summary()
    assert set(summary["passed_lanes"]) == set(LANE_ORDER)


def test_closure_summary_no_failed_lanes():
    summary = eleventd_closure_summary()
    assert summary["failed_lanes"] == []


def test_closure_summary_index_one():
    summary = eleventd_closure_summary()
    assert summary["closure_index"] == pytest.approx(1.0)


def test_closure_summary_fully_closed():
    summary = eleventd_closure_summary()
    assert summary["fully_closed"] is True


def test_closure_summary_status():
    summary = eleventd_closure_summary()
    assert summary["status"] == "ELEVENTD_FULL_CLOSURE_CERTIFIED"


# ---------------------------------------------------------------------------
# Terminal closure certificate
# ---------------------------------------------------------------------------

def test_terminal_cert_certified():
    cert = terminal_closure_certificate()
    assert cert["certified"] is True


def test_terminal_cert_closure_status():
    cert = terminal_closure_certificate()
    assert cert["closure_status"] == "ELEVENTD_FULL_CLOSURE_CERTIFIED"


def test_terminal_cert_runtime_seed_n_w():
    cert = terminal_closure_certificate()
    assert cert["runtime_seed"]["n_w"] == 5


def test_terminal_cert_runtime_seed_k_cs():
    cert = terminal_closure_certificate()
    assert cert["runtime_seed"]["k_cs"] == 74


def test_terminal_cert_runtime_seed_braid_pair():
    cert = terminal_closure_certificate()
    assert tuple(cert["runtime_seed"]["braid_pair"]) == (5, 7)


def test_terminal_cert_bridge_burned():
    cert = terminal_closure_certificate()
    assert cert["bridge_burned"] is True


def test_terminal_cert_no_score_inflation():
    cert = terminal_closure_certificate()
    assert cert["no_score_inflation"] is True


def test_terminal_cert_message_contains_nw5():
    cert = terminal_closure_certificate()
    assert "n_w = 5" in cert["message"]


def test_terminal_cert_falsification_condition():
    cert = terminal_closure_certificate()
    assert "FALSIFIED" in cert["falsification_condition"]
    assert "n_w=5" in cert["falsification_condition"]


# ---------------------------------------------------------------------------
# Full integrated report
# ---------------------------------------------------------------------------

EXPECTED_TOP_KEYS = (
    "pillar",
    "title",
    "status",
    "adjacency_track_label",
    "eleventd_closure_track",
    "adjacent_toe_score_delta",
    "separation_guard",
    "lane_reports",
    "closure_summary",
    "terminal_runtime_seed",
    "terminal_closure_certificate",
    "predecessor_pillar",
    "predecessor_handoff_consumed",
    "falsification_condition",
)


def test_full_report_has_expected_keys():
    report = pillar245_eleventd_full_closure_report()
    for key in EXPECTED_TOP_KEYS:
        assert key in report, f"Missing key: {key}"


def test_full_report_pillar_number():
    report = pillar245_eleventd_full_closure_report()
    assert report["pillar"] == 245


def test_full_report_zero_toe_delta():
    report = pillar245_eleventd_full_closure_report()
    assert report["adjacent_toe_score_delta"] == pytest.approx(0.0)


def test_full_report_predecessor_is_244():
    report = pillar245_eleventd_full_closure_report()
    assert report["predecessor_pillar"] == 244


def test_full_report_predecessor_handoff_consumed():
    report = pillar245_eleventd_full_closure_report()
    assert report["predecessor_handoff_consumed"] is True


def test_full_report_closure_certified():
    report = pillar245_eleventd_full_closure_report()
    assert report["closure_summary"]["status"] == "ELEVENTD_FULL_CLOSURE_CERTIFIED"


def test_full_report_cert_certified():
    report = pillar245_eleventd_full_closure_report()
    assert report["terminal_closure_certificate"]["certified"] is True


def test_full_report_adjacency_label():
    report = pillar245_eleventd_full_closure_report()
    assert report["adjacency_track_label"] == "ADJACENT_TRACK_NON_HARDGATE"


def test_full_report_separation_guard_isolation():
    report = pillar245_eleventd_full_closure_report()
    assert report["separation_guard"]["hardgate_isolation"] is True


def test_full_report_falsification_condition_non_empty():
    report = pillar245_eleventd_full_closure_report()
    assert len(report["falsification_condition"]) > 0
