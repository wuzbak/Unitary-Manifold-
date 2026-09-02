# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 985 — Cross-Domain Calibration Harness."""

from __future__ import annotations

from src.core.pillar985_cross_domain_calibration_harness import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cross_domain_calibration_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 985
    assert PILLAR_STATUS == "CROSS_DOMAIN_CALIBRATION_HARNESS_COMPLETE"
    assert PILLAR_VALID is True


def test_shared_signature_across_lanes() -> None:
    report = cross_domain_calibration_report()
    assert report["all_lanes_share_same_parameters"] is True
    signatures = {lane["parameter_signature"] for lane in report["lanes"].values()}
    assert len(signatures) == 1


def test_alpha_s_lane_marks_outside_window() -> None:
    report = cross_domain_calibration_report()
    assert report["lanes"]["alpha_s"]["calibration_status"] in {"OUTSIDE_WINDOW", "INSIDE_WINDOW"}


def test_flavor_lanes_can_report_moduli_lock_tension() -> None:
    report = cross_domain_calibration_report()
    assert report["lanes"]["ckm_theta13"]["calibration_status"] in {
        "EFT_EXHAUSTED",
        "MODULI_RADII_MISMATCH",
        "REVIEW",
    }
    assert report["lanes"]["fermion_magnitudes"]["calibration_status"] in {
        "WINDOW_CONSTRAINED",
        "MODULI_LOCKED_TENSION",
        "TUNED",
    }
