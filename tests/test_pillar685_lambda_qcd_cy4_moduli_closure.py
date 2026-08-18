# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 685 — ΛQCD CY4 moduli closure."""
import pytest
from src.core.pillar685_lambda_qcd_cy4_moduli_closure import (
    K_CS, N_W, LAMBDA_QCD_PDG_GEV, LAMBDA_QCD_SCAFFOLD_GEV,
    scaffold_lambda_qcd_estimate,
    cy4_moduli_inputs_missing,
    moduli_sensitivity_band,
    closure_roadmap,
    lambda_qcd_cy4_moduli_certificate,
)


# ── Constants ─────────────────────────────────────────────────────────────────

def test_k_cs():
    assert K_CS == 74

def test_n_w():
    assert N_W == 5

def test_pdg_value():
    assert abs(LAMBDA_QCD_PDG_GEV - 0.332) < 1e-6


# ── Scaffold estimate ─────────────────────────────────────────────────────────

def test_scaffold_returns_dict():
    result = scaffold_lambda_qcd_estimate()
    assert isinstance(result, dict)

def test_scaffold_lambda_qcd_positive():
    result = scaffold_lambda_qcd_estimate()
    assert result["lambda_qcd_mev"] > 0

def test_scaffold_lambda_qcd_reasonable():
    result = scaffold_lambda_qcd_estimate()
    # Should be in 100–1000 MeV range
    assert 100 < result["lambda_qcd_mev"] < 1000

def test_scaffold_residual_under_100pct():
    # Scaffold gives ~57% residual vs PDG (known from Pillar 153)
    result = scaffold_lambda_qcd_estimate()
    assert result["residual_percent"] < 100.0

def test_scaffold_alpha_s_mz_reasonable():
    result = scaffold_lambda_qcd_estimate()
    # PDG: α_s(M_Z) ≈ 0.118; scaffold uses this established value
    assert 0.05 < result["alpha_s_mz"] < 0.50

def test_scaffold_status():
    result = scaffold_lambda_qcd_estimate()
    assert result["status"] == "SCAFFOLD_ESTIMATE"


# ── Missing CY4 inputs ────────────────────────────────────────────────────────

def test_missing_inputs_count():
    result = cy4_moduli_inputs_missing()
    assert len(result["missing_inputs"]) >= 4

def test_missing_inputs_have_required_fields():
    result = cy4_moduli_inputs_missing()
    for item in result["missing_inputs"]:
        assert "input" in item
        assert "role" in item
        assert "status" in item

def test_missing_inputs_all_not_available():
    result = cy4_moduli_inputs_missing()
    for item in result["missing_inputs"]:
        assert "NOT_AVAILABLE" in item["status"]

def test_available_at_scaffold_non_empty():
    result = cy4_moduli_inputs_missing()
    assert len(result["available_at_scaffold"]) >= 3

def test_gap_characterization_present():
    result = cy4_moduli_inputs_missing()
    assert "gap_characterization" in result
    assert len(result["gap_characterization"]) > 50


# ── Moduli sensitivity band ───────────────────────────────────────────────────

def test_band_has_three_results():
    result = moduli_sensitivity_band()
    assert len(result["results"]) == 3

def test_band_labels():
    result = moduli_sensitivity_band()
    labels = [r["label"] for r in result["results"]]
    assert set(labels) == {"lower", "central", "upper"}

def test_band_upper_greater_than_lower():
    result = moduli_sensitivity_band()
    assert result["lambda_qcd_upper_mev"] > result["lambda_qcd_lower_mev"]

def test_band_central_in_middle():
    result = moduli_sensitivity_band()
    assert result["lambda_qcd_lower_mev"] <= result["lambda_qcd_central_mev"] <= result["lambda_qcd_upper_mev"]

def test_band_positive_width():
    result = moduli_sensitivity_band()
    assert result["lambda_qcd_band_mev"] > 0

def test_pdg_in_band():
    result = moduli_sensitivity_band(delta_pct=20.0)
    pdg_mev = LAMBDA_QCD_PDG_GEV * 1000.0
    assert result["lambda_qcd_lower_mev"] <= pdg_mev <= result["lambda_qcd_upper_mev"]


# ── Closure roadmap ───────────────────────────────────────────────────────────

def test_roadmap_has_4_steps():
    result = closure_roadmap()
    assert len(result["steps"]) == 4

def test_roadmap_steps_numbered():
    result = closure_roadmap()
    for i, step in enumerate(result["steps"], 1):
        assert step["step"] == i

def test_roadmap_blocking_step_is_1():
    result = closure_roadmap()
    assert "STEP_1" in result["blocking_step"]

def test_roadmap_current_status():
    result = closure_roadmap()
    assert "STEP_0" in result["current_status"]

def test_roadmap_steps_have_titles():
    result = closure_roadmap()
    for step in result["steps"]:
        assert "title" in step
        assert len(step["title"]) > 5


# ── Full certificate ──────────────────────────────────────────────────────────

def test_certificate_status():
    cert = lambda_qcd_cy4_moduli_certificate()
    assert cert["status"] == "ARCHITECTURE_LIMIT"

def test_certificate_pillar():
    cert = lambda_qcd_cy4_moduli_certificate()
    assert cert["pillar"] == "685"

def test_certificate_toe_zero():
    cert = lambda_qcd_cy4_moduli_certificate()
    assert cert["toe_impact"] == 0

def test_certificate_not_a_failure():
    cert = lambda_qcd_cy4_moduli_certificate()
    assert cert["architecture_limit_is_not_a_failure"] is True

def test_certificate_honest_residuals():
    cert = lambda_qcd_cy4_moduli_certificate()
    assert len(cert["honest_residuals"]) >= 3

def test_certificate_roadmap_has_steps():
    cert = lambda_qcd_cy4_moduli_certificate()
    assert len(cert["closure_roadmap"]["steps"]) == 4
