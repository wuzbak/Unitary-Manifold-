# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 304 — KATRIN / Project 8 / PTOLEMY Neutrino Mass Preregistration."""
import math
import pytest
from src.core.pillar304_katrin_neutrino_mass_preregistration import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    M1_EV,
    DM2_21_EV2,
    DM2_31_EV2,
    M2_EV,
    M3_EV,
    SUM_MNU_EV,
    THETA_12_DEG,
    THETA_13_DEG,
    THETA_23_DEG,
    U_E1_SQ,
    U_E2_SQ,
    U_E3_SQ,
    M_BETA_SQ_EV2,
    M_BETA_EV,
    KATRIN_CURRENT_LIMIT_EV,
    KATRIN_2026_SENSITIVITY_EV,
    PROJECT8_SENSITIVITY_EV,
    PTOLEMY_SENSITIVITY_EV,
    PLANCK_SUM_LIMIT_EV,
    PLANCK_TENSION_SIGMA,
    separation_guard,
    neutrino_mass_spectrum,
    pmns_electron_row_sq,
    beta_endpoint_mass,
    planck_sum_tension,
    katrin_routing,
    project8_routing,
    ptolemy_routing,
    neutrino_mass_preregistration_package,
    katrin_neutrino_report,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 304

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


# ── Neutrino mass constants ────────────────────────────────────────────────────

def test_m1_ev_positive():
    assert M1_EV > 0

def test_m1_ev_order():
    assert 0.01 < M1_EV < 0.2

def test_m2_m3_from_splittings():
    assert abs(M2_EV - math.sqrt(M1_EV**2 + DM2_21_EV2)) < 1e-8
    assert abs(M3_EV - math.sqrt(M1_EV**2 + DM2_31_EV2)) < 1e-8

def test_mass_ordering():
    # Normal ordering: m₁ < m₂ < m₃
    assert M1_EV < M2_EV < M3_EV

def test_sum_mnu_positive():
    assert SUM_MNU_EV > 0

def test_sum_mnu_is_sum():
    assert abs(SUM_MNU_EV - (M1_EV + M2_EV + M3_EV)) < 1e-8

def test_dm2_21_positive():
    assert DM2_21_EV2 > 0

def test_dm2_31_positive():
    assert DM2_31_EV2 > 0

def test_dm2_31_larger_than_21():
    # Atmospheric >> Solar splitting
    assert DM2_31_EV2 > DM2_21_EV2


# ── PMNS mixing ────────────────────────────────────────────────────────────────

def test_theta12_deg():
    assert 30.0 < THETA_12_DEG < 36.0

def test_theta13_deg():
    assert 7.0 < THETA_13_DEG < 10.0

def test_pmns_unitarity():
    # |U_e1|² + |U_e2|² + |U_e3|² = 1
    total = U_E1_SQ + U_E2_SQ + U_E3_SQ
    assert abs(total - 1.0) < 1e-8

def test_ue1_sq_dominant():
    # θ₁₂ ~ 34°, θ₁₃ ~ 8.6°: |U_e1|² should be ~0.68
    assert U_E1_SQ > 0.5

def test_ue3_sq_small():
    # |U_e3|² = sin²θ₁₃ ~ 0.022
    assert U_E3_SQ < 0.05


# ── Beta-endpoint mass ─────────────────────────────────────────────────────────

def test_m_beta_sq_formula():
    expected = U_E1_SQ * M1_EV**2 + U_E2_SQ * M2_EV**2 + U_E3_SQ * M3_EV**2
    assert abs(M_BETA_SQ_EV2 - expected) < 1e-12

def test_m_beta_positive():
    assert M_BETA_EV > 0

def test_m_beta_order():
    # Should be ~ m₁ (dominated by lightest mass)
    assert 0.01 < M_BETA_EV < 0.15

def test_m_beta_below_current_katrin():
    assert M_BETA_EV < KATRIN_CURRENT_LIMIT_EV

def test_m_beta_below_planck_per_neutrino():
    # m_beta < Σmν/3 would be unusual; check it's plausible
    assert M_BETA_EV < SUM_MNU_EV


# ── Experimental limits ────────────────────────────────────────────────────────

def test_katrin_current_limit():
    assert KATRIN_CURRENT_LIMIT_EV == pytest.approx(0.45, rel=1e-2)

def test_katrin_2026_sensitivity():
    assert KATRIN_2026_SENSITIVITY_EV > 0
    assert KATRIN_2026_SENSITIVITY_EV < KATRIN_CURRENT_LIMIT_EV

def test_project8_sensitivity():
    assert PROJECT8_SENSITIVITY_EV > 0
    assert PROJECT8_SENSITIVITY_EV < KATRIN_2026_SENSITIVITY_EV

def test_planck_sum_limit():
    assert PLANCK_SUM_LIMIT_EV == pytest.approx(0.12, rel=1e-2)

def test_planck_tension_positive():
    # Σmν > Planck limit → positive tension
    assert PLANCK_TENSION_SIGMA > 0


# ── separation_guard ───────────────────────────────────────────────────────────

def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 304

def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False

def test_separation_guard_experiments():
    g = separation_guard()
    exps = g["experiments_preregistered"]
    assert "KATRIN" in exps
    assert "Project_8" in exps
    assert "PTOLEMY" in exps


# ── neutrino_mass_spectrum ─────────────────────────────────────────────────────

def test_spectrum_returns_dict():
    s = neutrino_mass_spectrum()
    assert isinstance(s, dict)

def test_spectrum_normal_ordering():
    s = neutrino_mass_spectrum()
    assert s["ordering"] == "NORMAL"
    assert s["m1_ev"] < s["m2_ev"] < s["m3_ev"]

def test_spectrum_custom_m1():
    s = neutrino_mass_spectrum(m1=0.02)
    assert s["m1_ev"] == pytest.approx(0.02, rel=1e-8)


# ── pmns_electron_row_sq ───────────────────────────────────────────────────────

def test_pmns_returns_tuple():
    r = pmns_electron_row_sq()
    assert len(r) == 3

def test_pmns_unitarity_func():
    ue1, ue2, ue3 = pmns_electron_row_sq()
    assert abs(ue1 + ue2 + ue3 - 1.0) < 1e-8

def test_pmns_all_positive():
    for x in pmns_electron_row_sq():
        assert x > 0


# ── beta_endpoint_mass ─────────────────────────────────────────────────────────

def test_beta_returns_dict():
    b = beta_endpoint_mass()
    assert isinstance(b, dict)
    assert "m_beta_ev" in b

def test_beta_m_beta_positive():
    b = beta_endpoint_mass()
    assert b["m_beta_ev"] > 0

def test_beta_below_katrin():
    b = beta_endpoint_mass()
    assert b["m_beta_ev"] < KATRIN_CURRENT_LIMIT_EV

def test_beta_m_beta_sq_consistent():
    b = beta_endpoint_mass()
    assert abs(b["m_beta_ev"] - math.sqrt(b["m_beta_sq_ev2"])) < 1e-10


# ── planck_sum_tension ─────────────────────────────────────────────────────────

def test_planck_tension_returns_dict():
    pt = planck_sum_tension()
    assert isinstance(pt, dict)

def test_planck_verdict_nonzero():
    pt = planck_sum_tension()
    assert pt["verdict"] != "CONSISTENT_WITH_PLANCK"  # Σmν > 0.12

def test_planck_tension_sigma():
    pt = planck_sum_tension()
    assert pt["tension_sigma"] > 0

def test_planck_excess_positive():
    pt = planck_sum_tension()
    assert pt["excess_ev"] > 0


# ── katrin_routing ─────────────────────────────────────────────────────────────

def test_katrin_routing_current_consistent():
    r = katrin_routing()
    assert r["verdict_current"] == "CONSISTENT"

def test_katrin_routing_below_2026():
    r = katrin_routing()
    # mβ ~ 0.05 eV < 0.20 eV → BELOW_SENSITIVITY for 2026
    assert r["verdict_2026"] == "BELOW_SENSITIVITY"

def test_katrin_routing_consistent_current():
    r = katrin_routing()
    assert r["consistent_current"] is True

def test_katrin_routing_m_beta():
    r = katrin_routing()
    assert r["m_beta_ev"] == pytest.approx(M_BETA_EV, rel=1e-6)


# ── project8_routing ───────────────────────────────────────────────────────────

def test_project8_routing_returns_dict():
    p = project8_routing()
    assert isinstance(p, dict)

def test_project8_verdict_observable():
    p = project8_routing()
    # mβ ~ 0.05 eV > Project 8 target 0.04 eV → OBSERVABLE_WINDOW_OPEN
    assert p["verdict"] == "OBSERVABLE_WINDOW_OPEN"

def test_project8_observable_true():
    p = project8_routing()
    assert p["observable"] is True

def test_project8_falsification_condition():
    p = project8_routing()
    assert "falsification_condition" in p
    assert len(p["falsification_condition"]) > 0


# ── ptolemy_routing ────────────────────────────────────────────────────────────

def test_ptolemy_routing_returns_dict():
    p = ptolemy_routing()
    assert isinstance(p, dict)

def test_ptolemy_verdict():
    p = ptolemy_routing()
    assert p["verdict"] in ("PTOLEMY_OBSERVABLE", "PTOLEMY_MARGINAL")

def test_ptolemy_falsification_condition():
    p = ptolemy_routing()
    assert "falsification_condition" in p


# ── neutrino_mass_preregistration_package ─────────────────────────────────────

def test_package_returns_dict():
    pkg = neutrino_mass_preregistration_package()
    assert isinstance(pkg, dict)

def test_package_version():
    pkg = neutrino_mass_preregistration_package()
    assert pkg["version"] == "v11.11"

def test_package_has_all_experiments():
    pkg = neutrino_mass_preregistration_package()
    assert "katrin" in pkg
    assert "project8" in pkg
    assert "ptolemy" in pkg

def test_package_has_falsifiers():
    pkg = neutrino_mass_preregistration_package()
    assert "falsifiers" in pkg
    assert len(pkg["falsifiers"]) >= 3

def test_package_closure_stamp():
    pkg = neutrino_mass_preregistration_package()
    assert "PREREGISTERED" in pkg["closure_stamp"]
    assert "v11.11" in pkg["closure_stamp"]


# ── katrin_neutrino_report ─────────────────────────────────────────────────────

def test_report_returns_string():
    r = katrin_neutrino_report()
    assert isinstance(r, str)

def test_report_contains_katrin():
    r = katrin_neutrino_report()
    assert "KATRIN" in r

def test_report_contains_project8():
    r = katrin_neutrino_report()
    assert "Project 8" in r or "Project_8" in r or "Project8" in r

def test_report_contains_ptolemy():
    r = katrin_neutrino_report()
    assert "PTOLEMY" in r

def test_report_contains_planck():
    r = katrin_neutrino_report()
    assert "PLANCK" in r.upper() or "Planck" in r

def test_report_contains_preregistered():
    r = katrin_neutrino_report()
    assert "PREREGISTERED" in r
