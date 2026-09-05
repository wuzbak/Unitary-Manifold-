# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import json

import pytest

import src.core.pillar1080_internal_lane_resolution_packet as p1080

from src.core.pillar1080_internal_lane_resolution_packet import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    critique_internal_lane_resolution_packet,
    pillar1080_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1080
    assert PILLAR_GATE == "CRITIQUE_INTERNAL_LANE_RESOLUTION_PACKET"
    assert PILLAR_STATUS == "CRITIQUE_INTERNAL_LANE_RESOLUTION_PACKET_COMPLETE"
    assert isinstance(PILLAR_VALID, bool)


def test_packet_structure() -> None:
    report = critique_internal_lane_resolution_packet()
    lane_ids = {row["lane"] for row in report["rows"]}
    assert lane_ids == {
        "FLAVOR_CL",
        "UV_SHARED_OBJECT",
        "CMB_AMPLITUDE",
        "NEUTRINO_DEPENDENCY",
    }
    assert report["counts"]["tightened"] == 0
    assert report["scientific_progress"] is False
    assert report["outcome"] == "INTERNAL_LANES_CARRY_FORWARD_OPEN"
    assert report["honesty_boundaries"]["no_unearned_closure_labels"] is True
    assert report["valid"] is True


def test_neutrino_row_uses_exp3_status(monkeypatch, tmp_path) -> None:
    payload = {
        "predictions": [{"id": "EXP-3", "status": "PASS", "verdict": "ok"}],
    }
    path = tmp_path / "live.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(p1080, "_LIVE_STATUS", path)
    row = p1080._neutrino_lane_row()
    assert row["current_status"] == "PASS"
    assert row["deterministic_verdict"] == "PASS"
    assert row["tightened"] is False


def test_neutrino_row_fail_closed_when_exp3_missing(monkeypatch, tmp_path) -> None:
    path = tmp_path / "live.json"
    path.write_text(json.dumps({"predictions": []}), encoding="utf-8")
    monkeypatch.setattr(p1080, "_LIVE_STATUS", path)
    row = p1080._neutrino_lane_row()
    assert row["current_status"] == "MISSING_EXP3_STATUS"
    assert row["deterministic_verdict"] == "TENSION"
    assert row["tightened"] is False


def test_summary() -> None:
    summary = pillar1080_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["routing_counts"]["tightened"] == 0


@pytest.mark.parametrize("status", ["UNCONFIRMED", "NOT_RESOLVED", "NOT_PASS", "CONFIRMED_PENDING", "unknown"])
def test_neutrino_status_substrings_cannot_earn_pass(monkeypatch, tmp_path, status) -> None:
    path = tmp_path / "live.json"
    path.write_text(json.dumps({"predictions": [{"id": "EXP-3", "status": status}]}))
    monkeypatch.setattr(p1080, "_LIVE_STATUS", path)
    row = p1080._neutrino_lane_row()
    assert row["deterministic_verdict"] == "TENSION"
    assert row["tightened"] is False


def test_cmb_terminal_route_labels_are_not_irreducibility_evidence(monkeypatch) -> None:
    monkeypatch.setattr(p1080, "pillar999_summary", lambda: {
        "evidence_ledger": {"terminal_eft_routes": True}, "status": "historical"
    })
    row = p1080._cmb_lane_row()
    assert row["current_status"] == "CMB_AMPLITUDE_DERIVATION_OPEN"
    assert row["tightened"] is False
    assert row["runtime_flip_earned"] is False
