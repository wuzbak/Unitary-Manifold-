# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 270 — orbifold / Kawamura equivalence."""
from __future__ import annotations

from src.core.pillar270_orbifold_kawamura_equivalence import (
    ADJACENCY_TRACK_LABEL,
    orbifold_equivalence_report,
    orbifold_parity_equivalence,
    orbifold_spectrum_equivalence,
)


def test_parity_equivalence_passes():
    parity = orbifold_parity_equivalence()
    assert parity["equivalent"] is True


def test_spectrum_equivalence_passes():
    spectrum = orbifold_spectrum_equivalence()
    assert spectrum["equivalent"] is True


def test_report_closes_executable_equivalence():
    report = orbifold_equivalence_report()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["equivalence_closed"] is True
    assert report["status"] == "ORBIFOLD_EQUIVALENCE_EXECUTABLE_CLOSED"
