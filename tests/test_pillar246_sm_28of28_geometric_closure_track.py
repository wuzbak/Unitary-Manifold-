# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 246 — v11.1 SM 28/28 Pure-Geometry Closure Track."""

from __future__ import annotations

import pytest

from src.core.pillar246_sm_28of28_geometric_closure_track import (
    ADJACENCY_TRACK_LABEL,
    BRAID_PAIR,
    ETA_BAR,
    K_CS,
    N_W,
    PI_KR,
    SM_2828_TRACK_LABEL,
    SM_PARAMETER_IDS,
    __provenance__,
    pillar246_sm_28of28_report,
    separation_guard,
    sm_28of28_closure_certificate,
    sm_28of28_closure_summary,
    sm_28of28_parameter_ledger,
)


def test_provenance():
    assert __provenance__["pillar"] == 246
    assert __provenance__["version"] == "v11.1"
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]


def test_seed_constants():
    assert N_W == 5
    assert K_CS == 74
    assert BRAID_PAIR == (5, 7)
    assert ETA_BAR == pytest.approx(0.5)
    assert PI_KR == pytest.approx(37.0)


def test_track_labels():
    assert ADJACENCY_TRACK_LABEL == "ADJACENT_TRACK_NON_HARDGATE"
    assert SM_2828_TRACK_LABEL == "SM_28OF28_PURE_GEOMETRY_TRACK_V11_1"


def test_separation_guard():
    guard = separation_guard()
    assert guard["label"] == ADJACENCY_TRACK_LABEL
    assert guard["track"] == SM_2828_TRACK_LABEL
    assert guard["hardgate_isolation"] is True
    assert guard["toe_score_delta_allowed"] is False
    assert guard["physics_claim_promotion_allowed"] is False


def test_parameter_ids():
    assert len(SM_PARAMETER_IDS) == 28
    assert SM_PARAMETER_IDS[0] == "P1"
    assert SM_PARAMETER_IDS[-1] == "P28"


def test_ledger_covers_all_parameters():
    ledger = sm_28of28_parameter_ledger()
    assert tuple(ledger.keys()) == SM_PARAMETER_IDS


def test_all_entries_marked_closed_status():
    ledger = sm_28of28_parameter_ledger()
    for pid in SM_PARAMETER_IDS:
        assert ledger[pid]["status"] == "DERIVED_PURE_GEOMETRY_ADJACENT_V11_1"
        assert len(ledger[pid]["derivation_route"]) > 10


def test_p26_and_p27_present():
    ledger = sm_28of28_parameter_ledger()
    assert ledger["P26"]["name"] == "θ_QCD"
    assert ledger["P26"]["geo_value"] == pytest.approx(0.0)
    assert "Λ_CC" in ledger["P27"]["name"]


def test_summary_is_28of28_closed():
    summary = sm_28of28_closure_summary()
    assert summary["total_parameters"] == 28
    assert summary["n_closed"] == 28
    assert summary["n_open"] == 0
    assert summary["closure_index"] == pytest.approx(1.0)
    assert summary["status"] == "SM_28OF28_GEOMETRICALLY_CLOSED"


def test_certificate():
    cert = sm_28of28_closure_certificate()
    assert cert["certified"] is True
    assert cert["closed_count"] == 28
    assert cert["total_count"] == 28
    assert "FALSIFIED" in cert["falsification_condition"]


def test_full_report_shape():
    report = pillar246_sm_28of28_report()
    for key in (
        "pillar",
        "title",
        "version",
        "status",
        "adjacency_track_label",
        "closure_track",
        "adjacent_toe_score_delta",
        "separation_guard",
        "parameter_ledger",
        "closure_summary",
        "closure_certificate",
        "falsification_condition",
    ):
        assert key in report
    assert report["pillar"] == 246
    assert report["adjacent_toe_score_delta"] == pytest.approx(0.0)
    assert report["closure_summary"]["n_closed"] == 28
