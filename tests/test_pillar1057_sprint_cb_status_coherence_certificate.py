# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1057_sprint_cb_status_coherence_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    REQUIRED_SPRINT_MARKERS,
    STATUS_SURFACES,
    pillar1057_summary,
    sprint_cb_status_coherence_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1057
    assert PILLAR_GATE == "SPRINT_CB_STATUS_COHERENCE_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_CB_STATUS_COHERENCE_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is False or PILLAR_VALID is True


def test_surface_registry() -> None:
    assert len(STATUS_SURFACES) == 8
    assert REQUIRED_SPRINT_MARKERS == ["v35.8", "1051-1057", "1058"]


def test_certificate_shape() -> None:
    report = sprint_cb_status_coherence_certificate()
    assert report["surface_audit"]["all_exist"] is True
    assert "tests_ok" in report["live_status_audit"]
    assert "pillar1056" in report["dependency_chain"]


def test_summary() -> None:
    summary = pillar1057_summary()
    assert summary["status"] == PILLAR_STATUS
