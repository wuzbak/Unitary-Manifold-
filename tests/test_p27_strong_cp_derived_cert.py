# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P27 DERIVED certification (strong CP angle θ̄)."""
import math

from src.core.p27_strong_cp_derived_cert import (
    THETA_BAR_GEO,
    THETA_BAR_PDG_BOUND,
    p27_derived_gate_report,
    p27_derived_summary,
)
from src.core.delta_cp_hardgate_cert import P15_DELTA_CP_9D_RAD
from src.sixd.solar_splitting_6dplus import N_W, PI_KR


def test_theta_bar_positive_and_tiny():
    assert THETA_BAR_GEO > 0.0
    assert THETA_BAR_GEO < THETA_BAR_PDG_BOUND


def test_closed_form_identity():
    expected = abs(math.sin(P15_DELTA_CP_9D_RAD)) * math.exp(-PI_KR) / float(N_W)
    assert abs(THETA_BAR_GEO - expected) < 1e-30


def test_all_gates_pass():
    assert p27_derived_gate_report()["all_gates_pass"] is True


def test_status_after_derived():
    assert p27_derived_gate_report()["status_after"] == "DERIVED"


def test_toe_delta():
    assert p27_derived_gate_report()["toe_score_delta"] == 0.2


def test_axiomzero_empty():
    assert p27_derived_gate_report()["axiomzero_pdg_inputs"] == []


def test_summary_p27():
    s = p27_derived_summary()
    assert s["parameter"] == "P27"
    assert s["all_gates_pass"] is True
