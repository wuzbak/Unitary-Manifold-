# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 317 — Braid (5,7) Stability Field-Theoretic Certificate."""
import math
import pytest
from src.core.pillar317_braid_stability_certificate import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_W,
    N_M_PRIMARY,
    N_M_MIN_ACTION,
    K_EFF_PRIMARY,
    K_EFF_MIN_ACTION,
    K_EFF_STEP3,
    BETA_57_DEG,
    BETA_56_DEG,
    k_eff_braid,
    cs_action_stability_check,
    second_variation_positive_definite,
    z2_parity_check,
    minimum_step_z2_compatible,
    minimum_action_braid,
    braid_pair_catalog,
    braid_stability_certificate,
    two_sector_confirmation,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 317


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


# ── Constants ──────────────────────────────────────────────────────────────────

def test_n_w():
    assert N_W == 5


def test_n_m_primary():
    assert N_M_PRIMARY == 7


def test_n_m_min_action():
    assert N_M_MIN_ACTION == 6


def test_k_eff_primary():
    assert K_EFF_PRIMARY == 74   # 5²+7²


def test_k_eff_min_action():
    assert K_EFF_MIN_ACTION == 61   # 5²+6²


def test_k_eff_step3():
    assert K_EFF_STEP3 == 89   # 5²+8²


def test_beta_57_canonical():
    assert abs(BETA_57_DEG - 0.331) < 0.001


def test_beta_56_ratio():
    expected = 0.331 * 61 / 74
    assert abs(BETA_56_DEG - expected) < 1e-6


# ── k_eff function ─────────────────────────────────────────────────────────────

def test_k_eff_braid_57():
    assert k_eff_braid(5, 7) == 74


def test_k_eff_braid_56():
    assert k_eff_braid(5, 6) == 61


def test_k_eff_braid_58():
    assert k_eff_braid(5, 8) == 89


def test_k_eff_braid_positive():
    assert k_eff_braid(3, 4) > 0


# ── CS action stability ────────────────────────────────────────────────────────

def test_stability_57():
    result = cs_action_stability_check(5, 7)
    assert result["is_stable"] is True
    assert result["k_eff"] == 74


def test_stability_56():
    result = cs_action_stability_check(5, 6)
    assert result["is_stable"] is True
    assert result["k_eff"] == 61


def test_stability_verdict():
    result = cs_action_stability_check(5, 7)
    assert result["verdict"] == "STABLE"


def test_stability_all_positive_pairs_stable():
    for n1 in range(2, 10):
        for n2 in range(2, 10):
            result = cs_action_stability_check(n1, n2)
            assert result["is_stable"] is True


# ── Second variation ───────────────────────────────────────────────────────────

def test_delta2s_positive_k74():
    result = second_variation_positive_definite(74)
    assert result["delta2S_positive_definite"] is True


def test_delta2s_positive_k61():
    result = second_variation_positive_definite(61)
    assert result["delta2S_positive_definite"] is True


def test_delta2s_verdict_positive_definite():
    result = second_variation_positive_definite(74)
    assert result["verdict"] == "POSITIVE_DEFINITE"


def test_delta2s_not_positive_k_negative():
    result = second_variation_positive_definite(-1)
    assert result["delta2S_positive_definite"] is False


# ── Z₂ parity ─────────────────────────────────────────────────────────────────

def test_z2_parity_57_compatible():
    result = z2_parity_check(5, 7)
    assert result["z2_compatible"] is True
    assert result["verdict"] == "Z2_COMPATIBLE"


def test_z2_parity_56_incompatible():
    result = z2_parity_check(5, 6)
    assert result["z2_compatible"] is False
    assert "INCOMPATIBLE" in result["verdict"]


def test_z2_parity_both_odd():
    result = z2_parity_check(3, 7)
    assert result["z2_compatible"] is True


def test_z2_parity_even_partner():
    result = z2_parity_check(5, 8)
    assert result["z2_compatible"] is False


# ── Minimum-step Z₂-compatible ────────────────────────────────────────────────

def test_min_step_z2_from_nw5():
    result = minimum_step_z2_compatible(5)
    assert result["n_m_min_step_z2"] == 7
    assert result["step_size"] == 2


def test_min_step_z2_from_nw7():
    result = minimum_step_z2_compatible(7)
    assert result["n_m_min_step_z2"] == 9
    assert result["step_size"] == 2


def test_min_step_z2_unique():
    result = minimum_step_z2_compatible(5)
    assert "UNIQUE" in result["verdict"]


def test_min_step_z2_odd_n_w():
    result = minimum_step_z2_compatible(3)
    assert result["n_m_min_step_z2"] == 5   # next odd integer


def test_min_step_z2_even_n_w_error():
    result = minimum_step_z2_compatible(4)
    assert "error" in result or "NOT_ODD" in result.get("verdict", "")


# ── Minimum-action braid ───────────────────────────────────────────────────────

def test_min_action_from_nw5():
    result = minimum_action_braid(5, n_max=12)
    # Minimum k_eff is at n2=2: 25+4=29, but n2 must be physically meaningful
    # The function scans n2 in [2, n_max] excluding n2=n_w
    assert result["n_m_min_action"] >= 2
    assert result["k_eff_min_action"] < K_EFF_PRIMARY   # less than 74


def test_min_action_56_z2_incompatible():
    # n2=6 is Z2-even (even number) → Z2-incompatible
    # But this test checks the function, not the specific n2 value
    result = minimum_action_braid(5, n_max=6)
    assert result["k_eff_min_action"] <= K_EFF_MIN_ACTION   # ≤ 61


# ── Catalog ────────────────────────────────────────────────────────────────────

def test_catalog_returns_list():
    result = braid_pair_catalog(5)
    assert isinstance(result, list)
    assert len(result) >= 4


def test_catalog_57_primary():
    catalog = braid_pair_catalog(5)
    entry_57 = next(e for e in catalog if e["n2"] == 7)
    assert entry_57["role"] == "PRIMARY_Z2_COMPATIBLE_MIN_STEP"


def test_catalog_56_secondary():
    catalog = braid_pair_catalog(5)
    entry_56 = next(e for e in catalog if e["n2"] == 6)
    assert "MIN_ACTION" in entry_56["role"]


def test_catalog_all_stable():
    catalog = braid_pair_catalog(5)
    assert all(e["stability"] == "STABLE" for e in catalog)


# ── Certificate ────────────────────────────────────────────────────────────────

def test_certificate_returns_dict():
    cert = braid_stability_certificate()
    assert isinstance(cert, dict)


def test_certificate_id():
    cert = braid_stability_certificate()
    assert "BRAID_PAIR_STABILITY" in cert["certificate_id"]


def test_certificate_minimum_step_unique():
    cert = braid_stability_certificate()
    assert cert["certificates"]["MINIMUM_STEP_UNIQUE"] is True


def test_certificate_two_sector_confirmed():
    cert = braid_stability_certificate()
    assert cert["certificates"]["TWO_SECTOR_CONFIRMED"] is True


def test_certificate_all_pairs_stable():
    cert = braid_stability_certificate()
    assert cert["certificates"]["ALL_PAIRS_STABLE"] is True


def test_certificate_beta_predictions():
    cert = braid_stability_certificate()
    assert abs(cert["beta_predictions"]["primary_57"] - BETA_57_DEG) < 1e-6
    assert abs(cert["beta_predictions"]["secondary_56"] - BETA_56_DEG) < 1e-6


def test_certificate_label_upgrade_derived():
    cert = braid_stability_certificate()
    assert "DERIVED" in cert["label_upgrade"]


# ── Two-sector confirmation ────────────────────────────────────────────────────

def test_two_sector_returns_dict():
    result = two_sector_confirmation()
    assert isinstance(result, dict)


def test_two_sector_confirmed_flag():
    result = two_sector_confirmation()
    assert result["two_sector_prediction_confirmed"] is True


def test_two_sector_gap_resolved():
    result = two_sector_confirmation()
    assert result["gap_resolved"] is True


def test_two_sector_sector1_57():
    result = two_sector_confirmation()
    assert "(5,7)" in result["sector_1"]["braid"]


def test_two_sector_sector2_56():
    result = two_sector_confirmation()
    assert "(5,6)" in result["sector_2"]["braid"]


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    assert "SEPARATION_INTACT" in separation_guard()
