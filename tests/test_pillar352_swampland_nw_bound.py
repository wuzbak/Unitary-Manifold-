# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 352 — Swampland SDC Upper Bound on n_w / R_KK."""
import math
import pytest
from src.core.pillar352_swampland_nw_bound import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE,
    R_KK_UM_UM, M_KK_EV, M_PL_EV, N_W, SDC_ALPHA,
    R_UPPER_BOUND_UM, N_MODES_WGC,
    sdc_upper_bound_r, wgc_species_bound, tcc_ne_bound,
    n_w_swampland_constraint, swampland_consistency_report, separation_guard,
)


# ── Identity ─────────────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 352


def test_constants():
    assert N_W == 5
    assert M_KK_EV == pytest.approx(110e-3)
    assert M_PL_EV == pytest.approx(1.22e28, rel=0.01)
    assert SDC_ALPHA == 1.0


# ── SDC Upper Bound ──────────────────────────────────────────────────────────────

def test_sdc_upper_bound_r_consistent():
    result = sdc_upper_bound_r()
    assert result["consistent_with_sdc"]
    assert result["SDC_verdict"] == "CONSISTENT"


def test_sdc_upper_bound_r_ratio_small():
    result = sdc_upper_bound_r()
    # R_KK << SDC bound → ratio << 1
    assert result["ratio_R_to_bound"] < 1e-3


def test_sdc_upper_bound_r_kk_prediction():
    result = sdc_upper_bound_r()
    assert result["R_kk_um_prediction"] == pytest.approx(R_KK_UM_UM * 0.197e-6 * 1e6, rel=1e-6)


def test_sdc_r_upper_bound_unit():
    result = sdc_upper_bound_r()
    # Upper bound in μm should be >> 1 (much larger than R_KK)
    assert result["R_upper_bound_um"] > 1.0


# ── WGC Species Bound ────────────────────────────────────────────────────────────

def test_wgc_species_bound():
    result = wgc_species_bound()
    assert not result["constrains_n_w"]
    assert result["N_modes_WGC_bound"] == N_MODES_WGC


def test_wgc_species_bound_huge():
    result = wgc_species_bound()
    assert result["N_modes_WGC_bound"] > 1e50


def test_wgc_n_w_not_constrained():
    result = wgc_species_bound()
    assert not result["constrains_n_w"]


# ── TCC N_e Bound ────────────────────────────────────────────────────────────────

def test_tcc_strict_tension():
    result = tcc_ne_bound(strict_tcc=True)
    assert result["N_e_TCC_strict"] > 0
    # Strict TCC gives N_e < 12 (much less than 60)
    assert result["N_e_TCC_strict"] < 60


def test_tcc_strict_status():
    result = tcc_ne_bound(strict_tcc=True)
    assert result["status"] in ("CONSISTENT", "HIGH_TENSION")


def test_tcc_weak_consistent():
    result = tcc_ne_bound(strict_tcc=False)
    # RC-TCC gives N_e < 67 → consistent with N_e = 60
    assert result["N_e_RC_TCC"] == 67.0
    assert result["N_e_UM"] == 60.0
    assert result["consistent_with_tcc"]


def test_tcc_ne_values():
    result = tcc_ne_bound()
    assert result["N_e_UM"] == 60.0
    assert result["N_e_RC_TCC"] == 67.0


# ── n_w Swampland Constraint ─────────────────────────────────────────────────────

def test_n_w_not_constrained():
    result = n_w_swampland_constraint()
    assert not result["is_swampland_constrained"]
    assert result["wgc_verdict"] == "NO_CONSTRAINT"
    assert result["sdc_verdict"] == "CONSISTENT"


def test_n_w_selection_basis():
    result = n_w_swampland_constraint()
    assert "Planck" in result["actual_n_w_selection"]
    assert "APS" in result["actual_n_w_selection"]


# ── Full Report ──────────────────────────────────────────────────────────────────

def test_swampland_consistency_report():
    result = swampland_consistency_report()
    assert result["pillar"] == 352
    assert "CONSISTENT" in result["summary"]["R_KK_vs_SDC"]
    assert "NOT_CONSTRAINED" in result["summary"]["n_w_vs_WGC"]


def test_swampland_report_p339_upgrade():
    result = swampland_consistency_report()
    assert "P339" in result["p339_upgrade"]
    assert "explicit upper bounds" in result["p339_upgrade"].lower()


def test_swampland_r_kk_in_report():
    result = swampland_consistency_report()
    # R_KK should be much smaller than the bound
    sdc = result["sdc_analysis"]
    assert sdc["ratio_R_to_bound"] < 1e-3


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "352" in guard
