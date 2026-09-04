# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1050_sprint_ca_status_coherence_certificate import (
    EXPECTED_LEAN4_COUNT,
    EXPECTED_NEXT_SLOT,
    EXPECTED_TESTS_PASSED,
    EXPECTED_TOTAL_SLOTS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    REQUIRED_SPRINT_MARKERS,
    STATUS_SURFACES,
    pillar1050_summary,
    status_coherence_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1050
    assert PILLAR_GATE == "SPRINT_CA_STATUS_COHERENCE_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_CA_STATUS_COHERENCE_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_surface_registry() -> None:
    assert len(STATUS_SURFACES) == 8
    assert REQUIRED_SPRINT_MARKERS == ["v35.7", "1049-1050", "1051"]


def test_expected_thresholds() -> None:
    assert EXPECTED_TESTS_PASSED == 63732
    assert EXPECTED_LEAN4_COUNT == 3988
    assert EXPECTED_TOTAL_SLOTS == 1050
    assert EXPECTED_NEXT_SLOT == 1051


def test_certificate_passes() -> None:
    report = status_coherence_certificate()
    assert report["surface_audit"]["all_exist"] is True
    assert report["surface_audit"]["open_labels_pass"] is True
    assert report["surface_audit"]["sprint_markers_pass"] is True
    assert all(report["live_status_audit"].values()) is True
    assert report["article_audit"]["all_valid"] is True
    assert report["dependency_chain"]["pillar1049"]["valid"] is True
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1050_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
