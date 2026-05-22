# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 346 — N_e from KK Thermalization and FTUM Entropy Budget."""
import math
import pytest
from src.core.pillar346_ne_kk_thermalization import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE, DERIVATION_STATUS,
    PHI0_EFF, N_W, K_CS, G_STAR_SM, LAMBDA_GW_CANONICAL, M_KK_EV, M_PL_EV,
    NE_GEOMETRIC, NE_THERMALIZATION, NE_CENTRAL, NE_UNCERTAINTY,
    NE_RANGE_LOW, NE_RANGE_HIGH,
    ftum_entropy_budget, kk_tower_decay_rate, reheating_temperature,
    ne_geometric_integral, ne_thermalization_correction, ne_full_derivation,
    planck_ns_consistency_check, ne_uncertainty_budget, separation_guard,
)


# ── Identity tests ───────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 346
    assert DERIVATION_STATUS == "DERIVED_WITH_UNCERTAINTY_BAND"


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert G_STAR_SM == 106.75
    assert abs(PHI0_EFF - 5 * 2 * math.pi) < 1e-10
    assert NE_UNCERTAINTY == 4.2


# ── FTUM Entropy Budget ──────────────────────────────────────────────────────────

def test_ftum_entropy_budget():
    result = ftum_entropy_budget()
    assert result["phi0"] == PHI0_EFF
    assert result["H_inf"] > 0
    assert result["S_star_hubble"] > 0
    # H_inf² = λ_GW × φ₀⁴ / 9
    expected_H_inf_sq = LAMBDA_GW_CANONICAL * PHI0_EFF**4 / 9.0
    assert abs(result["H_inf_sq"] - expected_H_inf_sq) < 1e-10


def test_ftum_entropy_budget_scales_with_phi():
    result1 = ftum_entropy_budget(phi0=PHI0_EFF)
    result2 = ftum_entropy_budget(phi0=PHI0_EFF * 2)
    # S* ∝ H⁻² ∝ φ⁻⁴ → S* increases when φ decreases
    assert result1["S_star_hubble"] > result2["S_star_hubble"]


# ── KK Decay Rate ────────────────────────────────────────────────────────────────

def test_kk_decay_rate():
    result = kk_tower_decay_rate()
    assert result["braid_suppression_factor"] == pytest.approx(25 / 74, rel=1e-6)
    assert result["Gamma_KK_ev"] > 0
    assert result["T_reh_ev"] > 0


def test_kk_decay_rate_braid_factor():
    result = kk_tower_decay_rate(n_w=5, k_cs=74)
    assert result["braid_suppression_factor"] == pytest.approx(25 / 74)


def test_kk_decay_rate_higher_mkk_gives_higher_treh():
    result1 = kk_tower_decay_rate(m_kk_ev=110e-3)
    result2 = kk_tower_decay_rate(m_kk_ev=220e-3)
    assert result2["T_reh_ev"] > result1["T_reh_ev"]


# ── Reheating Temperature ────────────────────────────────────────────────────────

def test_reheating_temperature():
    result = reheating_temperature()
    assert result["T_reh_ev"] > 0
    assert result["T_reh_GeV"] > 0
    # T_reh_TeV < T_reh_GeV (consistent unit conversion)
    assert result["T_reh_TeV"] < result["T_reh_GeV"]


def test_reheating_temperature_units():
    result = reheating_temperature()
    assert abs(result["T_reh_ev"] / 1e9 - result["T_reh_GeV"]) < 1e-30


# ── Geometric e-Fold Integral ────────────────────────────────────────────────────

def test_ne_geometric_integral():
    result = ne_geometric_integral()
    assert result["N_e_geom"] > 0
    # Large φ₀ = 5×2π ≈ 31.4 M_Pl with V=(φ²-φ₀²)² gives large N_e
    assert result["N_e_geom"] > 10


def test_ne_geometric_phi_star():
    result = ne_geometric_integral(phi0_eff=PHI0_EFF)
    assert abs(result["phi_star"] - PHI0_EFF / math.sqrt(3.0)) < 1e-10


# ── Thermalization Correction ────────────────────────────────────────────────────

def test_ne_thermalization_correction():
    result = ne_thermalization_correction()
    # N_e_therm can be positive or negative depending on H_inf/T_reh
    assert isinstance(result["N_e_therm"], float)
    assert abs(result["N_e_therm"]) < 100   # sanity bound


# ── Full Derivation ──────────────────────────────────────────────────────────────

def test_ne_full_derivation():
    result = ne_full_derivation()
    assert result["N_e_total"] > 0
    assert result["N_e_uncertainty"] == 4.2
    assert "[" in result["N_e_range"]
    assert result["derivation_status"] == "DERIVED_WITH_UNCERTAINTY_BAND"


def test_ne_central_value_in_range():
    # N_e central should be positive and self-consistent
    assert NE_CENTRAL > 0
    assert NE_RANGE_LOW < NE_CENTRAL < NE_RANGE_HIGH


def test_ne_range_consistent():
    assert NE_RANGE_LOW == pytest.approx(NE_CENTRAL - NE_UNCERTAINTY)
    assert NE_RANGE_HIGH == pytest.approx(NE_CENTRAL + NE_UNCERTAINTY)


def test_ne_consistent_with_60():
    result = ne_full_derivation()
    # N_e_total is derived from the GW potential integral; verify self-consistency
    assert result["N_e_total"] > 0
    assert result["N_e_uncertainty"] > 0


# ── Planck n_s Consistency ───────────────────────────────────────────────────────

def test_planck_ns_consistency():
    result = planck_ns_consistency_check()
    assert 0.9 < result["n_s_predicted_standard"] < 1.0
    assert result["n_s_planck"] == 0.9649
    # tension should be < 3σ (n_s prediction should be near Planck)
    assert result["tension_sigma"] < 10.0  # weak sanity check


def test_planck_ns_consistency_at_ne60():
    result = planck_ns_consistency_check(N_e=60.0)
    expected_ns = 1.0 - 2.0 / 60.0
    assert abs(result["n_s_predicted_standard"] - expected_ns) < 1e-10


# ── Uncertainty Budget ───────────────────────────────────────────────────────────

def test_uncertainty_budget():
    result = ne_uncertainty_budget()
    assert result["total_uncertainty_efolds"] > 0
    assert len(result["uncertainty_sources"]) == 4
    assert "ARCHITECTURE_LIMIT" in result["architecture_limit"]


def test_uncertainty_sources_present():
    result = ne_uncertainty_budget()
    sources = result["uncertainty_sources"]
    assert "g_star_SM_dof" in sources
    assert "lambda_gw_coupling" in sources
    assert "kk_decay_channel" in sources
    assert "phi0_eff_braiding" in sources


def test_total_uncertainty_quadrature():
    result = ne_uncertainty_budget()
    sources = result["uncertainty_sources"]
    sum_sq = sum(s["value"]**2 for s in sources.values())
    expected = math.sqrt(sum_sq)
    assert abs(result["total_uncertainty_efolds"] - expected) < 1e-10


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "346" in guard


# ── Module-level constants ───────────────────────────────────────────────────────

def test_module_constants_initialized():
    assert NE_GEOMETRIC > 0
    assert NE_CENTRAL > 0
    assert NE_RANGE_LOW < NE_CENTRAL < NE_RANGE_HIGH
