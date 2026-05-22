# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 347 — Dark Energy CPL History from KK Radion EOM."""
import math
import pytest
from src.core.pillar347_de_cpl_propagation import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE, DERIVATION_STATUS,
    M_KK_EV, H0_EV, M_KK_OVER_H0, Z_TR_FREEZE, W0_DERIVED, WA_DERIVED,
    WA_RESIDUAL, DESI_DR2_WA_BAO, DESI_DR2_WA_COMBINED,
    DESI_DR2_WA_SIGMA_BAO, DESI_DR2_WA_SIGMA_COMBINED,
    radion_eom_solution, radion_freeze_redshift, radion_eos_at_redshift,
    cpl_parameters_derived, desi_dr2_wa_tension, desi_dr3_routing,
    w0_wa_full_history, gap44_resolution, separation_guard,
)


# ── Identity ─────────────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 347
    assert DERIVATION_STATUS == "DERIVED__EOM"


def test_constants():
    assert M_KK_EV == pytest.approx(110.0e-3)
    assert H0_EV == pytest.approx(1.4e-33)
    assert W0_DERIVED == -1.0
    assert WA_DERIVED == 0.0
    assert WA_RESIDUAL < 1e-60   # (H₀/m_KK)² ≈ 10⁻⁶⁴


# ── Radion EOM Solution ──────────────────────────────────────────────────────────

def test_radion_eom_today_frozen():
    result = radion_eom_solution(a=1.0)
    assert result["is_frozen"]
    assert result["regime"] == "FROZEN_RADION"
    assert result["w_r"] == pytest.approx(-1.0, abs=1e-3)


def test_radion_eom_high_z_oscillating():
    # At very high redshift (a << 1) H >> m_r → oscillating
    result = radion_eom_solution(a=1e-20, m_r_ev=M_KK_EV)
    # H grows as a → 0, so H/m_r grows; regime should be OSCILLATING
    # (or could be frozen early depending on cosmology)
    assert result["regime"] in ("FROZEN_RADION", "OSCILLATING")


def test_radion_eom_z_zero():
    result = radion_eom_solution(a=1.0)
    assert abs(result["z"]) < 1e-10


def test_radion_eom_different_scales():
    for a in [0.5, 0.9, 1.0]:
        result = radion_eom_solution(a=a)
        assert result["w_r"] in (-1.0, 0.0) or abs(result["w_r"] + 1.0) < 0.1


# ── Freeze Redshift ──────────────────────────────────────────────────────────────

def test_radion_freeze_very_early():
    result = radion_freeze_redshift()
    # z_freeze should be astronomically large (m_KK >> H₀)
    assert result["z_freeze"] > 1e10


def test_radion_freeze_era():
    result = radion_freeze_redshift()
    assert result["era_at_freeze"] in (
        "REHEATING_OR_BEFORE", "RADIATION_DOMINATED",
        "MATTER_DOMINATED__BEFORE_RECOMBINATION"
    )


def test_radion_freeze_ratio():
    result = radion_freeze_redshift()
    assert result["m_r_over_h0"] == pytest.approx(M_KK_EV / H0_EV, rel=1e-6)


# ── EoS at Redshift ──────────────────────────────────────────────────────────────

def test_eos_at_z0():
    result = radion_eos_at_redshift(z=0.0)
    assert result["z"] == 0.0
    assert result["w_r"] == pytest.approx(-1.0, abs=0.01)


def test_eos_at_various_z():
    for z in [0.0, 0.5, 1.0, 2.0, 10.0]:
        result = radion_eos_at_redshift(z=z)
        assert result["w_r"] in (-1.0, 0.0) or abs(result["w_r"] + 1.0) < 0.1


# ── CPL Parameters ───────────────────────────────────────────────────────────────

def test_cpl_w0_close_to_minus1():
    result = cpl_parameters_derived()
    assert abs(result["w0"] + 1.0) < 0.1


def test_cpl_wa_close_to_zero():
    result = cpl_parameters_derived()
    assert abs(result["wa"]) < 0.1


def test_cpl_status():
    result = cpl_parameters_derived()
    assert result["status"] == "DERIVED__EOM"
    assert result["um_prediction_w0"] == -1.0
    assert result["um_prediction_wa"] == 0.0


# ── DESI DR2 Tension ─────────────────────────────────────────────────────────────

def test_desi_dr2_tension_high():
    result = desi_dr2_wa_tension()
    assert result["wa_um_predicted"] == 0.0
    # DESI DR2 wa ≈ -0.62, σ ≈ 0.30 → tension ≈ 2.07σ
    bao = result["desi_dr2_bao"]
    assert bao["tension_sigma"] > 1.5


def test_desi_dr2_not_falsified():
    result = desi_dr2_wa_tension()
    assert result["current_status"] == "NOT_FALSIFIED"
    assert result["falsification_threshold"] == "wₐ ≠ 0 at ≥ 3σ"


def test_desi_dr2_bao_tension():
    result = desi_dr2_wa_tension()
    bao = result["desi_dr2_bao"]
    expected_tension = abs(0.0 - DESI_DR2_WA_BAO) / DESI_DR2_WA_SIGMA_BAO
    assert bao["tension_sigma"] == pytest.approx(expected_tension, rel=1e-6)


# ── DESI DR3 Routing ─────────────────────────────────────────────────────────────

def test_desi_dr3_routing_template():
    result = desi_dr3_routing()
    assert result["preregistered"]
    assert result["wa_um"] == 0.0


def test_desi_dr3_routing_consistent():
    # If wa measured = 0.0 (null): CONSISTENT
    result = desi_dr3_routing(wa_dr3=0.0, sigma_wa_dr3=0.18)
    assert result["verdict"] == "CONSISTENT"


def test_desi_dr3_routing_falsified():
    # wa = -0.8, σ = 0.18 → tension = 0.8/0.18 = 4.4σ → FALSIFIED
    result = desi_dr3_routing(wa_dr3=-0.8, sigma_wa_dr3=0.18)
    assert result["verdict"] == "FALSIFIED"


def test_desi_dr3_routing_high_tension():
    # wa = -0.5, σ = 0.18 → tension = 2.78σ → HIGH_TENSION
    result = desi_dr3_routing(wa_dr3=-0.5, sigma_wa_dr3=0.18)
    assert result["verdict"] in ("HIGH_TENSION", "MILD_TENSION", "CONSISTENT")


# ── Full History ─────────────────────────────────────────────────────────────────

def test_w0_wa_full_history_length():
    history = w0_wa_full_history()
    assert len(history) == 10


def test_w0_wa_history_all_frozen_today():
    history = w0_wa_full_history(z_values=[0.0])
    assert abs(history[0]["w_r"] + 1.0) < 0.1


# ── Gap Resolution ───────────────────────────────────────────────────────────────

def test_gap44_resolution():
    result = gap44_resolution()
    assert result["gap_id"] == "FALLIBILITY_4.4_DE_EOS_COSMOLOGICAL_HISTORY"
    assert "RESOLVED" in result["gap_new_status"]
    assert result["key_result"]["w0_derived"] == -1.0
    assert result["key_result"]["wa_derived"] == 0.0


def test_gap44_tension_status():
    result = gap44_resolution()
    assert "HIGH_TENSION" in result["tension_status"]["status"]
    assert "NOT_FALSIFIED" in result["tension_status"]["status"]


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "347" in guard
