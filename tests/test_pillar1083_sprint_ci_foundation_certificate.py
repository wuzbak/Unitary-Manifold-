# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1083_sprint_ci_foundation_certificate as p1083

from src.core.pillar1083_sprint_ci_foundation_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1083_summary,
    sprint_ci_foundation_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1083
    assert PILLAR_GATE == "SPRINT_CI_FOUNDATION_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_CI_FOUNDATION_CERTIFICATE_COMPLETE"
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


def test_summary() -> None:
    summary = pillar1083_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["sprint_success"] is True
