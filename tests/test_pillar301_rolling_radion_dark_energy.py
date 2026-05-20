# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 301 — Rolling Radion Dark Energy Architecture Limit."""
import math
import pytest
from src.core.pillar301_rolling_radion_dark_energy import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    H0_GEV,
    M_KK_BENCHMARK_GEV,
    GW_EPSILON_BENCHMARK,
    M_RADION_BENCHMARK_GEV,
    ETA_BENCHMARK,
    DESI_DR2_WA_CENTRAL,
    DESI_DR2_WA_SIGMA,
    DESI_DR2_TENSION_SIGMA,
    DESI_FALSIFICATION_SIGMA,
    M_RADION_REQUIRED_FOR_DESI_GEV,
    GW_EPSILON_REQUIRED_FOR_DESI,
    LOG10_FINE_TUNING,
    ARCHITECTURE_LIMIT_STATUS,
    separation_guard,
    radion_mass_gev,
    radion_hubble_ratio,
    cpl_wa_from_rolling,
    required_radion_mass_for_wa,
    required_gw_epsilon_for_wa,
    fine_tuning_cost,
    mkk_required_for_natural_rolling,
    hierarchy_violation_check,
    desi_dr3_routing,
    rolling_radion_architecture_limit_certificate,
    rolling_radion_report,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 301

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

def test_pillar_title_contains_rolling():
    assert "Rolling" in PILLAR_TITLE or "rolling" in PILLAR_TITLE.lower()

def test_architecture_limit_status():
    assert "ARCHITECTURE_LIMIT" in ARCHITECTURE_LIMIT_STATUS


# ── Physical constants ──────────────────────────────────────────────────────

def test_h0_gev_positive():
    assert H0_GEV > 0

def test_h0_gev_order_of_magnitude():
    # H₀ ~ 10⁻⁴² GeV
    assert 1e-44 < H0_GEV < 1e-40

def test_m_kk_benchmark_one_tev():
    assert M_KK_BENCHMARK_GEV == 1000.0

def test_gw_epsilon_benchmark_small():
    assert 0 < GW_EPSILON_BENCHMARK < 0.1

def test_m_radion_benchmark():
    # m_r = sqrt(ε) × M_KK = 0.1 × 1000 = 100 GeV
    expected = math.sqrt(GW_EPSILON_BENCHMARK) * M_KK_BENCHMARK_GEV
    assert abs(M_RADION_BENCHMARK_GEV - expected) < 1e-6

def test_eta_benchmark_large():
    # m_r/H₀ ~ 10⁴³
    assert ETA_BENCHMARK > 1e40

def test_desi_dr2_wa_central_negative():
    assert DESI_DR2_WA_CENTRAL < 0

def test_desi_dr2_tension_sigma():
    # Should be ~2.75σ
    assert 2.0 < DESI_DR2_TENSION_SIGMA < 4.0

def test_desi_falsification_threshold():
    assert DESI_FALSIFICATION_SIGMA == 3.0

def test_m_radion_required_tiny():
    # Must be ~ H₀ × 1.9 ~ 2.75 × 10⁻⁴² GeV
    assert M_RADION_REQUIRED_FOR_DESI_GEV < 1e-38

def test_gw_epsilon_required_extremely_small():
    # Should be ~ 10⁻⁸⁸
    assert GW_EPSILON_REQUIRED_FOR_DESI < 1e-80

def test_log10_fine_tuning_large_negative():
    # log10(ε_required / ε_benchmark) should be ~ -86
    assert LOG10_FINE_TUNING < -70


# ── separation_guard ───────────────────────────────────────────────────────────

def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 301

def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False

def test_separation_guard_no_toe_mod():
    g = separation_guard()
    assert g["modifies_toe_score"] is False

def test_separation_guard_closes_gap():
    g = separation_guard()
    assert "ARCHITECTURE_LIMIT" in g["closes_gap"]

def test_separation_guard_tension_sigma():
    g = separation_guard()
    assert g["desi_dr2_tension_sigma"] == pytest.approx(DESI_DR2_TENSION_SIGMA, rel=1e-3)


# ── radion_mass_gev ────────────────────────────────────────────────────────────

def test_radion_mass_benchmark():
    m_r = radion_mass_gev(1000.0, 0.01)
    assert abs(m_r - 100.0) < 1e-6

def test_radion_mass_scaling():
    m1 = radion_mass_gev(500.0, 0.04)
    m2 = radion_mass_gev(1000.0, 0.01)
    assert abs(m1 - m2) < 1e-6  # both = 100 GeV

def test_radion_mass_invalid_mkk():
    with pytest.raises(ValueError):
        radion_mass_gev(-1.0, 0.01)

def test_radion_mass_invalid_epsilon():
    with pytest.raises(ValueError):
        radion_mass_gev(1000.0, 0.0)


# ── radion_hubble_ratio ────────────────────────────────────────────────────────

def test_radion_hubble_ratio_benchmark():
    eta = radion_hubble_ratio(1000.0, 0.01)
    assert eta > 1e40

def test_radion_hubble_ratio_positive():
    eta = radion_hubble_ratio(100.0, 0.01)
    assert eta > 0


# ── cpl_wa_from_rolling ────────────────────────────────────────────────────────

def test_cpl_wa_benchmark_near_zero():
    wa = cpl_wa_from_rolling(1000.0, 0.01)
    assert abs(wa) < 1e-80  # m_r >> H₀ → wₐ ≈ 0

def test_cpl_wa_negative():
    wa = cpl_wa_from_rolling(1000.0, 0.01)
    assert wa < 0  # slow roll gives negative wₐ


# ── required_radion_mass_for_wa ────────────────────────────────────────────────

def test_required_mass_for_desi():
    m_r = required_radion_mass_for_wa(-0.55)
    assert abs(m_r - M_RADION_REQUIRED_FOR_DESI_GEV) < 1e-50

def test_required_mass_positive_wa_raises():
    with pytest.raises(ValueError):
        required_radion_mass_for_wa(0.1)

def test_required_mass_for_smaller_wa():
    # Smaller |wₐ| → larger m_r
    m1 = required_radion_mass_for_wa(-0.55)
    m2 = required_radion_mass_for_wa(-0.1)
    assert m2 > m1


# ── required_gw_epsilon_for_wa ─────────────────────────────────────────────────

def test_gw_epsilon_for_desi():
    eps = required_gw_epsilon_for_wa(-0.55, 1000.0)
    assert eps < 1e-80

def test_gw_epsilon_monotone_in_mkk():
    # Larger M_KK → smaller needed ε
    eps1 = required_gw_epsilon_for_wa(-0.55, 1000.0)
    eps2 = required_gw_epsilon_for_wa(-0.55, 100.0)
    assert eps1 < eps2


# ── fine_tuning_cost ───────────────────────────────────────────────────────────

def test_fine_tuning_returns_dict():
    ft = fine_tuning_cost(-0.55)
    assert isinstance(ft, dict)

def test_fine_tuning_log10_negative():
    ft = fine_tuning_cost(-0.55)
    assert ft["log10_tuning"] < -70

def test_fine_tuning_eta_natural_large():
    ft = fine_tuning_cost(-0.55)
    assert ft["eta_natural"] > 1e40

def test_fine_tuning_wa_natural_near_zero():
    ft = fine_tuning_cost(-0.55)
    assert abs(ft["wa_natural"]) < 1e-80

def test_fine_tuning_target_stored():
    ft = fine_tuning_cost(-0.55)
    assert ft["wa_target"] == -0.55


# ── mkk_required_for_natural_rolling ──────────────────────────────────────────

def test_mkk_required_subplanck():
    m_kk = mkk_required_for_natural_rolling(-0.55)
    # Should be far below 1 TeV
    assert m_kk < 1.0  # less than 1 GeV


# ── hierarchy_violation_check ──────────────────────────────────────────────────

def test_hierarchy_violation_check_destroyed():
    hv = hierarchy_violation_check(-0.55)
    assert hv["hierarchy_intact"] is False

def test_hierarchy_violation_verdict():
    hv = hierarchy_violation_check(-0.55)
    assert "DESTROYED" in hv["verdict"] or "UNNATURAL" in hv["verdict"]

def test_hierarchy_violation_mkk_tiny():
    hv = hierarchy_violation_check(-0.55)
    assert hv["m_kk_required_gev"] < 1.0


# ── desi_dr3_routing ───────────────────────────────────────────────────────────

def test_dr3_routing_consistent():
    r = desi_dr3_routing(0.05, 0.1)
    assert r["verdict"] == "CONSISTENT"

def test_dr3_routing_tension():
    r = desi_dr3_routing(-0.30, 0.10)
    assert "TENSION" in r["verdict"]

def test_dr3_routing_falsified():
    r = desi_dr3_routing(-0.60, 0.10)
    assert r["verdict"] == "FALSIFIED"

def test_dr3_routing_dr2_is_tension():
    r = desi_dr3_routing(DESI_DR2_WA_CENTRAL, DESI_DR2_WA_SIGMA)
    # DR2 at 2.75σ is HIGH_TENSION (not falsified)
    assert r["verdict"] in ("TENSION", "TENSION_PRE_THRESHOLD")

def test_dr3_routing_sigma_pull():
    r = desi_dr3_routing(-0.55, 0.20)
    assert r["sigma_pull"] == pytest.approx(2.75, rel=1e-2)


# ── rolling_radion_architecture_limit_certificate ─────────────────────────────

def test_cert_returns_dict():
    cert = rolling_radion_architecture_limit_certificate()
    assert isinstance(cert, dict)

def test_cert_type():
    cert = rolling_radion_architecture_limit_certificate()
    assert cert["certificate_type"] == "ARCHITECTURE_LIMIT_CERTIFICATE"

def test_cert_um_wa_zero():
    cert = rolling_radion_architecture_limit_certificate()
    assert cert["um_wa_prediction"] == 0.0

def test_cert_hierarchy_destroyed():
    cert = rolling_radion_architecture_limit_certificate()
    assert cert["hierarchy_destroyed"] is True

def test_cert_closure_stamp_final():
    cert = rolling_radion_architecture_limit_certificate()
    assert "FINAL" in cert["closure_stamp"]

def test_cert_fine_tuning_enormous():
    cert = rolling_radion_architecture_limit_certificate()
    assert cert["log10_fine_tuning"] < -70


# ── rolling_radion_report ──────────────────────────────────────────────────────

def test_report_returns_string():
    r = rolling_radion_report()
    assert isinstance(r, str)

def test_report_contains_pillar():
    r = rolling_radion_report()
    assert "301" in r

def test_report_contains_desi():
    r = rolling_radion_report()
    assert "DESI" in r

def test_report_contains_final():
    r = rolling_radion_report()
    assert "FINAL" in r
