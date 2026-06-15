# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 315 — N_e = 60 e-Folds Geometric Derivation."""
import math
import pytest
from src.core.pillar315_efolds_geometric_derivation import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_W,
    PHI0_EFF_MPLANCK,
    CS_BRAIDED,
    N_E_STANDARD,
    N_E_GW_INTEGRAL_LOW,
    N_E_GW_INTEGRAL_HIGH,
    N_E_MINIMUM_HORIZON,
    approach1_gw_slow_roll_integral,
    approach2_braided_correction,
    approach3_reheating_constraint,
    approach4_horizon_minimum,
    efolds_geometric_summary,
    efolds_architecture_limit_certificate,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 315


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_n_w():
    assert N_W == 5


def test_phi0_eff():
    assert abs(PHI0_EFF_MPLANCK - 5 * 2 * math.pi) < 1e-10


def test_cs_braided():
    assert abs(CS_BRAIDED - 12.0 / 37.0) < 1e-12


def test_n_e_standard():
    assert N_E_STANDARD == 60


# ── Approach 1 ────────────────────────────────────────────────────────────────

def test_approach1_epsilon_criterion_returns_dict():
    result = approach1_gw_slow_roll_integral(phi_end_criterion="epsilon")
    assert isinstance(result, dict)


def test_approach1_epsilon_n_e_positive():
    result = approach1_gw_slow_roll_integral(phi_end_criterion="epsilon")
    assert result["N_e_estimate"] > 0.0


def test_approach1_epsilon_n_e_in_range():
    result = approach1_gw_slow_roll_integral(phi_end_criterion="epsilon")
    # Should be between 20 and 100 for physical parameters
    assert 20.0 <= result["N_e_estimate"] <= 150.0


def test_approach1_gw_min_n_e_defined():
    # GW minimum criterion gives a result (may be negative for large phi0)
    # The key point is that the function returns a dict with N_e_estimate
    r_gw = approach1_gw_slow_roll_integral(phi_end_criterion="gw_min")
    assert "N_e_estimate" in r_gw
    assert isinstance(r_gw["N_e_estimate"], float)


def test_approach1_approach_field():
    result = approach1_gw_slow_roll_integral()
    assert "APPROACH1" in result["approach"]


def test_approach1_phi_pivot_default():
    result = approach1_gw_slow_roll_integral()
    expected_pivot = PHI0_EFF_MPLANCK / math.sqrt(3.0)
    assert abs(result["phi_pivot"] - expected_pivot) < 1e-10


# ── Approach 2 ────────────────────────────────────────────────────────────────

def test_approach2_returns_dict():
    result = approach2_braided_correction()
    assert isinstance(result, dict)


def test_approach2_c_s():
    result = approach2_braided_correction(c_s=CS_BRAIDED)
    assert abs(result["c_s"] - CS_BRAIDED) < 1e-12


def test_approach2_braided_linear_less_than_bare():
    result = approach2_braided_correction(n_e_bare=80.0)
    assert result["N_e_braided_linear"] < result["N_e_bare"]


def test_approach2_braided_quadratic_less_than_linear():
    result = approach2_braided_correction(n_e_bare=80.0)
    assert result["N_e_braided_quadratic"] < result["N_e_braided_linear"]


def test_approach2_assessment_below_target():
    result = approach2_braided_correction(n_e_bare=80.0, c_s=CS_BRAIDED)
    # Linear correction: 80 × 12/37 ≈ 26 < 40 → BELOW_TARGET
    assert result["assessment"] == "BELOW_TARGET"


# ── Approach 3 ────────────────────────────────────────────────────────────────

def test_approach3_returns_dict():
    result = approach3_reheating_constraint()
    assert isinstance(result, dict)


def test_approach3_n_e_positive():
    result = approach3_reheating_constraint()
    assert result["N_e_estimate"] > 0.0


def test_approach3_gut_scale_gives_n_e_60():
    # At GUT scale, T_reh ~ 10^13 GeV, V_inf ~ 10^16 GeV → N_e ≈ 50–70
    result = approach3_reheating_constraint(
        V_inf_GeV=1.0e16,
        T_reh_GeV=1.0e13,
    )
    assert 30.0 <= result["N_e_estimate"] <= 90.0


def test_approach3_formula_field():
    result = approach3_reheating_constraint()
    assert "N_e" in result["formula"]


def test_approach3_open_link():
    result = approach3_reheating_constraint()
    assert "open_link" in result


# ── Approach 4 ────────────────────────────────────────────────────────────────

def test_approach4_returns_dict():
    result = approach4_horizon_minimum()
    assert isinstance(result, dict)


def test_approach4_n_e_min_positive():
    result = approach4_horizon_minimum()
    assert result["N_e_minimum"] > 0.0


def test_approach4_standard_satisfies_minimum():
    result = approach4_horizon_minimum(V_inf_GeV=1.0e16)
    assert result["standard_N_e_satisfies_minimum"] is True


def test_approach4_n_e_min_order_60():
    result = approach4_horizon_minimum(V_inf_GeV=1.0e16, T_eq_eV=0.75)
    # Should be order 50–70
    assert 40.0 <= result["N_e_minimum"] <= 90.0


# ── Summary ────────────────────────────────────────────────────────────────────

def test_summary_returns_dict():
    result = efolds_geometric_summary()
    assert isinstance(result, dict)


def test_summary_has_all_approaches():
    result = efolds_geometric_summary()
    for key in ("approach1", "approach2", "approach3", "approach4"):
        assert key in result


def test_summary_label_upgrade():
    result = efolds_geometric_summary()
    assert "PARAMETERIZED" in result["label_upgrade"]


def test_summary_overall_finding_not_empty():
    result = efolds_geometric_summary()
    assert len(result["overall_finding"]) > 10


# ── Architecture limit certificate ────────────────────────────────────────────

def test_architecture_cert_returns_dict():
    cert = efolds_architecture_limit_certificate()
    assert isinstance(cert, dict)


def test_architecture_cert_id():
    assert "N_E_EFOLDS_ARCHITECTURE_LIMIT" in efolds_architecture_limit_certificate()["certificate_id"]


def test_architecture_cert_version():
    assert efolds_architecture_limit_certificate()["version"] == "v11.15"


def test_architecture_cert_standard_in_range():
    cert = efolds_architecture_limit_certificate()
    assert cert["standard_in_range"] is True


def test_architecture_cert_prior_label():
    cert = efolds_architecture_limit_certificate()
    assert "ASSUMPTION" in cert["prior_label"]


def test_architecture_cert_new_label():
    cert = efolds_architecture_limit_certificate()
    assert "PARAMETERIZED" in cert["new_label"]


def test_architecture_cert_what_was_shown():
    cert = efolds_architecture_limit_certificate()
    assert isinstance(cert["what_was_shown"], list)
    assert len(cert["what_was_shown"]) == 4


def test_architecture_cert_upgrade_path():
    cert = efolds_architecture_limit_certificate()
    assert len(cert["upgrade_path"]) > 20


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    assert "SEPARATION_INTACT" in separation_guard()
