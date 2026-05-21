# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 313 — G_{μ5} Z₂-Parity Derivation (Admission 3 Closure)."""
import math
import pytest
from src.core.pillar313_gmu5_z2_parity_derivation import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    ADMISSION_3_PRIOR_STATUS,
    ADMISSION_3_NEW_STATUS,
    GMU5_Z2_PARITY,
    path1_cotangent_bundle_argument,
    path2_israel_junction_argument,
    path3_kk_gauge_consistency_argument,
    path4_kk_mode_expansion_argument,
    combined_gmu5_z2_derivation,
    admission_3_updated_status,
    cotangent_sign_check,
    kk_mode_dirichlet_check,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 313


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_gmu5_parity_label():
    assert GMU5_Z2_PARITY == "Z2_ODD"


def test_admission_3_prior_contains_open():
    assert "OPEN" in ADMISSION_3_PRIOR_STATUS


def test_admission_3_new_contains_minimal_axiom():
    assert "MINIMAL_AXIOM" in ADMISSION_3_NEW_STATUS


# ── PATH 1 — Cotangent bundle ─────────────────────────────────────────────────

def test_path1_returns_dict():
    result = path1_cotangent_bundle_argument()
    assert isinstance(result, dict)


def test_path1_path_id():
    assert path1_cotangent_bundle_argument()["path"] == "PATH1_COTANGENT_BUNDLE"


def test_path1_gmu5_is_z2_odd():
    assert path1_cotangent_bundle_argument()["gmu5_parity"] == "Z2_ODD"


def test_path1_g_munu_is_z2_even():
    assert path1_cotangent_bundle_argument()["g_munu_parity"] == "Z2_EVEN"


def test_path1_phi_sq_is_z2_even():
    assert path1_cotangent_bundle_argument()["phi_sq_parity"] == "Z2_EVEN"


def test_path1_verdict_derived():
    assert "DERIVED" in path1_cotangent_bundle_argument()["verdict"]


def test_path1_residual_primitive_mentions_p7():
    assert "P7" in path1_cotangent_bundle_argument()["residual_primitive"]


# ── PATH 2 — Israel junction ──────────────────────────────────────────────────

def test_path2_returns_dict():
    result = path2_israel_junction_argument()
    assert isinstance(result, dict)


def test_path2_path_id():
    assert path2_israel_junction_argument()["path"] == "PATH2_ISRAEL_JUNCTION_CONDITIONS"


def test_path2_gmu5_is_z2_odd():
    assert path2_israel_junction_argument()["gmu5_parity"] == "Z2_ODD"


def test_path2_shift_vector_is_z2_odd():
    assert path2_israel_junction_argument()["shift_vector_parity"] == "Z2_ODD"


def test_path2_extrinsic_curvature_is_z2_even():
    assert path2_israel_junction_argument()["extrinsic_curvature_parity"] == "Z2_EVEN"


def test_path2_verdict_derived():
    assert "DERIVED" in path2_israel_junction_argument()["verdict"]


# ── PATH 3 — KK gauge consistency ────────────────────────────────────────────

def test_path3_returns_dict():
    result = path3_kk_gauge_consistency_argument()
    assert isinstance(result, dict)


def test_path3_path_id():
    assert "GAUGE" in path3_kk_gauge_consistency_argument()["path"]


def test_path3_xi5_parity_odd():
    assert path3_kk_gauge_consistency_argument()["xi5_parity"] == "Z2_ODD"


def test_path3_gmu5_zero_mode_parity_odd():
    assert path3_kk_gauge_consistency_argument()["gmu5_zero_mode_parity"] == "Z2_ODD"


def test_path3_verdict_derived():
    assert "DERIVED" in path3_kk_gauge_consistency_argument()["verdict"]


# ── PATH 4 — KK mode expansion ───────────────────────────────────────────────

def test_path4_returns_dict():
    result = path4_kk_mode_expansion_argument()
    assert isinstance(result, dict)


def test_path4_mode_type_is_sine():
    assert "SINE" in path4_kk_mode_expansion_argument()["gmu5_mode_type"]


def test_path4_zero_mode_absent():
    assert "ABSENT" in path4_kk_mode_expansion_argument()["zero_mode_status"]


def test_path4_gmu5_parity_odd():
    assert path4_kk_mode_expansion_argument()["gmu5_parity"] == "Z2_ODD"


def test_path4_verdict_derived():
    assert "DERIVED" in path4_kk_mode_expansion_argument()["verdict"]


# ── Combined derivation ────────────────────────────────────────────────────────

def test_combined_all_paths_agree():
    cert = combined_gmu5_z2_derivation()
    assert cert["all_paths_agree"] is True


def test_combined_gmu5_parity():
    cert = combined_gmu5_z2_derivation()
    assert cert["gmu5_parity"] == "Z2_ODD"


def test_combined_upgrade_achieved():
    cert = combined_gmu5_z2_derivation()
    assert cert["upgrade_achieved"] is True


def test_combined_n_paths():
    cert = combined_gmu5_z2_derivation()
    assert len(cert["paths"]) == 4


def test_combined_label_upgrade_mentions_minimal_axiom():
    cert = combined_gmu5_z2_derivation()
    assert "MINIMAL_AXIOM" in cert["label_upgrade"]


def test_combined_residual_primitive_mentions_p7():
    cert = combined_gmu5_z2_derivation()
    assert "P7" in cert["residual_primitive"]


# ── Admission 3 updated status ────────────────────────────────────────────────

def test_admission_3_status_returns_dict():
    status = admission_3_updated_status()
    assert isinstance(status, dict)


def test_admission_3_status_id():
    status = admission_3_updated_status()
    assert "ADMISSION_3" in status["admission_id"]


def test_admission_3_new_label():
    status = admission_3_updated_status()
    assert "MINIMAL_AXIOM" in status["new_label"]


def test_admission_3_n_paths():
    status = admission_3_updated_status()
    assert status["n_independent_paths"] == 4


def test_admission_3_all_agree():
    status = admission_3_updated_status()
    assert status["all_paths_agree"] is True


def test_admission_3_gmu5_parity():
    status = admission_3_updated_status()
    assert status["gmu5_parity"] == "Z2_ODD"


def test_admission_3_nw5_theorem_status():
    status = admission_3_updated_status()
    assert "GROUNDED" in status["nw5_theorem_status"]


def test_admission_3_pillar():
    status = admission_3_updated_status()
    assert status["derivation_pillar"] == 313


# ── Quantitative checks ───────────────────────────────────────────────────────

@pytest.mark.parametrize("y_val", [0.1, 0.5, 1.0, math.pi / 4, math.pi / 2])
def test_cotangent_sign_check_sum_is_zero(y_val):
    result = cotangent_sign_check(y_val)
    assert result["sum_is_zero"] is True


def test_cotangent_sign_check_verdict():
    result = cotangent_sign_check(1.0)
    assert result["verdict"] == "Z2_ODD_CONFIRMED"


def test_cotangent_sign_check_values():
    result = cotangent_sign_check(1.0)
    assert abs(result["gmu5_y"] + result["gmu5_minus_y"]) < 1e-12


def test_kk_mode_dirichlet_check_all_satisfied():
    result = kk_mode_dirichlet_check(n_modes=5)
    assert result["all_dirichlet_satisfied"] is True


def test_kk_mode_dirichlet_check_verdict():
    result = kk_mode_dirichlet_check(n_modes=5)
    assert "CONFIRMED" in result["verdict"]


def test_kk_mode_dirichlet_check_n_modes():
    result = kk_mode_dirichlet_check(n_modes=7)
    assert result["modes_checked"] == 7


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard_string():
    result = separation_guard()
    assert "SEPARATION_INTACT" in result


def test_separation_guard_adjacent_track():
    result = separation_guard()
    assert "adjacent-track" in result.lower()
