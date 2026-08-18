# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 683 — t₂ gauge artifact certificate."""
import pytest
from src.core.pillar683_t2_gauge_artifact_certificate import (
    N_DOF_5D_METRIC,
    N_DOF_PHYSICAL,
    kk_dof_decomposition,
    t2_gauge_elimination,
    u1_gauge_transformation,
    dof_count_certificate,
    t2_gauge_artifact_certificate,
)


# ── Constants ─────────────────────────────────────────────────────────────────

def test_5d_metric_components():
    assert N_DOF_5D_METRIC == 15

def test_physical_dof_count():
    assert N_DOF_PHYSICAL == 5


# ── KK DoF decomposition ──────────────────────────────────────────────────────

def test_decomposition_total_physical():
    result = kk_dof_decomposition()
    assert result["total_physical_dof"] == 5

def test_decomposition_t2_zero_dof():
    result = kk_dof_decomposition()
    assert result["t2_phase"]["physical_dof"] == 0

def test_decomposition_t2_is_gauge():
    result = kk_dof_decomposition()
    assert result["t2_phase"]["status"] == "GAUGE_ARTIFACT"

def test_decomposition_graviton_dof():
    result = kk_dof_decomposition()
    assert result["decomposition"]["4d_graviton_g_munu"]["physical_dof"] == 2

def test_decomposition_vector_dof():
    result = kk_dof_decomposition()
    assert result["decomposition"]["kk_gauge_boson_A_mu"]["physical_dof"] == 2

def test_decomposition_scalar_dof():
    result = kk_dof_decomposition()
    assert result["decomposition"]["radion_scalar"]["physical_dof"] == 1

def test_decomposition_sum_equals_physical():
    result = kk_dof_decomposition()
    d = result["decomposition"]
    total = sum(v["physical_dof"] for v in d.values())
    assert total == result["total_physical_dof"]


# ── U(1) gauge transformation ─────────────────────────────────────────────────

def test_u1_gauge_status():
    result = u1_gauge_transformation()
    assert result["status"] == "T2_ELIMINATED_BY_GAUGE"

def test_u1_gauge_choice():
    result = u1_gauge_transformation()
    assert "t₂" in result["gauge_choice"]

def test_u1_gauge_result():
    result = u1_gauge_transformation()
    assert "t₂(x) → 0" in result["result"]

def test_u1_no_ghost():
    result = u1_gauge_transformation()
    assert "ghost" in result["ghost_check"].lower()


# ── t₂ elimination proof ──────────────────────────────────────────────────────

def test_t2_elimination_status():
    result = t2_gauge_elimination()
    assert result["status"] == "PROVED"

def test_t2_architecture_limit():
    result = t2_gauge_elimination()
    assert result["architecture_limit"] is True

def test_t2_proof_steps_count():
    result = t2_gauge_elimination()
    assert len(result["proof_steps"]) >= 5

def test_t2_conclusion_contains_gauge():
    result = t2_gauge_elimination()
    assert "gauge" in result["conclusion"].lower()

def test_t2_final_step_certified():
    result = t2_gauge_elimination()
    last_step = result["proof_steps"][-1]
    assert "ARCHITECTURE_LIMIT" in last_step["status"]


# ── DoF certificate ───────────────────────────────────────────────────────────

def test_dof_certificate_status():
    result = dof_count_certificate()
    assert result["status"] == "CERTIFIED"

def test_dof_t2_is_zero():
    result = dof_count_certificate()
    assert result["t2_physical_dof"] == 0

def test_dof_total_is_5():
    result = dof_count_certificate()
    assert result["total_physical_dof"] == 5

def test_dof_no_field_includes_t2():
    result = dof_count_certificate()
    for field_key, field_data in result["massless_kk_sector"].items():
        if field_key != "t2_phase":
            assert field_data["includes_t2"] is False


# ── Full certificate ──────────────────────────────────────────────────────────

def test_full_certificate_status():
    cert = t2_gauge_artifact_certificate()
    assert cert["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"

def test_full_certificate_pillar():
    cert = t2_gauge_artifact_certificate()
    assert cert["pillar"] == "683"

def test_full_certificate_all_proved():
    cert = t2_gauge_artifact_certificate()
    assert cert["all_proved"] is True

def test_full_certificate_toe_zero():
    cert = t2_gauge_artifact_certificate()
    assert cert["toe_impact"] == 0

def test_full_certificate_not_a_gap():
    cert = t2_gauge_artifact_certificate()
    assert "NOT_A_GAP" in cert["resolution"]

def test_full_certificate_honest_statement():
    cert = t2_gauge_artifact_certificate()
    assert "pure gauge" in cert["honest_statement"].lower()
