# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1083_sprint_ci_foundation_certificate as p1083

from src.core.pillar1083_sprint_ci_foundation_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PRIMARY_LANE,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1083_summary,
    sprint_ci_foundation_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1083
    assert PILLAR_GATE == "SPRINT_CI_FOUNDATION_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_CI_FOUNDATION_CERTIFICATE_COMPLETE"
    assert PRIMARY_LANE == "FOUNDATION_PHOTON_ACTION"
    assert isinstance(PILLAR_VALID, bool)


def test_publication_packet_exists() -> None:
    report = sprint_ci_foundation_certificate()
    assert report["publication_packet"]["status"] == "PASS"
    assert report["scientific_progress"] is True
    assert report["merlin_handoff_ok"] is True
    assert report["sprint_success"] is True
    assert report["valid"] is True


def test_missing_publication_packet_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setitem(p1083.PUBLICATION_PACKET, "execution_report", tmp_path / "missing.md")
    report = sprint_ci_foundation_certificate()
    assert report["publication_packet"]["status"] == "FAIL"
    assert report["sprint_success"] is False
    assert report["valid"] is False


def test_incomplete_merlin_handoff_fails_closed(monkeypatch) -> None:
    packet = p1083.foundation_first_photon_action_audit()
    packet["merlin_handoff"] = {
        **packet["merlin_handoff"],
        "primary_lane": "WRONG_LANE",
    }
    monkeypatch.setattr(p1083, "foundation_first_photon_action_audit", lambda: packet)
    report = sprint_ci_foundation_certificate()
    assert report["merlin_handoff_ok"] is False
    assert report["valid"] is False


def test_empty_evidence_reviewed_fails_closed(monkeypatch) -> None:
    packet = p1083.foundation_first_photon_action_audit()
    packet["merlin_handoff"] = {
        **packet["merlin_handoff"],
        "evidence_reviewed": [],
    }
    monkeypatch.setattr(p1083, "foundation_first_photon_action_audit", lambda: packet)
    report = sprint_ci_foundation_certificate()
    assert report["merlin_handoff_ok"] is False
    assert report["valid"] is False


def test_mismatched_blocker_state_after_fails_closed(monkeypatch) -> None:
    packet = p1083.foundation_first_photon_action_audit()
    packet["merlin_handoff"] = {
        **packet["merlin_handoff"],
        "blocker_state_after": ["wrong blocker"],
    }
    monkeypatch.setattr(p1083, "foundation_first_photon_action_audit", lambda: packet)
    report = sprint_ci_foundation_certificate()
    assert report["merlin_handoff_ok"] is False
    assert report["valid"] is False


def test_mismatched_blocker_state_before_fails_closed(monkeypatch) -> None:
    packet = p1083.foundation_first_photon_action_audit()
    packet["merlin_handoff"] = {
        **packet["merlin_handoff"],
        "blocker_state_before": ["wrong starting state"],
    }
    monkeypatch.setattr(p1083, "foundation_first_photon_action_audit", lambda: packet)
    report = sprint_ci_foundation_certificate()
    assert report["merlin_handoff_ok"] is False
    assert report["valid"] is False


def test_summary() -> None:
    summary = pillar1083_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["sprint_success"] is True
