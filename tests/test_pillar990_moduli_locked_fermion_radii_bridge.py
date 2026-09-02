# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 990 — Moduli-locked fermion radii bridge."""

from __future__ import annotations

from src.core.pillar990_moduli_locked_fermion_radii_bridge import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    moduli_locked_fermion_radii_bridge,
    pillar990_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 990
    assert PILLAR_STATUS == "MODULI_LOCKED_FERMION_RADII_BRIDGE_COMPLETE"
    assert PILLAR_VALID is True


def test_runtime_status_is_honest() -> None:
    report = moduli_locked_fermion_radii_bridge()
    assert report["runtime_status"] in {
        "MODULI_LOCKED_FERMION_RADII_CONSISTENT",
        "MODULI_LOCKED_FERMION_RADII_TENSION",
        "MODULI_LOCKED_FERMION_RADII_ARCHITECTURE_LIMIT",
    }


def test_geometric_radii_are_ordered() -> None:
    radii = moduli_locked_fermion_radii_bridge()["generation_radii"]
    assert radii[0] < radii[1] < radii[2]


def test_normalized_gap_bounded() -> None:
    gap = moduli_locked_fermion_radii_bridge()["normalized_gap"]
    assert 0.0 <= gap < 1.0
    assert pillar990_summary()["normalized_gap"] == gap
