# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1040_sprint_by_precision_lock import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REQUIRED_OPEN_LABELS,
    STATUS_SURFACES,
    pillar1040_summary,
    sprint_by_precision_lock,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1040
    assert PILLAR_GATE == "SPRINT_BY_PRECISION_LOCK"
    assert PILLAR_STATUS == "SPRINT_BY_PRECISION_LOCK_COMPLETE"


def test_surface_registry() -> None:
    assert len(STATUS_SURFACES) == 8
    assert "CMB_AMP_CONFIRMED_IRREDUCIBLE" in REQUIRED_OPEN_LABELS


def test_report_passes() -> None:
    report = sprint_by_precision_lock()
    assert report["stale_checks"]["fallibility_stale_v35_3_removed"] is True
    assert report["workflow_checks"]["merlin_gate_has_schedule"] is True
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1040_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
