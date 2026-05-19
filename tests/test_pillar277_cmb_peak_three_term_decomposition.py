# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 277 — CMB Peak Suppression Three-Term Decomposition."""
from __future__ import annotations

import math

import pytest

from src.core.pillar277_cmb_peak_three_term_decomposition import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    S_5D_CAP_FLOOR,
    S_ALPHAGW_RANGE,
    S_BRAID_CENTRAL,
    S_BRAID_RANGE,
    S_TOTAL_OBSERVED_RANGE,
    alpha_gw_transfer_factor,
    braided_winding_factor,
    fallibility_admission2_summary,
    five_d_eft_cap_factor,
    log_decomposition_consistency,
    peak_suppression_report,
    separation_guard,
    three_term_decomposition,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 277
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    g = separation_guard()
    assert g["decomposes_existing_residual_only"] is True


def test_observed_range_is_canonical():
    lo, hi = S_TOTAL_OBSERVED_RANGE
    assert lo == pytest.approx(4.2)
    assert hi == pytest.approx(6.1)


def test_braided_winding_factor_levels():
    assert braided_winding_factor("central") == S_BRAID_CENTRAL
    assert braided_winding_factor("low") == S_BRAID_RANGE[0]
    assert braided_winding_factor("high") == S_BRAID_RANGE[1]
    with pytest.raises(ValueError):
        braided_winding_factor("unknown")


def test_alpha_gw_transfer_factor_endpoints():
    s_low, s_high = S_ALPHAGW_RANGE
    assert alpha_gw_transfer_factor(alpha_gw=4.2e-10) == pytest.approx(s_low)
    assert alpha_gw_transfer_factor(alpha_gw=4.8e-10) == pytest.approx(s_high)
    mid = alpha_gw_transfer_factor(alpha_gw=4.5e-10)
    assert s_low < mid < s_high


def test_alpha_gw_transfer_validation():
    with pytest.raises(ValueError):
        alpha_gw_transfer_factor(alpha_gw=4.2e-10, alpha_gw_high=4.0e-10)
    with pytest.raises(ValueError):
        alpha_gw_transfer_factor(alpha_gw=5.0e-10)


def test_five_d_eft_cap_factor_basic():
    cap = five_d_eft_cap_factor(s_total=5.0, s_braid=1.55, s_alphagw=1.7)
    assert cap == pytest.approx(5.0 / (1.55 * 1.7))
    with pytest.raises(ValueError):
        five_d_eft_cap_factor(s_total=-1.0, s_braid=1.0, s_alphagw=1.0)
    with pytest.raises(ValueError):
        five_d_eft_cap_factor(s_total=5.0, s_braid=0.0, s_alphagw=1.0)


def test_three_term_decomposition_keys_and_log_sum():
    d = three_term_decomposition()
    for key in (
        "S_total", "S_braid", "S_alphaGW", "S_5D_cap",
        "log_S_total", "log_S_braid", "log_S_alphaGW", "log_S_5D_cap",
    ):
        assert key in d
    # Log identity to machine precision
    assert log_decomposition_consistency(d) < 1.0e-12


def test_three_term_decomposition_central_in_observed_window():
    d = three_term_decomposition()
    lo, hi = S_TOTAL_OBSERVED_RANGE
    assert lo <= d["S_total"] <= hi
    assert d["S_5D_cap"] >= S_5D_CAP_FLOOR - 1.0e-6


def test_peak_suppression_report_full():
    rep = peak_suppression_report()
    assert rep["acceptance_gate_passed"] is True
    assert len(rep["decomposition_rows"]) == 3
    # Each row's log identity holds to machine precision
    for row in rep["decomposition_rows"]:
        assert row["log_consistency_residual"] < 1.0e-12


def test_central_fractions_sum_to_one():
    rep = peak_suppression_report()
    f = rep["central_log_fractions"]
    total = f["braid_fraction"] + f["alphaGW_fraction"] + f["5D_cap_fraction"]
    assert total == pytest.approx(1.0)


def test_named_modules_listed():
    rep = peak_suppression_report()
    nm = rep["named_modules"]
    assert "S_braid" in nm and "S_alphaGW" in nm and "S_5D_cap" in nm
    assert "alpha_gw_10d_uv_completion" in nm["S_alphaGW"]


def test_fallibility_admission2_summary_has_percentages():
    s = fallibility_admission2_summary()
    assert "%" in s["headline"]
    assert "braided-winding" in s["headline"]
    assert "α_GW" in s["headline"] or "alpha_GW" in s["headline"] or "alphaGW" in s["headline"].lower()
    assert "5D" in s["headline"]
    assert s["log_consistency_residual_central"] < 1.0e-12


def test_decomposition_monotone_in_total():
    lo, hi = S_TOTAL_OBSERVED_RANGE
    d_lo = three_term_decomposition(s_total=lo)
    d_hi = three_term_decomposition(s_total=hi)
    # S_5D_cap increases with total suppression (others held fixed at central)
    assert d_hi["S_5D_cap"] > d_lo["S_5D_cap"]


def test_no_hardgate_drift():
    rep = peak_suppression_report()
    assert rep["separation_guard"]["is_hardgate"] is False
    assert rep["separation_guard"]["alters_falsifier_window"] is False
