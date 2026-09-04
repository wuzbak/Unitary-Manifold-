# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1047_sprint_by_status_coherence_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REQUIRED_OPEN_LABELS,
    REQUIRED_SPRINT_MARKERS,
    STATUS_SURFACES,
    pillar1047_summary,
    status_coherence_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1047
    assert PILLAR_GATE == "SPRINT_BY_STATUS_COHERENCE_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_BY_STATUS_COHERENCE_CERTIFICATE_COMPLETE"


def test_surface_registry() -> None:
    assert len(STATUS_SURFACES) == 8
    assert REQUIRED_SPRINT_MARKERS == ["v35.5", "1040-1047", "1048"]
    assert "ALPHA_S_TYPE_B_FLOOR" in REQUIRED_OPEN_LABELS


def test_certificate_passes() -> None:
    report = status_coherence_certificate()
    assert report["surface_audit"]["all_exist"] is True
    assert report["surface_audit"]["open_labels_pass"] is True
    assert report["surface_audit"]["sprint_markers_pass"] is True
    assert all(report["live_status_audit"].values()) is True
    assert report["dependency_chain"]["pillar1046"]["valid"] is True
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1047_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
