# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 887 — FN charge assignment."""
from __future__ import annotations

import numpy as np
import pytest

from src.sevend.pillar887_fn_charge_assignment import (
    FIXED_POINTS_T2Z2,
    FN_CHARGES_DOWN,
    FN_CHARGES_LEPTON,
    FN_CHARGES_NEUTRINO,
    FN_CHARGES_UP,
    FN_EPSILON,
    PILLAR_GATE,
    PILLAR_NUMBER,
    STATUS_LABEL,
    charge_differences,
    fn_charge_summary,
    fn_suppression_matrix,
)

ALLOWED = {"RESOLVED", "TENSION_PERSISTS", "PARTIAL", "ARCHITECTURE_LIMIT", "IRREDUCIBLE_ARCHITECTURE_LIMIT"}


def test_pillar_number(): assert PILLAR_NUMBER == 887

def test_gate_string(): assert PILLAR_GATE == "FN_CHARGE_ASSIGNMENT_FROM_7D_MONODROMY"

def test_status_label_allowed(): assert STATUS_LABEL in ALLOWED

def test_fixed_points_count(): assert len(FIXED_POINTS_T2Z2) == 4

def test_fixed_points_unique(): assert len(set(FIXED_POINTS_T2Z2)) == 4

def test_fn_epsilon_value(): assert FN_EPSILON == pytest.approx(0.2253)

def test_fn_epsilon_unit_interval(): assert 0.0 < FN_EPSILON < 1.0

@pytest.mark.parametrize("charges", [FN_CHARGES_UP, FN_CHARGES_DOWN, FN_CHARGES_LEPTON, FN_CHARGES_NEUTRINO])
def test_charges_length(charges): assert len(charges) == 3

@pytest.mark.parametrize("charges", [FN_CHARGES_UP, FN_CHARGES_DOWN, FN_CHARGES_LEPTON, FN_CHARGES_NEUTRINO])
def test_charges_strictly_ordered(charges): assert charges[0] > charges[1] > charges[2] >= 0

@pytest.mark.parametrize(
    ("charges", "expected"),
    [
        (FN_CHARGES_UP, {"dq12": 2, "dq13": 4, "dq23": 2}),
        (FN_CHARGES_DOWN, {"dq12": 1, "dq13": 2, "dq23": 1}),
        (FN_CHARGES_LEPTON, {"dq12": 1, "dq13": 2, "dq23": 1}),
        (FN_CHARGES_NEUTRINO, {"dq12": 1, "dq13": 2, "dq23": 1}),
    ],
)
def test_charge_differences(charges, expected): assert charge_differences(charges) == expected

@pytest.mark.parametrize("charges", [FN_CHARGES_UP, FN_CHARGES_DOWN, FN_CHARGES_LEPTON, FN_CHARGES_NEUTRINO])
def test_suppression_matrix_shape(charges): assert fn_suppression_matrix(charges).shape == (3, 3)

@pytest.mark.parametrize("charges", [FN_CHARGES_UP, FN_CHARGES_DOWN, FN_CHARGES_LEPTON, FN_CHARGES_NEUTRINO])
def test_suppression_matrix_symmetric(charges): assert np.allclose(fn_suppression_matrix(charges), fn_suppression_matrix(charges).T)

@pytest.mark.parametrize("charges", [FN_CHARGES_UP, FN_CHARGES_DOWN, FN_CHARGES_LEPTON, FN_CHARGES_NEUTRINO])
def test_suppression_matrix_unit_diagonal(charges): assert np.allclose(np.diag(fn_suppression_matrix(charges)), np.ones(3))

@pytest.mark.parametrize("charges", [FN_CHARGES_UP, FN_CHARGES_DOWN, FN_CHARGES_LEPTON, FN_CHARGES_NEUTRINO])
def test_suppression_entries_bounded(charges): assert np.all((fn_suppression_matrix(charges) > 0.0) & (fn_suppression_matrix(charges) <= 1.0))

@pytest.mark.parametrize("charges", [FN_CHARGES_UP, FN_CHARGES_DOWN, FN_CHARGES_LEPTON, FN_CHARGES_NEUTRINO])
def test_suppression_monotone_offdiag(charges):
    matrix = fn_suppression_matrix(charges)
    assert matrix[0, 2] <= matrix[0, 1] <= 1.0


def test_summary_gate(): assert fn_charge_summary()["gate"] == PILLAR_GATE

def test_summary_pillar(): assert fn_charge_summary()["pillar"] == 887

def test_summary_status(): assert fn_charge_summary()["status_label"] == STATUS_LABEL

def test_summary_charges_keys(): assert set(fn_charge_summary()["charges"]) == {"up", "down", "lepton", "neutrino"}

def test_summary_matrices_keys(): assert set(fn_charge_summary()["suppression_matrices"]) == {"up", "down", "lepton", "neutrino"}

def test_summary_fixed_points(): assert fn_charge_summary()["fixed_points_t2z2"] == list(FIXED_POINTS_T2Z2)

def test_no_toe_language(): assert "TOE" not in fn_charge_summary()["epistemic_status"].upper()
