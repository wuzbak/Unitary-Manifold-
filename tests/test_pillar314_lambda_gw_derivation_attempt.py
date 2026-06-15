# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 314 — λ_GW Architecture Limit Formal Certificate."""
import pytest
from src.core.pillar314_lambda_gw_derivation_attempt import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_W,
    K_CS,
    PI_KR,
    LAMBDA_GW_RS1_NATURAL_RANGE,
    LAMBDA_GW_BACKREACTION_CENTRAL,
    LAMBDA_GW_BACKREACTION_RANGE,
    attempt_a_rs1_bulk_brane_ratio,
    attempt_b_backreaction_formula,
    lambda_gw_naturalness_scan,
    lambda_gw_derivation_status,
    lambda_gw_architecture_limit_certificate,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 314


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_pi_kr():
    assert PI_KR == 37


# ── Constants ──────────────────────────────────────────────────────────────────

def test_natural_range_tuple():
    assert isinstance(LAMBDA_GW_RS1_NATURAL_RANGE, tuple)
    assert LAMBDA_GW_RS1_NATURAL_RANGE[0] < LAMBDA_GW_RS1_NATURAL_RANGE[1]


def test_backreaction_central_positive():
    assert LAMBDA_GW_BACKREACTION_CENTRAL > 0.0


def test_backreaction_range_ordered():
    lo, hi = LAMBDA_GW_BACKREACTION_RANGE
    assert lo < hi


# ── Attempt A — RS1 ───────────────────────────────────────────────────────────

def test_attempt_a_returns_dict():
    result = attempt_a_rs1_bulk_brane_ratio()
    assert isinstance(result, dict)


def test_attempt_a_id():
    assert attempt_a_rs1_bulk_brane_ratio()["attempt"] == "A__RS1_BULK_BRANE_TENSION_RATIO"


def test_attempt_a_natural_for_alpha1():
    result = attempt_a_rs1_bulk_brane_ratio(alpha_m=1.0)
    assert result["is_natural_order_unity"] is True


def test_attempt_a_natural_for_alpha05():
    result = attempt_a_rs1_bulk_brane_ratio(alpha_m=0.5)
    assert result["is_natural_order_unity"] is True


def test_attempt_a_lambda_gw_positive():
    result = attempt_a_rs1_bulk_brane_ratio(alpha_m=1.0)
    assert result["lambda_gw_estimate_units_k2_over_M53"] > 0.0


def test_attempt_a_status_constrained():
    result = attempt_a_rs1_bulk_brane_ratio(alpha_m=1.0)
    assert "CONSTRAINED" in result["status"]


def test_attempt_a_upgrade_path_present():
    result = attempt_a_rs1_bulk_brane_ratio()
    assert "upgrade_path" in result


# ── Attempt B — Backreaction ──────────────────────────────────────────────────

def test_attempt_b_returns_dict():
    result = attempt_b_backreaction_formula()
    assert isinstance(result, dict)


def test_attempt_b_id():
    assert attempt_b_backreaction_formula()["attempt"] == "B__BACKREACTION_FORMULA"


def test_attempt_b_lambda_gw_positive():
    result = attempt_b_backreaction_formula(alpha_m=1.0)
    assert result["lambda_gw"] > 0.0


def test_attempt_b_natural_for_alpha1():
    result = attempt_b_backreaction_formula(alpha_m=1.0)
    assert result["is_natural_order_unity"] is True


def test_attempt_b_range_ordered():
    result = attempt_b_backreaction_formula()
    lo, hi = result["lambda_gw_range"]
    assert lo < hi


def test_attempt_b_status_constrained():
    result = attempt_b_backreaction_formula()
    assert "CONSTRAINED" in result["status"]


def test_attempt_b_formula_involves_pi_kr():
    # lambda_gw should scale with pi_kr^2: for pi_kr=37, n_w=5, alpha_m=1
    result = attempt_b_backreaction_formula(alpha_m=1.0, pi_kr=37, n_w=5)
    expected = (1.0 / 5.0)**2 * 37.0**2 / 4.0  # = 37²/100 = 13.69
    assert abs(result["lambda_gw"] - expected) < 0.01


# ── Naturalness scan ───────────────────────────────────────────────────────────

def test_naturalness_scan_returns_list():
    result = lambda_gw_naturalness_scan()
    assert isinstance(result, list)


def test_naturalness_scan_length():
    result = lambda_gw_naturalness_scan((0.1, 0.5, 1.0))
    assert len(result) == 3


def test_naturalness_scan_alpha1_both_natural():
    result = lambda_gw_naturalness_scan((1.0,))
    assert result[0]["both_natural"] is True


def test_naturalness_scan_monotone():
    # lambda_gw_rs1 should increase with alpha_m
    result = lambda_gw_naturalness_scan((0.5, 1.0, 2.0))
    lams = [r["lambda_gw_rs1_est"] for r in result]
    assert lams[0] < lams[1] < lams[2]


# ── Derivation status ─────────────────────────────────────────────────────────

def test_derivation_status_returns_dict():
    status = lambda_gw_derivation_status()
    assert isinstance(status, dict)


def test_derivation_status_parameter():
    assert lambda_gw_derivation_status()["parameter"] == "lambda_GW"


def test_derivation_status_not_uniquely_derived():
    assert lambda_gw_derivation_status()["is_uniquely_derived"] is False


def test_derivation_status_architecture_limit_flag():
    assert lambda_gw_derivation_status()["architecture_limit_flag"] == "LAMBDA_GW_ARCHITECTURE_LIMIT"


def test_derivation_status_label():
    status = lambda_gw_derivation_status()
    assert status["status_label"] in ("CONSTRAINED", "UNCONSTRAINED")


# ── Architecture limit certificate ────────────────────────────────────────────

def test_architecture_cert_returns_dict():
    cert = lambda_gw_architecture_limit_certificate()
    assert isinstance(cert, dict)


def test_architecture_cert_id():
    assert "LAMBDA_GW_ARCHITECTURE_LIMIT" in lambda_gw_architecture_limit_certificate()["certificate_id"]


def test_architecture_cert_version():
    assert lambda_gw_architecture_limit_certificate()["version"] == "v11.15"


def test_architecture_cert_pillar():
    assert lambda_gw_architecture_limit_certificate()["pillar"] == 314


def test_architecture_cert_prior_label_postulated():
    cert = lambda_gw_architecture_limit_certificate()
    assert "POSTULATED" in cert["prior_label"]


def test_architecture_cert_new_label_constrained():
    cert = lambda_gw_architecture_limit_certificate()
    assert "CONSTRAINED" in cert["new_label"]


def test_architecture_cert_what_was_shown_list():
    cert = lambda_gw_architecture_limit_certificate()
    assert isinstance(cert["what_was_shown"], list)
    assert len(cert["what_was_shown"]) >= 2


def test_architecture_cert_upgrade_path_not_empty():
    cert = lambda_gw_architecture_limit_certificate()
    assert len(cert["upgrade_path"]) > 10


def test_architecture_cert_verdict_architecture_limit():
    cert = lambda_gw_architecture_limit_certificate()
    assert "ARCHITECTURE_LIMIT" in cert["certificate_verdict"]


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    result = separation_guard()
    assert "SEPARATION_INTACT" in result
    assert "adjacent-track" in result.lower()
