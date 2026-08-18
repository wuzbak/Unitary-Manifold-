# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 684 — Sp(2,ℝ) anomaly cancellation in 13D."""
import pytest
from fractions import Fraction
from src.core.pillar684_sp2r_anomaly_cancellation_13d import (
    N_W, K_CS, C2_SP2, DIM_13, N_F_KK,
    sp2r_group_theory,
    eta_invariant_kk,
    parity_anomaly_coefficient,
    gs_counterterm_coefficient,
    anomaly_cancellation_check,
    i14_factorization,
    sp2r_anomaly_cancellation_certificate,
)


# ── Constants ─────────────────────────────────────────────────────────────────

def test_n_w():
    assert N_W == 5

def test_k_cs():
    assert K_CS == 74

def test_c2_sp2():
    assert C2_SP2 == 5

def test_dim_13():
    assert DIM_13 == 13

def test_n_f_kk_equals_k_cs():
    assert N_F_KK == K_CS


# ── Group theory ──────────────────────────────────────────────────────────────

def test_group_theory_c2():
    result = sp2r_group_theory()
    assert result["c2_fundamental"] == 5

def test_group_theory_rank():
    result = sp2r_group_theory()
    assert result["rank"] == 2

def test_group_theory_group_name():
    result = sp2r_group_theory()
    assert "Sp(2" in result["group"]


# ── η-invariant ───────────────────────────────────────────────────────────────

def test_eta_sign():
    result = eta_invariant_kk()
    # n_w=5 is odd → (-1)^5 = -1 → η(0) < 0
    assert result["eta_invariant"] < 0

def test_eta_exact_fraction():
    result = eta_invariant_kk()
    # η(0) = -5/74
    eta = Fraction(result["eta_exact"])
    assert eta == Fraction(-5, 74)

def test_eta_source_pillar():
    result = eta_invariant_kk()
    assert "70-D" in result["source"]


# ── Parity anomaly coefficient ─────────────────────────────────────────────────

def test_parity_anomaly_value():
    result = parity_anomaly_coefficient()
    # A = (74/2) × 5 × (-5/74) = 37 × 5 × (-5/74) = -925/74 = -12.5
    assert abs(result["A_parity"] - (-12.5)) < 1e-10

def test_parity_anomaly_exact():
    result = parity_anomaly_coefficient()
    a = Fraction(result["A_parity_exact"])
    assert a == Fraction(-925, 74)

def test_parity_anomaly_not_integer():
    result = parity_anomaly_coefficient()
    assert result["is_integer"] is False

def test_parity_anomaly_n_f():
    result = parity_anomaly_coefficient()
    assert result["N_f"] == K_CS

def test_parity_anomaly_c2():
    result = parity_anomaly_coefficient()
    assert result["C2_Sp2"] == C2_SP2


# ── GS counterterm ────────────────────────────────────────────────────────────

def test_gs_coefficient_value():
    result = gs_counterterm_coefficient()
    assert abs(result["k_GS"] - 2.5) < 1e-10

def test_gs_coefficient_exact():
    result = gs_counterterm_coefficient()
    k = Fraction(result["k_GS_exact"])
    assert k == Fraction(5, 2)

def test_gs_coefficient_is_nw_over_2():
    result = gs_counterterm_coefficient()
    k = Fraction(result["k_GS_exact"])
    assert k == Fraction(N_W, 2)

def test_gs_mentions_nw5():
    result = gs_counterterm_coefficient()
    assert "n_w=5" in result["consistency_with_nw5"] or "n_w" in result["consistency_with_nw5"]


# ── Anomaly cancellation check ────────────────────────────────────────────────

def test_anomaly_cancelled():
    result = anomaly_cancellation_check()
    assert result["anomaly_cancelled"] is True

def test_anomaly_total_zero():
    result = anomaly_cancellation_check()
    assert abs(result["total_anomaly"]) < 1e-10

def test_anomaly_status():
    result = anomaly_cancellation_check()
    assert result["status"] == "CANCELLED"

def test_anomaly_exact_zero():
    result = anomaly_cancellation_check()
    assert Fraction(result["total_anomaly_exact"]) == Fraction(0)


# ── I_{15} factorization ──────────────────────────────────────────────────────

def test_i15_factorization_verified():
    result = i14_factorization()
    assert result["factorization_verified"] is True

def test_i15_form_degrees():
    result = i14_factorization()
    assert result["X4"]["form_degree"] == 4
    assert result["X11"]["form_degree"] == 11

def test_i15_gs_counterterm_present():
    result = i14_factorization()
    assert "ΔS_GS" in result["gs_counterterm"]["action"]


# ── Full certificate ──────────────────────────────────────────────────────────

def test_certificate_status():
    cert = sp2r_anomaly_cancellation_certificate()
    assert cert["status"] == "PROVED_AT_SCAFFOLD_LEVEL"

def test_certificate_pillar():
    cert = sp2r_anomaly_cancellation_certificate()
    assert cert["pillar"] == "684"

def test_certificate_all_proved():
    cert = sp2r_anomaly_cancellation_certificate()
    assert cert["all_proved"] is True

def test_certificate_toe_zero():
    cert = sp2r_anomaly_cancellation_certificate()
    assert cert["toe_impact"] == 0

def test_certificate_nw5_corroboration():
    cert = sp2r_anomaly_cancellation_certificate()
    assert "n_w=5" in cert["nw5_corroboration"]

def test_certificate_honest_residuals():
    cert = sp2r_anomaly_cancellation_certificate()
    assert len(cert["honest_residuals"]) >= 2
