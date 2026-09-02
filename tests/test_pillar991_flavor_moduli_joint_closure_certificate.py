# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 991 — Flavor-moduli joint closure certificate."""

from __future__ import annotations

from src.core.pillar991_flavor_moduli_joint_closure_certificate import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    flavor_moduli_joint_closure_certificate,
    pillar991_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 991
    assert PILLAR_STATUS == "FLAVOR_MODULI_JOINT_CLOSURE_CERTIFICATE_COMPLETE"
    assert PILLAR_VALID is True


def test_attribution_is_normalized() -> None:
    attribution = flavor_moduli_joint_closure_certificate()["attribution"]
    assert abs(sum(attribution.values()) - 1.0) < 1e-9


def test_budget_rows_present() -> None:
    report = flavor_moduli_joint_closure_certificate()
    assert report["ckm_theta13_row"]["lane"] == "CKM_THETA13"
    assert report["fermion_magnitudes_row"]["lane"] == "FERMION_MASS_MAGNITUDES"


def test_summary_tracks_recommendation() -> None:
    report = flavor_moduli_joint_closure_certificate()
    summary = pillar991_summary()
    assert summary["recommended_next_target"] == report["recommended_next_target"]
