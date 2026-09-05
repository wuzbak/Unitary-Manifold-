# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1055_sprint_cb_verification_release_discipline import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    TARGETED_SUITES,
    sprint_cb_verification_release_discipline,
    pillar1055_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1055
    assert PILLAR_GATE == "SPRINT_CB_VERIFICATION_RELEASE_DISCIPLINE"
    assert PILLAR_STATUS == "SPRINT_CB_VERIFICATION_RELEASE_DISCIPLINE_COMPLETE"
    assert PILLAR_VALID is True


def test_verification_contract() -> None:
    report = sprint_cb_verification_release_discipline()
    assert len(TARGETED_SUITES) >= 5
    assert report["workflow_checks"]["schedule_present"] is True
    assert report["workflow_checks"]["upload_artifact_present"] is True
    assert report["status_gate"]["zero_failures_in_header"] is True
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1055_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
