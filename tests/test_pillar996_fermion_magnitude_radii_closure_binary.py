# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 996 — Fermion magnitude/radii closure binary decision."""

from __future__ import annotations

from src.core.pillar996_fermion_magnitude_radii_closure_binary import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    fermion_magnitude_radii_closure_binary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 996
    assert PILLAR_STATUS == "FERMION_MAGNITUDE_RADII_CLOSURE_BINARY_COMPLETE"
    assert PILLAR_VALID is True


def test_binary_status_only() -> None:
    status = fermion_magnitude_radii_closure_binary()["runtime_status"]
    assert status in {
        "FERMION_MAGNITUDE_RADII_CLOSED_FROM_PARENT_13D",
        "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
    }


def test_geometry_is_ordered() -> None:
    radii = fermion_magnitude_radii_closure_binary()["generation_radii"]
    assert radii[0] < radii[1] < radii[2]
