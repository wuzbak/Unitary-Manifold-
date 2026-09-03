# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1024 — Sprint BU status coherence."""

from __future__ import annotations

from src.core.pillar1024_sprint_bu_status_coherence_certificate import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REQUIRED_OPEN_LABELS,
    REQUIRED_SPRINT_MARKERS,
    STATUS_SURFACES,
    pillar1024_summary,
    status_coherence_certificate,
    status_surface_audit,
)


AUDIT = status_surface_audit()
REPORT = status_coherence_certificate()
SUMMARY = pillar1024_summary()


def test_constants():
    assert PILLAR_NUMBER == 1024
    assert PILLAR_STATUS == "SPRINT_BU_STATUS_COHERENCE_CERTIFICATE_COMPLETE"


def test_expected_surface_set_present():
    assert len(STATUS_SURFACES) == 8
    assert REQUIRED_OPEN_LABELS == [
        "CMB_AMP_CONFIRMED_IRREDUCIBLE",
        "ALPHA_S_TYPE_B_FLOOR",
        "LITEBIRD_BIREFRINGENCE",
    ]
    assert REQUIRED_SPRINT_MARKERS == ["v35.1", "1021-1024", "1025"]


def test_audit_passes():
    assert AUDIT["all_exist"] is True
    assert AUDIT["open_labels_pass"] is True
    assert AUDIT["sprint_markers_pass"] is True


def test_certificate_depends_on_sprint_certificate():
    assert REPORT["dependency_chain"]["pillar1023"]["valid"] is True
    assert REPORT["valid"] is True


def test_summary_matches_report():
    assert SUMMARY["open_labels_pass"] is True
    assert SUMMARY["sprint_markers_pass"] is True
