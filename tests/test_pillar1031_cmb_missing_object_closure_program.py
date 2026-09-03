# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1031 — CMB missing-object closure program."""

from src.core.pillar1031_cmb_missing_object_closure_program import (
    CANDIDATE_OBJECT_NAME,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cmb_missing_object_closure_program,
    pillar1031_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1031
    assert PILLAR_GATE == "CMB_MISSING_OBJECT_CLOSURE_PROGRAM"
    assert PILLAR_STATUS == "CMB_MISSING_OBJECT_CLOSURE_PROGRAM_COMPLETE"
    assert PILLAR_VALID is True


def test_candidate_targets_both_missing_objects() -> None:
    report = cmb_missing_object_closure_program()
    assert report["candidate"]["name"] == CANDIDATE_OBJECT_NAME
    assert report["candidate"]["uses_external_as_target"] is False
    assert report["candidate"]["free_parameters_added"] == 0
    assert report["both_targets_satisfied"] is True


def test_binary_nonpromotion_when_deficit_not_collapsed() -> None:
    report = cmb_missing_object_closure_program()
    assert report["deficit_collapsed"] is False
    assert report["closure_earned"] is False
    assert report["outcome"] == "CMB_MISSING_OBJECT_NONPROMOTION_STRENGTHENED"
    assert report["tightened_certificate"] is True


def test_summary() -> None:
    summary = pillar1031_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True

