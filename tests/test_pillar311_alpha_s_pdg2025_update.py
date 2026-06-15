# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 311 PDG 2025 Update — α_s Basin Refresh."""
import pytest
from src.core.pillar311_alpha_s_pdg2025_update import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    ALPHA_S_PDG_2025_CENTRAL,
    ALPHA_S_PDG_2025_UNCERTAINTY,
    ALPHA_S_PDG_2024_CENTRAL,
    pdg_2025_basin_update,
    pdg_2025_stability_gate,
    p3_label_after_pdg_2025,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 311


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_pdg_2025_central():
    assert abs(ALPHA_S_PDG_2025_CENTRAL - 0.1180) < 1e-6


def test_pdg_2025_uncertainty():
    assert abs(ALPHA_S_PDG_2025_UNCERTAINTY - 0.0009) < 1e-7


def test_pdg_2024_central():
    assert abs(ALPHA_S_PDG_2024_CENTRAL - 0.1179) < 1e-6


def test_pdg_shift_is_small():
    shift = abs(ALPHA_S_PDG_2025_CENTRAL - ALPHA_S_PDG_2024_CENTRAL)
    assert shift < 0.001   # shift is only 0.0001


# ── PDG 2025 basin update ─────────────────────────────────────────────────────

def test_basin_update_returns_dict():
    result = pdg_2025_basin_update()
    assert isinstance(result, dict)


def test_basin_update_version():
    result = pdg_2025_basin_update()
    assert result["update_version"] == "v11.15"


def test_basin_update_n_total():
    result = pdg_2025_basin_update()
    assert result["n_total"] == 27   # 3×3×3 grid


def test_basin_update_counts_sum_to_total():
    result = pdg_2025_basin_update()
    assert (
        result["n_stable_core"] + result["n_margin_zone"] + result["n_volatile_outer"]
        == result["n_total"]
    )


def test_basin_update_canonical_residual_positive():
    result = pdg_2025_basin_update()
    assert result["canonical_residual_pdg2025_pct"] > 0.0


def test_basin_update_canonical_residual_below_5_pct():
    result = pdg_2025_basin_update()
    # Gate threshold is 5%; if PDG 2025 ~ PDG 2024, should remain < 5%
    assert result["canonical_residual_pdg2025_pct"] < 5.0


def test_basin_update_gate_pass():
    result = pdg_2025_basin_update()
    assert result["gate_pass"] is True


def test_basin_update_p3_label_derived():
    result = pdg_2025_basin_update()
    assert result["p3_label"] == "DERIVED"


def test_basin_update_p3_label_not_changed():
    result = pdg_2025_basin_update()
    assert result["p3_label_changed"] is False


def test_basin_update_has_volatility_map():
    result = pdg_2025_basin_update()
    assert isinstance(result["volatility_map"], list)
    assert len(result["volatility_map"]) == 27


def test_basin_update_residual_shift_from_2024_to_2025():
    result = pdg_2025_basin_update()
    # Shift should be small (PDG 2025 shifted by +0.0001)
    assert abs(result["residual_shift_pct"]) < 1.0


# ── PDG 2025 stability gate ───────────────────────────────────────────────────

def test_stability_gate_returns_dict():
    result = pdg_2025_stability_gate()
    assert isinstance(result, dict)


def test_stability_gate_pass():
    result = pdg_2025_stability_gate()
    assert result["gate_pass_central"] is True


def test_stability_gate_verdict_derived():
    result = pdg_2025_stability_gate()
    assert "GATE_PASS" in result["verdict"]


def test_stability_gate_residual_positive():
    result = pdg_2025_stability_gate()
    assert result["residual_pct_central"] > 0.0


# ── P3 label after PDG 2025 ───────────────────────────────────────────────────

def test_p3_label_returns_dict():
    result = p3_label_after_pdg_2025()
    assert isinstance(result, dict)


def test_p3_prior_label_derived():
    result = p3_label_after_pdg_2025()
    assert result["p3_prior_label"] == "DERIVED"


def test_p3_new_label_derived():
    result = p3_label_after_pdg_2025()
    assert result["p3_new_label"] == "DERIVED"


def test_p3_label_not_changed():
    result = p3_label_after_pdg_2025()
    assert result["label_changed"] is False


def test_p3_action_no_reclassification():
    result = p3_label_after_pdg_2025()
    assert "No action" in result["action"] or "PASS" in result["gate_verdict"]


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    assert "SEPARATION_INTACT" in separation_guard()
