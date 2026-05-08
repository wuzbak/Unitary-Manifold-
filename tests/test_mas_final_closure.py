# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for W14: src/core/mas_final_closure.py — MAS Final Closure Sprint."""

from __future__ import annotations

import pytest

from src.core.mas_final_closure import (
    MAS_COMPLETE,
    MAS_PROGRAMME_VERSION,
    P3_FINAL_STATUS,
    P5_FINAL_STATUS,
    P14_FINAL_STATUS,
    P19_FINAL_STATUS,
    P20_FINAL_STATUS,
    P21_FINAL_STATUS,
    all_parameter_statuses,
    mas_completion_summary,
    p3_closure_certificate,
    p5_closure_certificate,
    p14_closure_certificate,
    p19_p20_p21_closure_certificate,
)


# ──────────────────────────────────────────────────────────────────────────────
# Module-level constants
# ──────────────────────────────────────────────────────────────────────────────

def test_mas_complete_is_true():
    assert MAS_COMPLETE is True


def test_programme_version():
    assert MAS_PROGRAMME_VERSION == "v10.12"


def test_p3_final_status():
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in P3_FINAL_STATUS
    assert "10D" in P3_FINAL_STATUS


def test_p5_final_status():
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in P5_FINAL_STATUS
    assert "6D" in P5_FINAL_STATUS


def test_p14_final_status():
    assert "CONSTRAINED" in P14_FINAL_STATUS


def test_p19_p20_p21_final_status():
    for s in (P19_FINAL_STATUS, P20_FINAL_STATUS, P21_FINAL_STATUS):
        assert "GEOMETRIC_ESTIMATE_CERTIFIED" in s


# ──────────────────────────────────────────────────────────────────────────────
# P3 closure certificate
# ──────────────────────────────────────────────────────────────────────────────

def test_p3_certificate_parameter():
    cert = p3_closure_certificate()
    assert cert["parameter"] == "P3"


def test_p3_certificate_final_status():
    cert = p3_closure_certificate()
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in cert["final_status"]


def test_p3_certificate_direct_chain_err_positive():
    cert = p3_closure_certificate()
    assert cert["direct_chain_pct_err"] > 0.0


def test_p3_certificate_architecture_limit_dim():
    cert = p3_closure_certificate()
    assert cert["architecture_limit_dimension"] == "10D"


def test_p3_certificate_auxiliary_su5():
    cert = p3_closure_certificate()
    su5 = cert["auxiliary_su5_evidence"]
    assert su5["gate_met"] is True
    assert "auxiliary" in su5["policy"].lower()


def test_p3_certificate_hidden_anchor_guard():
    cert = p3_closure_certificate()
    assert cert["hidden_anchor_guard"] == "PASS"


def test_p3_certificate_has_terminal_verdict():
    cert = p3_closure_certificate()
    assert isinstance(cert["terminal_verdict"], str)
    assert len(cert["terminal_verdict"]) > 20


# ──────────────────────────────────────────────────────────────────────────────
# P5 closure certificate
# ──────────────────────────────────────────────────────────────────────────────

def test_p5_certificate_parameter():
    cert = p5_closure_certificate()
    assert cert["parameter"] == "P5"


def test_p5_certificate_final_status():
    cert = p5_closure_certificate()
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in cert["final_status"]


def test_p5_certificate_ghu_killed():
    cert = p5_closure_certificate()
    assert cert["ghu_killed"] is True


def test_p5_certificate_selected_path():
    cert = p5_closure_certificate()
    assert "Coleman" in cert["selected_path"] or "CW" in cert["selected_path"]


def test_p5_certificate_open_free_parameter():
    cert = p5_closure_certificate()
    assert "θ_HR" in cert["open_free_parameter"]


def test_p5_certificate_architecture_limit_dim():
    cert = p5_closure_certificate()
    assert "6D" in cert["architecture_limit_dimension"]


# ──────────────────────────────────────────────────────────────────────────────
# P14 closure certificate
# ──────────────────────────────────────────────────────────────────────────────

def test_p14_certificate_parameter():
    cert = p14_closure_certificate()
    assert cert["parameter"] == "P14"


def test_p14_certificate_final_status():
    cert = p14_closure_certificate()
    assert "CONSTRAINED" in cert["final_status"]


def test_p14_nominal_pct_err_positive():
    cert = p14_closure_certificate()
    assert cert["nominal_pct_err"] > 0.0


def test_p14_nominal_pct_err_small():
    cert = p14_closure_certificate()
    assert cert["nominal_pct_err"] < 5.0


def test_p14_robustness_gate_fail_recorded():
    cert = p14_closure_certificate()
    assert cert["robustness_gate_result"] == "FAIL"


def test_p14_axiomzero_purity_pass():
    cert = p14_closure_certificate()
    assert cert["axiomzero_purity_gate"] == "PASS"


def test_p14_has_terminal_verdict():
    cert = p14_closure_certificate()
    assert isinstance(cert["terminal_verdict"], str)
    assert len(cert["terminal_verdict"]) > 20


# ──────────────────────────────────────────────────────────────────────────────
# P19/P20/P21 closure certificate
# ──────────────────────────────────────────────────────────────────────────────

def test_nu_certificate_parameters():
    cert = p19_p20_p21_closure_certificate()
    assert set(cert["parameters"]) == {"P19", "P20", "P21"}


def test_nu_certificate_dm2_31_err_positive():
    cert = p19_p20_p21_closure_certificate()
    assert cert["dm2_31_pct_err"] > 0.0


def test_nu_certificate_dm2_21_calibrated():
    cert = p19_p20_p21_closure_certificate()
    assert cert["dm2_21_calibrated"] is True


def test_nu_certificate_sum_mnu_bound():
    cert = p19_p20_p21_closure_certificate()
    assert cert["sum_mnu_bound_met"] is True


def test_nu_certificate_final_statuses():
    cert = p19_p20_p21_closure_certificate()
    for p in ["P19", "P20", "P21"]:
        assert "GEOMETRIC_ESTIMATE_CERTIFIED" in cert["final_status"][p]


def test_nu_certificate_architecture_limit_dim():
    cert = p19_p20_p21_closure_certificate()
    assert "6D" in cert["architecture_limit_dimension"]


def test_nu_certificate_has_terminal_verdict():
    cert = p19_p20_p21_closure_certificate()
    assert isinstance(cert["terminal_verdict"], str)
    assert len(cert["terminal_verdict"]) > 20


# ──────────────────────────────────────────────────────────────────────────────
# all_parameter_statuses
# ──────────────────────────────────────────────────────────────────────────────

def test_all_statuses_keys():
    s = all_parameter_statuses()
    expected = {"P3", "P5", "P6", "P7", "P8", "P14", "P16", "P19", "P20", "P21", "P26", "P27"}
    assert expected == set(s.keys())


def test_all_statuses_no_empty():
    s = all_parameter_statuses()
    for k, v in s.items():
        assert isinstance(v, str) and len(v) > 0, f"{k} has empty status"


# ──────────────────────────────────────────────────────────────────────────────
# mas_completion_summary
# ──────────────────────────────────────────────────────────────────────────────

def test_summary_mas_complete():
    s = mas_completion_summary()
    assert s["mas_complete"] is True


def test_summary_version():
    s = mas_completion_summary()
    assert s["version"] == "v10.12"


def test_summary_total_parameters():
    s = mas_completion_summary()
    assert s["total_parameters_assessed"] == 12


def test_summary_architecture_limits_documented():
    s = mas_completion_summary()
    limits = s["architecture_limits_documented"]
    assert isinstance(limits, list)
    assert len(limits) >= 4


def test_summary_dbp_ladder_all_six_rungs():
    s = mas_completion_summary()
    rungs = s["dbp_ladder_all_rungs"]
    assert len(rungs) == 6
    for rung, status in rungs.items():
        assert isinstance(status, str) and len(status) > 0


def test_summary_certificates_present():
    s = mas_completion_summary()
    certs = s["certificates"]
    assert {"P3", "P5", "P14", "P19_P20_P21"} == set(certs.keys())


def test_summary_epistemic_honesty_check():
    s = mas_completion_summary()
    ehc = s["epistemic_honesty_check"]
    for key in ("no_status_inflation", "no_residual_rounding",
                "architecture_limits_documented", "falsifiers_preserved"):
        assert ehc[key] is True, f"epistemic check '{key}' must be True"


def test_summary_has_completion_statement():
    s = mas_completion_summary()
    stmt = s["completion_statement"]
    assert isinstance(stmt, str)
    assert len(stmt) > 50
    assert "complete" in stmt.lower()


def test_summary_actionable_next_steps():
    s = mas_completion_summary()
    steps = s["actionable_next_steps_for_future_waves"]
    assert isinstance(steps, list)
    assert len(steps) >= 2


def test_summary_date_closed():
    s = mas_completion_summary()
    assert s["date_closed"] == "2026-05-08"
