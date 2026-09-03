# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1013 — 10D status-coherence certificate."""

from src.core.pillar1013_tend_status_coherence_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REQUIRED_OPEN_LABELS,
    REQUIRED_SPRINT_MARKERS,
    STATUS_SURFACES,
    status_coherence_certificate,
)


def test_identity_constants():
    assert PILLAR_NUMBER == 1013
    assert PILLAR_GATE == "TEN_D_STATUS_COHERENCE_CERTIFICATE"
    assert PILLAR_STATUS == "TEN_D_STATUS_COHERENCE_CERTIFICATE_COMPLETE"


def test_surface_registry_complete():
    expected = {
        "status",
        "fallibility",
        "mas_tracker",
        "claim_master_board",
        "gatekeeper_summary",
        "truth_layer",
        "wave_changelog",
        "sprint_plan",
    }
    assert set(STATUS_SURFACES.keys()) == expected
    assert "v34.8" in REQUIRED_SPRINT_MARKERS
    assert "1011-1013" in REQUIRED_SPRINT_MARKERS
    assert "ALPHA_S_TYPE_B_FLOOR" in REQUIRED_OPEN_LABELS


def test_status_coherence_certificate_passes():
    report = status_coherence_certificate()
    assert report["surface_audit"]["all_exist"] is True
    assert report["surface_audit"]["open_labels_pass"] is True
    assert report["surface_audit"]["sprint_markers_pass"] is True
    assert report["dependency_chain"]["pillar1011"]["valid"] is True
    assert report["dependency_chain"]["pillar1012"]["valid"] is True
    assert report["valid"] is True
