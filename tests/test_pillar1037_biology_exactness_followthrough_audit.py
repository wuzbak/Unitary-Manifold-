# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1037 — biology exactness follow-through audit."""

from src.core.pillar1037_biology_exactness_followthrough_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    biology_exactness_followthrough_audit,
    pillar1037_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1037
    assert PILLAR_GATE == "BIOLOGY_EXACTNESS_FOLLOWTHROUGH_AUDIT"
    assert PILLAR_STATUS == "BIOLOGY_EXACTNESS_FOLLOWTHROUGH_AUDIT_COMPLETE"
    assert PILLAR_VALID is True


def test_hox_lane_stays_empirical_and_adjacent() -> None:
    report = biology_exactness_followthrough_audit()
    assert "ADJACENT TRACK" in report["hox_empirical_lane"]["pillar_classification"]
    assert len(report["hox_empirical_lane"]["promotion_condition"]) > 20


def test_hydration_window_keeps_model_dependence_explicit() -> None:
    report = biology_exactness_followthrough_audit()
    assert report["hydration_model_dependence"]["status"] == "FALSIFIABLE_PREDICTION"
    assert report["hydration_model_dependence"]["volume_fraction_spread"] > 0.0
    assert report["hydration_model_dependence"]["mass_ratio_spread"] > 0.0


def test_summary() -> None:
    summary = pillar1037_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
