# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/higgs_radion_full_geometry_6dplus.py."""
from __future__ import annotations

import math

from src.sixd.higgs_radion_full_geometry_6dplus import (
    HIGGS_MASS_PDG_GEV,
    brane_localized_xi_6d,
    exact_theta_hr_6d,
    higgs_mass_from_mixing,
    ws_i_full_geometry_gate,
)


def test_xi_6d_positive_and_reasonable():
    xi = brane_localized_xi_6d()
    assert 0.1 < xi < 0.3


def test_theta_hr_perturbative():
    theta = exact_theta_hr_6d(brane_localized_xi_6d())
    assert 1e-4 < abs(theta) < math.pi / 4


def test_higgs_mass_prediction_close_to_pdg():
    theta = exact_theta_hr_6d(brane_localized_xi_6d())
    pred = higgs_mass_from_mixing(theta)
    residual = abs(pred - HIGGS_MASS_PDG_GEV) / HIGGS_MASS_PDG_GEV * 100.0
    assert residual < 5.0


def test_ws_i_gate_passes():
    gate = ws_i_full_geometry_gate()
    assert gate["gate_pass"] is True
    assert "PASS_FREEZE" in gate["status"]
    assert gate["mass_close"] is True
    assert gate["perturbative"] is True

