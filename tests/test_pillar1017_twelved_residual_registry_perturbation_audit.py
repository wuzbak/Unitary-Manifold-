# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1017 — 12D residual registry + perturbation audit."""

from src.core.pillar1017_twelved_residual_registry_perturbation_audit import (
    OFF_REFERENCE_CHI_VALUES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    off_reference_perturbation_audit,
    pillar1017_summary,
    residual_registry_audit,
    twelved_lane_report,
)


def test_identity_constants():
    assert PILLAR_NUMBER == 1017
    assert PILLAR_GATE == "TWELVED_RESIDUAL_REGISTRY_PERTURBATION_AUDIT"
    assert PILLAR_STATUS == "TWELVED_RESIDUAL_REGISTRY_PERTURBATION_AUDIT_COMPLETE"


def test_registry_rows_are_registered():
    reg = residual_registry_audit()
    assert reg["all_registered"] is True
    assert reg["open_residual_count"] >= 1


def test_off_reference_rows_match_inputs():
    pert = off_reference_perturbation_audit()
    assert len(pert["rows"]) == len(OFF_REFERENCE_CHI_VALUES)
    assert pert["all_rows_pass"] is True


def test_lane_report_keeps_dual_truth():
    report = twelved_lane_report()
    assert report["valid"] is True
    assert report["reference_complete"] is True
    assert report["global_open"] is True


def test_summary_has_outcome():
    s = pillar1017_summary()
    assert s["status"] == PILLAR_STATUS
    assert "binary_outcome" in s
