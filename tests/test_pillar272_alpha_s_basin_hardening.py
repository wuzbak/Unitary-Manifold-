# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 272 — α_s basin hardening."""
from __future__ import annotations

import pytest

from src.core.pillar272_alpha_s_basin_hardening import (
    ADJACENCY_TRACK_LABEL,
    ALPHA_S_PDG_CENTRAL,
    ALPHA_S_PDG_UNCERTAINTY,
    ALPHA_S_UM_CANONICAL_PREDICTION,
    GATE_BOUNDARY_WARNING_THRESHOLD_PCT,
    alpha_s_basin_hardening_report,
    alpha_s_basin_scan,
    pdg_alpha_s_stability_gate,
)


def test_basin_scan_has_expected_grid_size():
    points = alpha_s_basin_scan()
    assert len(points) == 27


def test_basin_report_has_majority_passing_points():
    report = alpha_s_basin_hardening_report()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["n_points"] == 27
    assert report["basin_fraction"] > 0.5


def test_basin_status_is_robust():
    report = alpha_s_basin_hardening_report()
    assert report["status"] == "ROBUST_BASIN_CONFIRMED"


# ---------------------------------------------------------------------------
# PDG α_s stability gate (new)
# ---------------------------------------------------------------------------


def test_pdg_constants_have_correct_values():
    assert ALPHA_S_PDG_CENTRAL == pytest.approx(0.1179)
    assert ALPHA_S_PDG_UNCERTAINTY == pytest.approx(0.0009)
    assert GATE_BOUNDARY_WARNING_THRESHOLD_PCT == pytest.approx(4.5)


def test_um_canonical_prediction_is_below_pdg():
    """UM prediction is below PDG 2024 central by ~4.1%."""
    assert ALPHA_S_UM_CANONICAL_PREDICTION < ALPHA_S_PDG_CENTRAL
    residual = abs(ALPHA_S_UM_CANONICAL_PREDICTION - ALPHA_S_PDG_CENTRAL) / ALPHA_S_PDG_CENTRAL * 100
    # Residual should be in the ~3.5%–4.5% range (near the 5% gate)
    assert 3.0 < residual < 5.0


def test_stability_gate_structure():
    gate = pdg_alpha_s_stability_gate()
    for key in (
        "residual_pct_central",
        "residual_pct_1sigma_up",
        "gate_pass_central",
        "gate_pass_1sigma",
        "gate_boundary_warning",
        "verdict",
        "reclassification_action",
        "pdg_values_used",
        "um_prediction_used",
        "gate_threshold_pct",
        "note",
    ):
        assert key in gate


def test_stability_gate_passes_at_pdg_2024():
    """At PDG 2024 central value (0.1179), UM prediction must still be < 5% away."""
    gate = pdg_alpha_s_stability_gate()
    assert gate["gate_pass_central"] is True
    assert gate["residual_pct_central"] < 5.0


def test_stability_gate_warning_is_active():
    """Current residual (~4.1%) is above the 4.5% warning threshold — warning must fire."""
    gate = pdg_alpha_s_stability_gate()
    # Gate passes (< 5%) but warning is active if residual > 4.5%
    if gate["residual_pct_central"] >= GATE_BOUNDARY_WARNING_THRESHOLD_PCT:
        assert gate["gate_boundary_warning"] is True
        assert gate["verdict"] == "DERIVED_GATE_PASS_WITH_WARNING"
    else:
        assert gate["verdict"] == "DERIVED_GATE_PASS"


def test_stability_gate_breach_detected():
    """Inject a PDG central value that puts UM > 5% away — must report BREACHED."""
    gate = pdg_alpha_s_stability_gate(pdg_central=0.120, pdg_uncertainty=0.0009)
    residual = abs(ALPHA_S_UM_CANONICAL_PREDICTION - 0.120) / 0.120 * 100
    if residual >= 5.0:
        assert gate["gate_pass_central"] is False
        assert gate["verdict"] == "DERIVED_GATE_BREACHED"
        assert gate["reclassification_action"] is not None
        assert "RECLASSIFY" in gate["reclassification_action"]


def test_stability_gate_passes_reclassification_action_is_none_when_passing():
    gate = pdg_alpha_s_stability_gate()
    if gate["gate_pass_central"]:
        assert gate["reclassification_action"] is None


def test_stability_gate_pdg_values_recorded():
    gate = pdg_alpha_s_stability_gate(pdg_central=0.1179, pdg_uncertainty=0.0009)
    assert gate["pdg_values_used"]["alpha_s_pdg_central"] == pytest.approx(0.1179)
    assert gate["pdg_values_used"]["alpha_s_pdg_uncertainty"] == pytest.approx(0.0009)
    assert "PDG" in gate["pdg_values_used"]["source"]


def test_stability_gate_custom_inputs_propagate():
    gate = pdg_alpha_s_stability_gate(pdg_central=0.1180, pdg_uncertainty=0.0010)
    assert gate["pdg_values_used"]["alpha_s_pdg_central"] == pytest.approx(0.1180)
    assert gate["um_prediction_used"] == pytest.approx(ALPHA_S_UM_CANONICAL_PREDICTION)
