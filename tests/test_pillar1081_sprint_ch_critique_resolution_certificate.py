# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1081_sprint_ch_critique_resolution_certificate as p1081

from src.core.pillar1081_sprint_ch_critique_resolution_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1081_summary,
    sprint_ch_critique_resolution_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1081
    assert PILLAR_GATE == "SPRINT_CH_CRITIQUE_RESOLUTION_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_CH_CRITIQUE_RESOLUTION_CERTIFICATE_COMPLETE"
    assert isinstance(PILLAR_VALID, bool)


def test_publication_packet_exists() -> None:
    report = sprint_ch_critique_resolution_certificate()
    assert report["publication_packet"]["status"] == "PASS"
    assert report["sprint_success"] is True
    assert report["valid"] is True


def test_publication_packet_missing_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setitem(p1081.PUBLICATION_PACKET, "execution_report", tmp_path / "missing.md")
    report = sprint_ch_critique_resolution_certificate()
    assert report["publication_packet"]["status"] == "FAIL"
    assert report["sprint_success"] is False


def test_summary() -> None:
    summary = pillar1081_summary()
    assert summary["status"] == PILLAR_STATUS

