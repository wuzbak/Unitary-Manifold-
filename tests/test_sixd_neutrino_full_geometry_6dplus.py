# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/neutrino_full_geometry_6dplus.py."""
from __future__ import annotations

import pytest

from src.sixd.neutrino_full_geometry_6dplus import (
    DM2_21_PDG,
    DM2_31_PDG,
    exact_overlap_profile,
    simultaneous_splittings_from_geometry,
    ws_iii_full_geometry_gate,
)


def test_exact_overlap_profile_monotonic_by_generation():
    p0 = exact_overlap_profile(0)
    p1 = exact_overlap_profile(1)
    p2 = exact_overlap_profile(2)
    assert p0 < p1 < p2


def test_exact_overlap_profile_invalid_index_raises():
    with pytest.raises(ValueError):
        exact_overlap_profile(3)


def test_simultaneous_splittings_positive():
    pred = simultaneous_splittings_from_geometry()
    assert pred["dm2_21_eV2"] > 0.0
    assert pred["dm2_31_eV2"] > 0.0
    assert len(pred["masses_ev"]) == 3


def test_simultaneous_splittings_close_to_pdg_bands():
    pred = simultaneous_splittings_from_geometry()
    r21 = abs(pred["dm2_21_eV2"] - DM2_21_PDG) / DM2_21_PDG * 100.0
    r31 = abs(pred["dm2_31_eV2"] - DM2_31_PDG) / DM2_31_PDG * 100.0
    assert r21 < 20.0
    assert r31 < 10.0


def test_ws_iii_gate_passes():
    gate = ws_iii_full_geometry_gate()
    assert gate["gate_pass"] is True
    assert gate["simultaneous_prediction"] is True
    assert gate["residuals_bounded"] is True
    assert "PASS_FREEZE" in gate["status"]

